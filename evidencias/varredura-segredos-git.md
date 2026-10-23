# Varredura de segredos no Git — 2026-10-23

## Escopo

- Working tree + arquivos rastreados (`git ls-files`)
- Histórico completo (`git rev-list --all` + `git grep`)
- Padrões: `ghp_`, `github_pat_`, `AKIA…`, `sk-…`, `xox*`, chaves PEM, `password=` em código

## Resultado

| Verificação | Status |
|---|---|
| Tokens GitHub / AWS / Slack no conteúdo versionado | **Nenhum encontrado** |
| Chaves privadas PEM no repositório | **Nenhuma** |
| Arquivos `.env` / `.pem` / `id_rsa` commitados | **Nenhum** |
| `.gitignore` cobre `.env`, `.env.*`, `*.db` | **OK** |
| `hackathon-2026-d2-kit.zip` / PDF da apresentação | **Não rastreados** (ignorados ou fora do git) |

## Observações (não são segredos de API)

- **E-mail do autor Git** (`leonardo.dias@petzpartner.com.br`) aparece nos metadados dos commits — dado de identidade do `git commit`, não token. Para ocultar no futuro, usar e-mail GitHub `noreply` ou `git config` local antes de novos commits.
- Textos em skills/README que **mencionam** “token/senha” são regras de processo, não valores reais.

## Comandos executados (reproduzir)

```bash
cd hackathon
git grep -iE '(ghp_|github_pat_|AKIA[0-9A-Z]{16}|BEGIN (RSA |OPENSSH )?PRIVATE)' $(git rev-list --all)
git ls-files
```

## Revalidação de segurança (código)

Ver seção adicionada em `gerado/docs/security-audit/relatorio-auditoria-seguranca.md` (Revalidação 2026-10-23).
