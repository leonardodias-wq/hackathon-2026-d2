#!/usr/bin/env bash
# Gera prompts/PROMPT-COMPLETO.md — um único bloco para colar em qualquer chat.
# Uso: ./scripts/montar-prompt.sh [nome-do-pedido]
# Ex.: ./scripts/montar-prompt.sh PEDIDO-TREINO.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/prompts/PROMPT-COMPLETO.md"
PEDIDO_ARG="${1:-PEDIDO-TREINO.md}"

resolve_pedido() {
  if [[ -f "$ROOT/$PEDIDO_ARG" ]]; then
    PEDIDO_FILE="$ROOT/$PEDIDO_ARG"
  elif [[ -f "$ROOT/pedidos/$PEDIDO_ARG" ]]; then
    PEDIDO_FILE="$ROOT/pedidos/$PEDIDO_ARG"
  else
    echo "Pedido não encontrado: $PEDIDO_ARG (procure em pedidos/)" >&2
    exit 1
  fi
  PEDIDO_REL="${PEDIDO_FILE#"$ROOT"/}"
}

resolve_pedido

{
  echo "# Prompt completo · Fábrica Ideen (gerado automaticamente)"
  echo ""
  echo "_Não edite manualmente; regenere com: \`./scripts/montar-prompt.sh ${PEDIDO_ARG}\`_"
  echo ""
  cat "$ROOT/prompts/INSTRUCOES-UNIVERSAIS.md"
  echo ""
  echo "---"
  echo ""
  echo "## Pedido anexado (\`${PEDIDO_REL}\`)"
  echo ""
  cat "$PEDIDO_FILE"
  echo ""
  echo "---"
  echo ""
  echo "## Mensagem final do usuário"
  echo ""
  cat <<EOF
Siga integralmente prompts/INSTRUCOES-UNIVERSAIS.md deste repositório.

Usando as skills disponíveis, construa o sistema descrito em ${PEDIDO_REL} dentro da pasta gerado/. Siga todas as etapas das skills até o sistema rodar e os critérios de aceite serem verificados.

Não pare entre etapas. Registre em evidencias/erros-ia.md qualquer erro seu antes de corrigir.
EOF
} > "$OUT"

echo "Gerado: $OUT (pedido: ${PEDIDO_REL})"
