(function () {
  const form = document.getElementById("form-reserva");
  const salaSelect = document.getElementById("sala_id");
  const feedback = document.getElementById("feedback");
  const agendaData = document.getElementById("agenda-data");
  const agendaBody = document.getElementById("agenda-body");
  const agendaTable = document.getElementById("agenda-table");
  const agendaEmpty = document.getElementById("agenda-empty");
  const btnAtualizar = document.getElementById("btn-atualizar");

  function showFeedback(kind, message) {
    feedback.textContent = message;
    feedback.className = "feedback show " + kind;
  }

  function clearFeedback() {
    feedback.textContent = "";
    feedback.className = "feedback";
  }

  function toLocalInputValue(d) {
    const pad = (n) => String(n).padStart(2, "0");
    return (
      d.getFullYear() +
      "-" +
      pad(d.getMonth() + 1) +
      "-" +
      pad(d.getDate()) +
      "T" +
      pad(d.getHours()) +
      ":" +
      pad(d.getMinutes())
    );
  }

  function toIsoLocal(localValue) {
    if (!localValue) return "";
    return localValue.length === 16 ? localValue + ":00" : localValue;
  }

  function formatHora(iso) {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    const pad = (n) => String(n).padStart(2, "0");
    return pad(d.getHours()) + ":" + pad(d.getMinutes());
  }

  function todayYmd() {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  }

  async function api(path, options) {
    const res = await fetch(path, options);
    let data = null;
    const text = await res.text();
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (_) {
        data = { detail: text };
      }
    }
    if (!res.ok) {
      const detail =
        (data && (data.detail || data.message)) || "Erro na requisição.";
      const msg = typeof detail === "string" ? detail : JSON.stringify(detail);
      const err = new Error(msg);
      err.status = res.status;
      throw err;
    }
    return data;
  }

  async function carregarSalas() {
    const salas = await api("/api/salas");
    while (salaSelect.firstChild) {
      salaSelect.removeChild(salaSelect.firstChild);
    }
    salas.forEach(function (sala) {
      const opt = document.createElement("option");
      opt.value = String(sala.id);
      opt.textContent =
        sala.nome + " · " + sala.local + " (" + sala.capacidade + " pax)";
      salaSelect.appendChild(opt);
    });
  }

  async function carregarAgenda() {
    const data = agendaData.value || todayYmd();
    agendaData.value = data;
    showFeedback("loading", "Carregando agenda…");
    try {
      const reservas = await api("/api/reservas?data=" + encodeURIComponent(data));
      while (agendaBody.firstChild) {
        agendaBody.removeChild(agendaBody.firstChild);
      }
      if (!reservas.length) {
        agendaTable.hidden = true;
        agendaEmpty.hidden = false;
        clearFeedback();
        return;
      }
      agendaEmpty.hidden = true;
      agendaTable.hidden = false;
      reservas.forEach(function (r) {
        const tr = document.createElement("tr");

        const tdSala = document.createElement("td");
        tdSala.textContent = r.sala_nome || "Sala #" + r.sala_id;
        tr.appendChild(tdSala);

        const tdHorario = document.createElement("td");
        tdHorario.textContent = formatHora(r.inicio) + "–" + formatHora(r.fim);
        tr.appendChild(tdHorario);

        const tdTitulo = document.createElement("td");
        tdTitulo.textContent = r.titulo;
        tr.appendChild(tdTitulo);

        const tdStatus = document.createElement("td");
        const chip = document.createElement("span");
        chip.className =
          "chip " + (r.status === "ATIVA" ? "ativa" : "cancelada");
        chip.textContent = r.status;
        tdStatus.appendChild(chip);
        tr.appendChild(tdStatus);

        agendaBody.appendChild(tr);
      });
      clearFeedback();
    } catch (err) {
      showFeedback("error", err.message || "Falha ao carregar agenda.");
    }
  }

  form.addEventListener("submit", async function (ev) {
    ev.preventDefault();
    showFeedback("loading", "Criando reserva…");
    const payload = {
      sala_id: Number(salaSelect.value),
      responsavel_nome: document.getElementById("responsavel_nome").value.trim(),
      responsavel_email: document.getElementById("responsavel_email").value.trim(),
      titulo: document.getElementById("titulo").value.trim(),
      participantes: Number(document.getElementById("participantes").value),
      inicio: toIsoLocal(document.getElementById("inicio").value),
      fim: toIsoLocal(document.getElementById("fim").value),
    };
    try {
      const reserva = await api("/api/reservas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      showFeedback(
        "success",
        "Reserva #" + reserva.id + " criada (" + reserva.status + ")."
      );
      form.reset();
      preencherHorariosPadrao();
      await carregarSalas();
      await carregarAgenda();
    } catch (err) {
      showFeedback("error", err.message || "Não foi possível reservar.");
    }
  });

  btnAtualizar.addEventListener("click", function () {
    carregarAgenda();
  });

  agendaData.addEventListener("change", function () {
    carregarAgenda();
  });

  function preencherHorariosPadrao() {
    const start = new Date();
    start.setMinutes(0, 0, 0);
    start.setHours(start.getHours() + 1);
    const end = new Date(start.getTime() + 60 * 60 * 1000);
    document.getElementById("inicio").value = toLocalInputValue(start);
    document.getElementById("fim").value = toLocalInputValue(end);
  }

  async function boot() {
    agendaData.value = todayYmd();
    preencherHorariosPadrao();
    try {
      await carregarSalas();
      await carregarAgenda();
    } catch (err) {
      showFeedback("error", err.message || "Falha ao iniciar.");
    }
  }

  boot();
})();
