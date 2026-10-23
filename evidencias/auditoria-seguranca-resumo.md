# Bônus · Auditoria de segurança

**Skill:** [`skills/revisao-seguranca/SKILL.md`](../skills/revisao-seguranca/SKILL.md)  
**Crédito metodologia:** [Vibe Coding — o prompt que audita seu código](https://manodeyvin.com.br/p/vibe-coding-o-prompt-que-audita-seu)

## Artefatos

| Arquivo | Descrição |
|---|---|
| [`gerado/docs/security-audit/relatorio-auditoria-seguranca.md`](../gerado/docs/security-audit/relatorio-auditoria-seguranca.md) | Relatório completo + issues GitHub |
| [`gerado/docs/security-audit/relatorio-auditoria-seguranca.pdf`](../gerado/docs/security-audit/relatorio-auditoria-seguranca.pdf) | PDF (após `generate_pdf.py`) |
| [`gerado/docs/security-audit/generate_pdf.py`](../gerado/docs/security-audit/generate_pdf.py) | Script regenerável |

## Regenerar PDF

```bash
cd gerado/docs/security-audit
python3 -m venv .venv-audit
source .venv-audit/bin/activate
pip install -r requirements-audit.txt
python generate_pdf.py
```

## Nota

A entrega **obrigatória** foi congelada em [`entrega-base-confirmada.md`](entrega-base-confirmada.md). Esta auditoria **não altera** os testes CA-01..CA-10.
