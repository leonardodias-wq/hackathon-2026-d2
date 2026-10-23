---
name: revisao-seguranca
description: >-
  Auditoria de segurança em 5 categorias (tenant, permissões no cliente, IDOR,
  segredos, XSS/input). Detecta a stack, adapta o checklist, reporta achados
  verificados com arquivo:linha e gera relatório em gerado/docs/security-audit/.
  Use após construir o sistema em gerado/, no bônus do hackathon, ou quando o
  usuário pedir revisão de segurança ou auditoria.
disable-model-invocation: true
---

# Revisão de segurança (5 categorias)

Metodologia inspirada em [Vibe Coding — o prompt que audita seu código](https://manodeyvin.com.br/p/vibe-coding-o-prompt-que-audita-seu) (Mano de Yvin). Adaptar sempre à stack detectada.

## Antes de auditar

1. Detectar stack: linguagem, framework, ORM, auth, frontend, deploy (Docker/CI/etc.).
2. Definir escopo: por padrão auditar **`gerado/`** (sistema produzido). Não alterar testes de aceite (CA-xx) salvo pedido explícito.
3. Registrar premissas (ex.: “sem login por requisito do PRD”).

## Categorias (adaptar à stack)

### 1. Banco sem tranca (tenant/dono)

- Supabase: RLS ausente.
- API própria: listagens/buscas/relatórios sem filtro por usuário/organização.
- Identificar mecanismo esperado (RLS, middleware tenant, `user_id`) e onde falta.

### 2. Permissão no navegador

- UI esconde por `isAdmin` / `role` sem checagem equivalente no servidor.
- Cruzar cada gate do frontend com o endpoint.

### 3. IDOR

- GET/PATCH/DELETE por ID sem verificar posse do chamador.
- Percorrer **todos** os handlers, não amostra.

### 4. Chaves expostas

- Secrets em código, compose, CI, Helm, docs, defaults `${VAR:-public}`.
- Bundle frontend; histórico git se relevante.

### 5. Inputs sem tratamento (XSS)

- Frontend: `innerHTML`, `dangerouslySetInnerHTML`, `v-html`, markdown sem sanitizar, `javascript:` em URLs.
- Backend: input em HTML/e-mail/template sem escape.

## Regras da auditoria

- Só achados **verificados** no código. Por achado: arquivo, linha(s), trecho, exploitabilidade, severidade (crítica/alta/média/baixa/informativa).
- Listar arquivo por arquivo, linha por linha.
- Registrar o que está **correto** (pontos fortes com evidência).
- Categoria N/A → declarar N/A, não inventar achado.
- Notar feature flags / config necessária para exploit.

## Saídas (ordem)

1. **Markdown fonte:** `gerado/docs/security-audit/relatorio-auditoria-seguranca.md`
2. **Resumo no repo:** `evidencias/auditoria-seguranca-resumo.md` (link para o relatório)
3. **PDF:** rodar `gerado/docs/security-audit/generate_pdf.py` → `relatorio-auditoria-seguranca.pdf`
4. **Chat:** lista resumida dos achados para o usuário.

## Estrutura do relatório Markdown

- Capa (título, data, escopo, metodologia/stack)
- Resumo executivo (contagem por severidade; referência aos gráficos do PDF)
- Pontos fortes / pontos fracos
- Tabela por categoria
- Recomendações P1, P2, P3…
- Seção **ISSUES PARA O GITHUB** (blocos `--- ISSUE n ---` … `--- FIM ISSUE n ---`)

## PDF (bônus visual)

- Script: `gerado/docs/security-audit/generate_pdf.py`
- Venv local: `python3 -m venv .venv-audit && pip install -r requirements-audit.txt`
- Paleta: crítica `#B91C1C`, alta `#EA580C`, média `#D97706`, baixa `#2563EB`, ponto forte `#059669`
- A4, margens ~2 cm, cabeçalho/rodapé com número de página.

## Integração com a fábrica

- **Opcional** após etapa 04 de `fabrique-sistema`.
- Não bloqueia entrega se o PDF falhar; o Markdown verificado conta como evidência do bônus.
