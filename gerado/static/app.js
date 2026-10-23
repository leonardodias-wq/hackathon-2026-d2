(function () {
  const projetosById = new Map();

  function el(tag, props, children) {
    const node = document.createElement(tag);
    if (props) {
      Object.entries(props).forEach(([k, v]) => {
        if (k === "className") node.className = v;
        else if (k === "text") node.textContent = v;
        else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2).toLowerCase(), v);
        else if (v !== undefined && v !== null) node.setAttribute(k, v);
      });
    }
    (children || []).forEach((c) => {
      if (c == null) return;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function setStatus(id, message, kind) {
    const box = document.getElementById(id);
    box.textContent = message || "";
    box.className = "status-bar" + (kind ? " " + kind : "");
  }

  async function api(path, options) {
    const res = await fetch(path, options);
    const ct = res.headers.get("content-type") || "";
    let body = null;
    if (ct.includes("application/json")) {
      body = await res.json();
    } else if (ct.includes("text/csv")) {
      body = await res.text();
    } else if (res.status !== 204) {
      body = await res.text();
    }
    if (!res.ok) {
      const detail = body && body.detail ? body.detail : body || res.statusText;
      const err = new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
      err.status = res.status;
      throw err;
    }
    return body;
  }

  function fillProjetoSelects(projetos) {
    ["crono-projeto", "manual-projeto"].forEach((id) => {
      const select = document.getElementById(id);
      select.textContent = "";
      projetos.forEach((p) => {
        select.appendChild(
          el("option", { value: String(p.id), text: p.nome + " · " + p.cliente })
        );
      });
    });
  }

  function syncIdentity(from) {
    const nome =
      document.getElementById("crono-nome").value ||
      document.getElementById("manual-nome").value;
    const email =
      document.getElementById("crono-email").value ||
      document.getElementById("manual-email").value ||
      document.getElementById("lista-email").value;
    if (from !== "crono" && nome) document.getElementById("crono-nome").value = nome;
    if (from !== "manual" && nome) document.getElementById("manual-nome").value = nome;
    if (email) {
      document.getElementById("crono-email").value = email;
      document.getElementById("manual-email").value = email;
      document.getElementById("lista-email").value = email;
    }
  }

  function localIso(dtLocal) {
    // datetime-local → ISO sem Z
    if (!dtLocal) return "";
    return dtLocal.length === 16 ? dtLocal + ":00" : dtLocal;
  }

  function formatWhen(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function renderLista(items) {
    const container = document.getElementById("lista-container");
    container.textContent = "";
    if (!items.length) {
      container.appendChild(el("p", { className: "empty", text: "Nenhum lançamento hoje para este e-mail." }));
      return;
    }
    const table = el("table", { "aria-label": "Lançamentos do dia" });
    const thead = el("thead");
    thead.appendChild(
      el("tr", null, [
        el("th", { text: "Projeto" }),
        el("th", { text: "Descrição" }),
        el("th", { text: "Início" }),
        el("th", { text: "Fim" }),
        el("th", { text: "Min" }),
        el("th", { text: "Status" }),
        el("th", { text: "" }),
      ])
    );
    table.appendChild(thead);
    const tbody = el("tbody");
    items.forEach((item) => {
      const proj = projetosById.get(item.projeto_id);
      const nomeProj = proj ? proj.nome : "#" + item.projeto_id;
      const cor = proj ? proj.cor : "#888";
      const tr = el("tr");
      const projCell = el("td");
      projCell.appendChild(el("span", { className: "projeto-dot", style: "background:" + cor }));
      projCell.appendChild(document.createTextNode(nomeProj));
      tr.appendChild(projCell);
      tr.appendChild(el("td", { text: item.descricao }));
      tr.appendChild(el("td", { text: formatWhen(item.inicio) }));
      tr.appendChild(el("td", { text: formatWhen(item.fim) }));
      tr.appendChild(
        el("td", {
          text: item.duracao_minutos != null ? String(item.duracao_minutos) : "—",
        })
      );
      tr.appendChild(
        el("td", null, [el("span", { className: "chip " + item.status, text: item.status })])
      );
      const actions = el("td");
      if (item.status === "EM_ANDAMENTO") {
        actions.appendChild(
          el("button", {
            type: "button",
            className: "secondary",
            text: "Excluir",
            onClick: async () => {
              try {
                await api("/api/lancamentos/" + item.id, { method: "DELETE" });
                setStatus("lista-status", "Lançamento excluído.", "ok");
                await loadLista();
              } catch (e) {
                setStatus("lista-status", e.message, "error");
              }
            },
          })
        );
      }
      tr.appendChild(actions);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    container.appendChild(table);
  }

  function todayBounds() {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, "0");
    const d = String(now.getDate()).padStart(2, "0");
    return { data_inicio: y + "-" + m + "-" + d, data_fim: y + "-" + m + "-" + d };
  }

  function monthBounds() {
    const now = new Date();
    const y = now.getFullYear();
    const m = now.getMonth();
    const start = y + "-" + String(m + 1).padStart(2, "0") + "-01";
    const last = new Date(y, m + 1, 0).getDate();
    const end = y + "-" + String(m + 1).padStart(2, "0") + "-" + String(last).padStart(2, "0");
    return { data_inicio: start, data_fim: end };
  }

  async function loadProjetos() {
    const projetos = await api("/api/projetos");
    projetosById.clear();
    projetos.forEach((p) => projetosById.set(p.id, p));
    fillProjetoSelects(projetos);
  }

  async function loadLista() {
    const email = document.getElementById("lista-email").value.trim();
    if (!email) {
      setStatus("lista-status", "Informe o e-mail para listar o dia.", "error");
      return;
    }
    const { data_inicio, data_fim } = todayBounds();
    setStatus("lista-status", "Carregando…");
    try {
      const q =
        "/api/lancamentos?email=" +
        encodeURIComponent(email) +
        "&data_inicio=" +
        data_inicio +
        "&data_fim=" +
        data_fim;
      const items = await api(q);
      renderLista(items);
      setStatus("lista-status", items.length + " lançamento(s).", "ok");
    } catch (e) {
      setStatus("lista-status", e.message, "error");
    }
  }

  document.getElementById("form-cronometro").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    syncIdentity("crono");
    const payload = {
      projeto_id: Number(document.getElementById("crono-projeto").value),
      colaborador_nome: document.getElementById("crono-nome").value.trim(),
      colaborador_email: document.getElementById("crono-email").value.trim(),
      descricao: document.getElementById("crono-desc").value.trim(),
    };
    setStatus("crono-status", "Iniciando…");
    try {
      const created = await api("/api/cronometro/iniciar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setStatus("crono-status", "Cronômetro #" + created.id + " em andamento.", "ok");
      await loadLista();
    } catch (e) {
      setStatus("crono-status", e.message, "error");
    }
  });

  document.getElementById("btn-parar").addEventListener("click", async () => {
    syncIdentity("crono");
    const email = document.getElementById("crono-email").value.trim();
    if (!email) {
      setStatus("crono-status", "Informe o e-mail para parar.", "error");
      return;
    }
    setStatus("crono-status", "Parando…");
    try {
      const done = await api("/api/cronometro/parar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      setStatus(
        "crono-status",
        "Finalizado #" + done.id + " · " + done.duracao_minutos + " min.",
        "ok"
      );
      await loadLista();
    } catch (e) {
      setStatus("crono-status", e.message, "error");
    }
  });

  document.getElementById("form-manual").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    syncIdentity("manual");
    const payload = {
      projeto_id: Number(document.getElementById("manual-projeto").value),
      colaborador_nome: document.getElementById("manual-nome").value.trim(),
      colaborador_email: document.getElementById("manual-email").value.trim(),
      descricao: document.getElementById("manual-desc").value.trim(),
      inicio: localIso(document.getElementById("manual-inicio").value),
      fim: localIso(document.getElementById("manual-fim").value),
    };
    setStatus("manual-status", "Salvando…");
    try {
      const created = await api("/api/lancamentos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setStatus(
        "manual-status",
        "Salvo #" + created.id + " · " + created.duracao_minutos + " min.",
        "ok"
      );
      await loadLista();
    } catch (e) {
      setStatus("manual-status", e.message, "error");
    }
  });

  document.getElementById("btn-atualizar").addEventListener("click", () => {
    syncIdentity("lista");
    loadLista();
  });

  document.getElementById("btn-csv").addEventListener("click", async () => {
    const { data_inicio, data_fim } = monthBounds();
    setStatus("lista-status", "Gerando CSV…");
    try {
      const text = await api(
        "/api/relatorio/csv?data_inicio=" + data_inicio + "&data_fim=" + data_fim
      );
      const blob = new Blob([text], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = el("a", {
        href: url,
        download: "horas_" + data_inicio + "_" + data_fim + ".csv",
      });
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setStatus("lista-status", "CSV do mês baixado.", "ok");
    } catch (e) {
      setStatus("lista-status", e.message, "error");
    }
  });

  loadProjetos()
    .then(() => {
      const saved = localStorage.getItem("ponto_fiel_email");
      if (saved) {
        document.getElementById("lista-email").value = saved;
        document.getElementById("crono-email").value = saved;
        document.getElementById("manual-email").value = saved;
      }
    })
    .catch((e) => setStatus("lista-status", e.message, "error"));

  ["crono-email", "manual-email", "lista-email"].forEach((id) => {
    document.getElementById(id).addEventListener("change", (ev) => {
      localStorage.setItem("ponto_fiel_email", ev.target.value.trim());
    });
  });
})();
