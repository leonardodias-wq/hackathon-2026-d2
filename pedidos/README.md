# Pedidos

Cada arquivo `.md` aqui é um pedido em linguagem natural para a fábrica gerar um sistema em `gerado/`.

| Arquivo | Uso |
|---|---|
| `PEDIDO-TREINO.md` | Calibração oficial (reserva de salas, CA-01..CA-10) |
| `PEDIDO.md` | Pedido de teste / cenário alternativo (ex.: controle de horas) |

Rodar com um agente:

```bash
./scripts/usar-agente.sh claude PEDIDO-TREINO.md
./scripts/usar-agente.sh colar PEDIDO.md
```

O caminho usado no prompt é sempre `pedidos/<arquivo>`.
