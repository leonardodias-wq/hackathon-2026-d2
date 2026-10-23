#!/usr/bin/env bash
# Guia rápido: passos + blocos para copiar/colar por agente de IA.
# Uso: ./scripts/usar-agente.sh <agente> <pedido.md>
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MSG_TMP=""

usage() {
  cat <<'EOF'
Uso: ./scripts/usar-agente.sh <agente> <pedido>

  pedido   Nome do arquivo em pedidos/ (ex.: PEDIDO-TREINO.md, PEDIDO.md)

Agentes: cursor | chatgpt | claude | gemini | copilot | colar

Exemplos:
  ./scripts/usar-agente.sh claude PEDIDO-TREINO.md
  ./scripts/usar-agente.sh colar PEDIDO.md
EOF
}

cleanup() {
  [[ -n "$MSG_TMP" && -f "$MSG_TMP" ]] && rm -f "$MSG_TMP"
}
trap cleanup EXIT

list_help() {
  echo "Uso: ./scripts/usar-agente.sh <agente> <pedido>"
  echo ""
  echo "Agentes: cursor, chatgpt, claude, gemini, copilot, colar"
  echo ""
  echo "Pedidos em pedidos/:"
  shopt -s nullglob
  local f
  for f in "$ROOT/pedidos"/*.md; do
    [[ "$(basename "$f")" == "README.md" ]] && continue
    echo "  - $(basename "$f")"
  done
  shopt -u nullglob
  echo ""
  echo "Exemplo: ./scripts/usar-agente.sh claude PEDIDO-TREINO.md"
  echo "Detalhes: skills/PORTABILIDADE.md"
}

copy_block() {
  local title="$1"
  local file="$2"
  echo ""
  echo "──────── COPIAR: ${title} ────────"
  cat "$file"
  echo "──────── fim ────────"
  echo ""
}

resolve_pedido() {
  local name="$1"
  if [[ -z "$name" ]]; then
    echo "Informe o pedido (arquivo em pedidos/)." >&2
    usage >&2
    exit 1
  fi
  if [[ "$name" == */* ]]; then
    PEDIDO_FILE="$ROOT/$name"
    PEDIDO_REL="$name"
  elif [[ -f "$ROOT/pedidos/$name" ]]; then
    PEDIDO_FILE="$ROOT/pedidos/$name"
    PEDIDO_REL="pedidos/$name"
  else
    echo "Pedido não encontrado: $name (veja pedidos/)" >&2
    exit 1
  fi
}

write_mensagem() {
  MSG_TMP="$(mktemp)"
  cat > "$MSG_TMP" <<EOF
Siga integralmente prompts/INSTRUCOES-UNIVERSAIS.md deste repositório.

Usando as skills disponíveis, construa o sistema descrito em ${PEDIDO_REL} dentro da pasta gerado/. Siga todas as etapas das skills até o sistema rodar e os critérios de aceite serem verificados.

Não pare entre etapas. Registre em evidencias/erros-ia.md qualquer erro seu antes de corrigir.
EOF
}

header() {
  local agente="$1"
  echo "════════════════════════════════════════════════════════"
  echo "  Fábrica Ideen · ${agente} · ${PEDIDO_REL}"
  echo "════════════════════════════════════════════════════════"
  echo ""
}

agent_cursor() {
  header "Cursor"
  cat <<EOF
1. Clone o repo e abra a pasta no Cursor.
2. A skill já está em .cursor/skills/fabrique-sistema/.
3. Cole o prompt abaixo (ou /fabrique-sistema + o mesmo texto).
4. Valide: cd gerado && ./run-tests.sh

EOF
  copy_block "prompt no chat" "$MSG_TMP"
}

agent_chatgpt() {
  header "ChatGPT"
  cat <<EOF
1. Project com os arquivos do repositório anexados.
2. Cole INSTRUÇÕES nas "Instructions" do Project.
3. Chat novo com terminal; envie a PRIMEIRA MENSAGEM abaixo.

EOF
  copy_block "instruções do Project" "$ROOT/prompts/INSTRUCOES-UNIVERSAIS.md"
  copy_block "primeira mensagem" "$MSG_TMP"
}

agent_claude() {
  header "Claude"
  cat <<EOF
1. Project ou Claude Code na pasta do repo.
2. Inclua no contexto: prompts/INSTRUCOES-UNIVERSAIS.md, skills/fabrique-sistema/SKILL.md, ${PEDIDO_REL}.
3. Cole a PRIMEIRA MENSAGEM abaixo.

EOF
  copy_block "primeira mensagem" "$MSG_TMP"
}

agent_gemini() {
  header "Gemini"
  cat <<EOF
1. Gem ou chat com upload: INSTRUCOES-UNIVERSAIS.md, fabrique-sistema SKILL, ${PEDIDO_REL}.
2. Cole a PRIMEIRA MENSAGEM abaixo.

EOF
  copy_block "primeira mensagem" "$MSG_TMP"
}

agent_copilot() {
  header "GitHub Copilot (VS Code)"
  cat <<EOF
1. Abra o repo no VS Code; @workspace + INSTRUCOES-UNIVERSAIS.md.
2. Envie a PRIMEIRA MENSAGEM abaixo.

EOF
  copy_block "primeira mensagem" "$MSG_TMP"
}

agent_colar() {
  header "Colar tudo"
  cat <<EOF
1. Agente com terminal (Cursor Agent, Claude Code, etc.).
2. Cole o PROMPT COMPLETO abaixo.

EOF
  "$ROOT/scripts/montar-prompt.sh" "$(basename "$PEDIDO_FILE")" >/dev/null
  copy_block "prompt completo" "$ROOT/prompts/PROMPT-COMPLETO.md"
}

# --- main ---
AGENT=""
PEDIDO_NAME=""

for arg in "$@"; do
  case "$arg" in
    --help|-h) usage; exit 0 ;;
    *)
      if [[ -z "$AGENT" ]]; then
        AGENT="$arg"
      elif [[ -z "$PEDIDO_NAME" ]]; then
        PEDIDO_NAME="$arg"
      else
        echo "Argumento extra: $arg" >&2
        usage >&2
        exit 1
      fi
      ;;
  esac
done

if [[ -z "$AGENT" ]]; then
  list_help
  exit 0
fi

resolve_pedido "$PEDIDO_NAME"
write_mensagem

case "$AGENT" in
  cursor) agent_cursor ;;
  chatgpt|gpt) agent_chatgpt ;;
  claude) agent_claude ;;
  gemini) agent_gemini ;;
  copilot|github_copilot) agent_copilot ;;
  colar|generico|paste) agent_colar ;;
  *)
    echo "Agente desconhecido: $AGENT" >&2
    list_help >&2
    exit 1
    ;;
esac
