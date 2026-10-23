---
name: interface-agradavel
description: >-
  Guia de UI/UX para sistemas gerados: layout agradável, acessível e sem
  estética genérica de IA (antislop). Use na etapa de construção ao criar HTML,
  CSS, componentes ou telas em gerado/static/ ou frontend do projeto.
---

# Interface agradável (antislop)

Aplicar **durante a construção** da UI, antes de considerar a tela pronta. Complementa `fabrique-sistema` etapa 03; não substitui requisitos funcionais nem testes.

## Objetivo

Entregar interface **clara, bonita e específica do domínio** — não “landing de startup genérica” nem dashboard roxo com gradiente.

## Antislop — não fazer

- Gradiente roxo/azul neon em fundo branco “de template IA”.
- Fonte padrão do sistema em tudo, sem hierarquia tipográfica.
- Cards idênticos com ícones emoji como único diferencial visual.
- Copy vazio: “Bem-vindo à nossa plataforma inovadora”, “Soluções disruptivas”.
- Excesso de bordas arredondadas, sombras pesadas e `backdrop-blur` sem motivo.
- Layout que ignora o fluxo real do usuário (form gigante + tabela minúscula).
- `innerHTML` com dados da API (usar `textContent` / DOM seguro).

## Fazer — checklist mínimo

1. **Contexto:** 1 frase no topo explicando o que o sistema faz (ex.: reserva de salas sem conflito).
2. **Tipografia:** uma fonte de título + uma de corpo (ex.: Google Fonts: `DM Sans` + `Source Sans 3`, ou `Fraunces` + `IBM Plex Sans`). Tamanhos com escala clara (título, subtítulo, corpo, legenda).
3. **Cor:** paleta enxuta (3–5 tokens): fundo, superfície, texto, primária, erro/sucesso. Primária alinhada ao domínio (escritório/corporativo → azul petróleo, verde musgo ou laranja queimado — **não** o roxo clichê).
4. **Espaço:** padding consistente (ex.: 8px grid), formulário em coluna legível, largura máx ~960px.
5. **Estados:** loading, erro de API, sucesso de reserva, lista vazia na agenda — todos visíveis e em pt-BR.
6. **Acessibilidade:** contraste WCAG AA em texto; labels em inputs; foco visível em botões; `lang="pt-BR"`.
7. **Mobile:** layout usável em ~375px (stack, botões tocáveis).

## Fluxo por tipo de tela

| Tipo | Prioridade visual |
|---|---|
| Formulário principal | Campos agrupados, CTA óbvio, validação inline |
| Listagem / agenda | Tabela ou cards escaneáveis; status com cor + texto, não só cor |
| Dashboard / relatório | Números grandes só se o pedido pedir; senão tabela simples |

## Entrega no repo

- CSS em `gerado/static/` (um arquivo `styles.css` ou equivalente; evitar 200 linhas inline no HTML).
- Opcional: `gerado/docs/UI-NOTAS.md` (5 linhas: paleta, fontes, decisão de layout).

## Revisão rápida antes de merge

- [ ] Parece feito para **este** produto, não para qualquer SaaS?
- [ ] Alguém consegue reservar / ver agenda sem ler manual?
- [ ] Nenhum texto placeholder em inglês sem motivo?
- [ ] Segurança: sem `innerHTML` em dados dinâmicos.

## Exemplo de direção (reserva de salas)

- Tom: ferramenta interna confiável, não marketing.
- Agenda do dia: colunas Sala | Horário | Título | Status; status `ATIVA` / `CANCELADA` com chips discretos.
- Formulário: “Nova reserva” com data/hora nativos ou inputs claros; feedback após submit.
