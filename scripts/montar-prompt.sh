#!/usr/bin/env bash
# Gera prompts/PROMPT-COMPLETO.md — um único bloco para colar em qualquer chat.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/prompts/PROMPT-COMPLETO.md"
PEDIDO="${1:-}"

{
  echo "# Prompt completo · Fábrica Ideen (gerado automaticamente)"
  echo ""
  echo "_Não edite manualmente; regenere com: \`./scripts/montar-prompt.sh [PEDIDO.md]\`_"
  echo ""
  cat "$ROOT/prompts/INSTRUCOES-UNIVERSAIS.md"
  echo ""
  echo "---"
  echo ""
  echo "## Pedido anexado"
  echo ""
  if [[ -n "$PEDIDO" && -f "$PEDIDO" ]]; then
    cat "$PEDIDO"
  elif [[ -f "$ROOT/PEDIDO.md" ]]; then
    cat "$ROOT/PEDIDO.md"
  elif [[ -f "$ROOT/PEDIDO-TREINO.md" ]]; then
    cat "$ROOT/PEDIDO-TREINO.md"
  else
    echo "_Nenhum PEDIDO encontrado; cole o pedido do cliente abaixo._"
  fi
  echo ""
  echo "---"
  echo ""
  echo "## Mensagem final do usuário"
  echo ""
  cat "$ROOT/prompts/mensagem-usuario-iniciar.txt"
} > "$OUT"

echo "Gerado: $OUT"
