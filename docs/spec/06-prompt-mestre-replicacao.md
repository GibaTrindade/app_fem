# Prompt Mestre de Replicacao

Use este prompt quando quiser que outro projeto siga exatamente o design deste app.

```text
Use o app FEM como referencia visual oficial.

Arquivos de referencia obrigatorios:
- templates/base.html
- templates/partials/_styles.html
- templates/partials/_ui_kit_theme.html
- templates/partials/_navbar.html
- templates/ptms/ptm_list.html
- templates/ptms/dashboard.html
- templates/ptms/ptm_detail.html
- docs/spec/05-design-spec.md

Objetivo:
Replicar EXATAMENTE esse design no projeto atual.
Nao quero apenas algo "parecido", "inspirado" ou "na mesma linha".

Prioridade maxima:
A pagina `ptm_detail.html` e a referencia principal.
Quero copiar especialmente o padrao de:
- cabecalho rico da entidade
- resumo recolhivel
- tabs em `nav-pills`
- card de conteudo abaixo das tabs
- tabelas e modais dentro desse contexto

Fluxo obrigatorio:
1. Leia os arquivos de referencia.
2. Resuma em 10 a 15 bullets os elementos que definem visualmente esse design.
3. Extraia os tokens, componentes e regras de composicao.
4. Implemente o projeto atual preservando esse design sem reinterpretacao.
5. Ao final, liste o que ficou 100% fiel e o que ficou aproximado.

Regras visuais obrigatorias:
- Manter fundo geral claro `#f5f7fb`.
- Manter navbar azul escura `#0c3c60`.
- Manter container principal com largura maxima de `1280px`.
- Manter uso dominante de `card shadow-sm`.
- Manter cabecalhos de cards com `p-4 border-bottom bg-light-subtle`.
- Manter labels discretas com `small text-muted`.
- Manter tabelas Bootstrap com `table-striped` e `table-hover`.
- Manter tabs com `nav-pills`, inativas em azul escuro e ativa preenchida em azul escuro.
- Manter a hierarquia de botoes primario, secundario e destrutivo.
- Manter a logica de uma tela de detalhe unica com tabs, em vez de quebrar em varias paginas.

Regras de implementacao:
- Nao invente nova paleta.
- Nao troque a navbar por sidebar se a meta for copiar este design.
- Nao transforme tabs em dropdown ou acordeao sem necessidade tecnica real.
- Nao substitua cards por secoes soltas.
- Nao adicione efeitos chamativos, gradientes, glassmorphism ou animacoes decorativas.
- Nao simplifique a pagina de detalhe a ponto de perder o padrao premium do app.

Se houver conflito tecnico entre o projeto atual e a referencia:
- preserve ao maximo a aparencia final
- explique exatamente onde a copia 1:1 nao foi possivel
- proponha a alternativa mais fiel visualmente
```

## Variacao Curta

```text
Copie EXATAMENTE o design do app FEM no projeto atual, usando como referencia principal a `ptm_detail.html` e a spec em `docs/spec/05-design-spec.md`. Nao quero reinterpretacao visual. Preserve navbar azul escura, fundo claro, cards com shadow-sm, cabecalhos em bg-light-subtle, tabs em nav-pills e o padrao de detalhe com resumo recolhivel + tabs + card de conteudo.
```
