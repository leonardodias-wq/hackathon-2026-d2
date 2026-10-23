# Relatório de Auditoria de Segurança — Reserva de Salas (gerado/)

**Data:** 2026-10-23  
**Escopo:** `gerado/` (FastAPI, SQLite/pysqlite3, HTML/JS estático, sem auth)  
**Metodologia:** 5 categorias (Mano de Yvin / skill `revisao-seguranca`), adaptadas à stack.

## Resumo executivo

| Severidade | Quantidade |
|---|---|
| Crítica | 0 |
| Alta | 0 |
| Média | 1 |
| Baixa | 1 |
| Informativa | 2 |

**Riscos centrais:** API totalmente aberta (esperado pelo PRD); possível XSS refletido/armazenado na agenda via campos de reserva renderizados com `innerHTML`.

## Mapeamento stack → categorias

| Categoria | Aplicabilidade |
|---|---|
| 1 Tenant | **N/A** — sem multi-tenant nem login |
| 2 Permissão no browser | **N/A** — sem papéis |
| 3 IDOR | **Parcial** — IDs expostos sem “dono”; risco baixo sem auth |
| 4 Segredos | **Aplicável** |
| 5 XSS/input | **Aplicável** (UI) |

## Pontos fortes

| Evidência | Detalhe |
|---|---|
| `gerado/app/main.py` (queries) | SQL parametrizado (`?` placeholders) em INSERT/SELECT/UPDATE — mitiga SQL injection |
| `gerado/app/main.py` | Validação Pydantic em `SalaCreate` / `ReservaCreate` (tipos, `gt=0`) |
| `gerado/requirements.txt` | Sem segredos; `.gitignore` na raiz cobre `.env` |
| `gerado/app/business.py` | Regras de negócio centralizadas (`validate_reservation`, `overlaps`) |

## Achados detalhados

### 5 · Inputs / XSS

| Sev. | Arquivo:linha | Descrição |
|---|---|---|
| **Média** | `gerado/static/index.html:63` | `msg.textContent = ... + data.status` — OK para mensagem; porém linhas 72–74 usam `innerHTML` com `r.titulo`, `r.inicio`, `r.status` vindos da API. Título controlado pelo usuário (ex. `<img onerror=...>`) pode executar script no browser do operador. |

**Trecho (72–74):**

```javascript
document.getElementById('agenda-body').innerHTML = reservas.map(r =>
  `<tr><td>${byId[r.sala_id] || r.sala_id}</td><td>${r.titulo}</td>...
```

**Exploitabilidade:** criar reserva com título HTML/JS malicioso; abrir agenda do dia.

### 3 · IDOR (parcial)

| Sev. | Arquivo:linha | Descrição |
|---|---|---|
| **Baixa** | `gerado/app/main.py:144-163` | `POST /api/reservas/{reserva_id}/cancelar` cancela qualquer reserva futura conhecendo o ID, sem autenticação. Alinhado ao PRD (“sem login”), mas qualquer cliente na rede pode cancelar reservas alheias. |

### Informativos (contexto PRD)

| Sev. | Arquivo:linha | Descrição |
|---|---|---|
| Informativa | `gerado/app/main.py` (todos endpoints) | API sem autenticação/autorização — aceitável para hackathon; inaceitável em produção. |
| Informativa | `gerado/app/main.py:64-76` | `POST /api/salas` permite criar salas arbitrárias sem restrição. |

### Categorias N/A

- **1 Banco sem tranca:** sem conceito de inquilino/usuário autenticado.
- **2 Permissão no navegador:** sem UI por papel.

## Recomendações

| Prioridade | Ação |
|---|---|
| P1 | Substituir `innerHTML` na agenda por `textContent` / `createElement` ou sanitizar (DOMPurify) |
| P2 | Documentar que cancelamento por ID é público; em produção exigir auth + checagem de posse |
| P3 | Rate limiting / CORS restrito se exposto além de localhost |

## ISSUES PARA O GITHUB

--- ISSUE 1 ---
**Título:** [Segurança] XSS na agenda ao renderizar título de reserva com innerHTML

**Labels:** security, medium

**Descrição:** A agenda do dia em `static/index.html` monta linhas da tabela com `innerHTML` e interpola `r.titulo` (e outros campos) sem escape.

**Evidência:** `gerado/static/index.html` linhas 72–74.

**Impacto:** Execução de script no contexto da página ao visualizar reservas maliciosas.

**Sugestão:** Usar DOM API com `textContent` ou biblioteca de sanitização.

**Critérios de aceite:**
- [ ] Título com `<script>alert(1)</script>` exibido como texto, sem execução
- [ ] Teste manual ou automatizado (Playwright) na agenda

--- FIM ISSUE 1 ---

--- ISSUE 2 ---
**Título:** [Segurança] Cancelamento de reserva por ID sem autenticação

**Labels:** security, low

**Descrição:** Endpoint de cancelamento aceita qualquer `reserva_id` válido.

**Evidência:** `gerado/app/main.py:144-163`.

**Impacto:** Negação de serviço leve (cancelar reservas de terceiros) em rede aberta.

**Sugestão:** Fora do escopo do PRD atual; para produção, adicionar auth e validar posse.

**Critérios de aceite:**
- [ ] Documentado como limitação conhecida no README de `gerado/`
- [ ] (Produção) 401 sem token; 403 se não for o responsável

--- FIM ISSUE 2 ---
