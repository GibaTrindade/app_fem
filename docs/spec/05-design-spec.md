# Design Spec

## Objetivo

Esta especificacao define o design visual e estrutural do app FEM para que ele possa ser reproduzido com alta fidelidade em outros projetos. O objetivo nao e apenas copiar "o clima" da interface, mas preservar exatamente os elementos que formam sua identidade: navegacao superior escura, fundo claro, cards com sombra leve, cabecalhos contextuais, filtros em blocos, tabelas administrativas e, principalmente, a pagina de detalhe com navegacao por tabs.

Arquivos-base desta spec:

- `templates/base.html`
- `templates/partials/_styles.html`
- `templates/partials/_navbar.html`
- `templates/ptms/ptm_list.html`
- `templates/ptms/dashboard.html`
- `templates/ptms/ptm_detail.html`

## Principios do Design

- Interface administrativa limpa, sobria e funcional.
- Visual institucional, sem exibicionismo grafico.
- A densidade de informacao e alta, mas sempre organizada em blocos claros.
- A navegacao deve parecer estavel e previsivel.
- O layout deve transmitir "controle operacional", nao "site marketing".
- A pagina de detalhe e o centro da experiencia e deve ser tratada como padrao premium do sistema.

## Identidade Visual

### Paleta

- Fundo geral da aplicacao: `#f5f7fb`
- Cor principal institucional: `#0c3c60`
- Texto de apoio e metadados: usar tons Bootstrap `text-muted`
- Cards neutros informativos: `bg-light` ou `bg-light-subtle`
- Botoes e estados seguem a semantica Bootstrap:
- Primario para acao principal
- Secondary/outline-secondary para acoes neutras
- Danger para exclusao
- Light e outline-light sobre a navbar

### Sensacao visual

- Limpa
- Leve
- Profissional
- Operacional
- Discreta

Nao deve parecer:

- App de startup chamativo
- Dashboard futurista
- Landing page
- Interface escura
- UI com gradientes, glassmorphism ou efeitos decorativos

## Layout Global

### Estrutura base

- Navbar fixa no topo visual da pagina, ocupando toda a largura.
- Conteudo principal centralizado dentro de um container com largura maxima de `1280px`.
- Area principal com respiro vertical de `py-4`.
- O fundo do body deve permanecer claro e uniforme.

### Regra de largura

- O conteudo nao deve ficar solto em largura total.
- O limite de leitura e operacao e dado pela classe `.app-main`.
- Mesmo quando a navbar usa `container-fluid`, o conteudo interno respeita o mesmo eixo do restante da interface.

### Espacamento

- Blocos principais separados por `mb-3`.
- Cabecalhos internos usam `p-4`.
- Conteudo interno de cards usa `p-3` ou `p-4`.
- Grids internas usam `g-3`.
- A interface evita espacos exagerados; o ritmo e compacto, mas respirado.

## Tipografia e Hierarquia

### Cabecalhos

- Titulo principal de pagina: `h1.h4`
- Titulos secundarios de secao: `h2.h6`
- Numeros de KPI: `h3` ou `h5`, dependendo da densidade do bloco

### Textos auxiliares

- Subtitulos explicativos ficam logo abaixo do titulo principal.
- Sempre usar texto curto, direto e operacional.
- Metadados e labels devem usar `small text-muted`.

### Microcopy

- Linguagem objetiva e administrativa.
- Verbos claros: `Aplicar`, `Limpar`, `Voltar`, `Editar`, `Excluir`, `Salvar`.
- Evitar frases longas, promocionais ou excessivamente informais.

## Componentes Fundamentais

### 1. Navbar

Referencia principal: `templates/partials/_navbar.html`

Caracteristicas obrigatorias:

- Fundo solido em `#0c3c60`
- Marca em branco com peso semibold
- Itens de navegacao como botoes pequenos `btn btn-sm`
- Acoes primarias de sessao no canto direito
- Nome do usuario em texto discreto `text-white-50 small`

A navbar deve comunicar aplicacao interna autenticada, nao site publico.

### 2. Card base

Padrao mais recorrente da interface.

Caracteristicas:

- Estrutura principal com `card shadow-sm`
- Separacao externa com `mb-3`
- Conteudo interno dividido por `card-body`
- Quando ha cabecalho rico, usar `card-body p-0` com faixa superior separada

Uso:

- Listagens
- Dashboards
- Blocos de tabs
- Formularios
- Areas de resumo
- Secoes de detalhe

### 3. Cabecalho de card com destaque suave

Padrao visto em `ptm_list.html` e `ptm_detail.html`.

Estrutura:

- Container superior com `p-4 border-bottom bg-light-subtle`
- Titulo, badges e subtitulo do lado esquerdo
- Acoes principais do lado direito
- Comportamento responsivo com `flex-wrap` e `gap-3`

Este padrao e obrigatorio para paginas principais e detalhes.

### 4. Badges

Uso semantico, nao decorativo.

Padroes:

- `text-bg-light border` para identificadores neutros
- `text-bg-secondary` para status contextual de apoio
- `text-bg-primary`, `text-bg-warning`, `text-bg-danger` para contagens e alertas

Regras:

- Badges aparecem em grupos pequenos
- Nunca empilhar muitas cores fortes juntas
- O badge deve complementar o titulo, nao competir com ele

### 5. Botoes

Hierarquia obrigatoria:

- Acao principal da tela: `btn btn-primary`
- Acao secundaria: `btn btn-outline-secondary`
- Acao destrutiva: `btn btn-danger` ou `btn btn-outline-danger`
- Em tabelas, usar `btn btn-sm`

Regras:

- Normalmente ha uma unica acao primaria por bloco
- Em grupos de acoes, a primaria vem por ultimo ou como maior destaque contextual
- Nao criar muitos estilos customizados; manter a disciplina Bootstrap com a paleta existente

### 6. Formularios de filtro

Referencia principal: `templates/ptms/ptm_list.html`

Estrutura:

- Formulario dentro de card
- Labels pequenas e discretas
- Inputs em grade `row g-3`
- Grupo final com botao primario `Aplicar` e secundario `Limpar`

Comportamento:

- O formulario deve parecer uma ferramenta de trabalho, nao um wizard
- Os filtros ficam visiveis na pagina, sem drawer lateral

### 7. Tabelas administrativas

Padrao recorrente nas tabs da `ptm_detail.html` e na listagem principal.

Caracteristicas:

- Sempre dentro de `.table-responsive`
- Uso de `.table`, `.table-striped`, `.table-hover`
- Header com `.table-light`
- Coluna de acoes alinhada a direita
- Botoes pequenos para editar e excluir

Estados vazios:

- Mostrar mensagem direta dentro da tabela, sem ilustracoes
- Exemplo de tom: `Sem eventos.`, `Sem pagamentos.`, `Nenhum PTM encontrado.`

### 8. Modais CRUD

Referencia principal: `templates/ptms/ptm_detail.html`

Padrao:

- Modal Bootstrap simples
- Titulo claro no header
- Corpo com campos padrao
- Footer com `Cancelar` em outline-secondary e `Salvar` ou `Excluir` como acao principal

Regras:

- Modais servem para operacoes pontuais
- Nao substituir paginas inteiras por excesso de modais
- O visual do modal deve herdar a sobriedade do resto do sistema

## Paginas-Padrao

### Dashboard

Referencia principal: `templates/ptms/dashboard.html`

Composicao:

- Bloco inicial com titulo, subtitulo e CTA secundaria
- KPIs em grade compacta
- Cards de alertas com listas internas
- Cards de distribuicao com badges de contagem

Tom:

- Resumo executivo-operacional
- Foco em leitura rapida
- Nenhum grafico e necessario para preservar a identidade visual

### Listagem

Referencia principal: `templates/ptms/ptm_list.html`

Composicao:

- Cabecalho rico em card
- Badge de contexto e contador de registros
- Filtros logo abaixo no mesmo bloco
- Tabela principal em card separado
- Paginacao discreta no rodape do card

Tom:

- Pagina de trabalho diario
- Leitura escaneavel
- Alta clareza em buscas e consulta

### Detalhe com tabs

Referencia principal: `templates/ptms/ptm_detail.html`

Esta e a pagina mais importante da spec e o principal padrao a ser copiado em outros projetos.

#### Estrutura obrigatoria

1. Card de cabecalho da entidade
2. Area de resumo expandivel/recolhivel
3. Card opcional de acao secundaria contextual
4. Barra de tabs em card proprio
5. Card de conteudo da tab ativa

#### Cabecalho da entidade

Elementos obrigatorios:

- Grupo de badges identificadores no topo
- Titulo principal da entidade
- Linha de metadados logo abaixo
- Grupo de acoes no canto direito

As acoes devem incluir:

- Voltar
- Acao secundaria contextual
- Acao primaria de edicao
- Acao destrutiva quando aplicavel

#### Resumo recolhivel

O resumo recolhivel e parte central da linguagem visual.

Regras:

- Fica logo abaixo do cabecalho da entidade, dentro do mesmo card
- Abre com botao `Mostrar Resumo`
- Conteudo interno organizado em grades
- Mistura blocos pequenos de status, blocos financeiros e bloco lateral de metadados
- Informacoes textuais longas aparecem em cards simples na parte inferior do resumo

Esse padrao deve ser reutilizado em qualquer tela de detalhe rica em contexto.

#### Tabs

Este e o componente mais importante para replicacao em outros sistemas.

Estrutura:

- Tabs ficam em um card separado do conteudo
- Navegacao com `ul.nav.nav-pills.gap-2`
- Cor padrao da tab inativa: texto em `#0c3c60`
- Tab ativa com fundo `#0c3c60`
- Labels curtos e funcionais
- A troca de tab recarrega a mesma pagina com foco em secao contextual

Regras visuais:

- As tabs devem parecer instrumentos de navegacao de modulo, nao filtro cosmetico
- Manter espacamento horizontal entre pills
- Evitar tabs comprimidas sem respiro
- Em telas menores, permitir quebra de linha

Regras de uso:

- Cada tab representa um dominio de informacao da mesma entidade
- O usuario nao sai do contexto principal ao trocar de tab
- O card abaixo muda de conteudo, mas preserva a moldura visual do detalhe

#### Conteudo da tab

Padrao:

- Sempre dentro de um `card shadow-sm`
- `card-body` abriga a acao principal da secao e a tabela ou bloco informativo
- Se houver criacao de item, o botao vem acima da tabela
- Acoes de linha ficam na coluna final alinhada a direita

Este arranjo deve ser mantido mesmo quando o conteudo nao for tabela. O importante e preservar o modelo: `tabs acima`, `conteudo encapsulado abaixo`.

## Sistema de Composicao

### Formula da tela

Quase toda tela relevante do sistema segue esta formula:

- 1 bloco de contexto
- 1 bloco de acao
- 1 bloco de dados

Ou, no detalhe:

- 1 bloco de identidade da entidade
- 1 bloco de navegacao contextual
- 1 bloco de conteudo operacional

### Densidade correta

- Nao espalhar demais os elementos
- Nao comprimir a ponto de parecer legado hostil
- O sistema trabalha com densidade media: bastante informacao, mas em recipientes bem definidos

### Ritmo visual

- Alternancia entre blocos suaves (`bg-light`, `bg-light-subtle`) e superficies brancas
- Uso constante de borda, sombra leve e espacamento regular
- Repeticao deliberada dos mesmos padroes para transmitir consistencia

## Responsividade

### Regras obrigatorias

- Cabecalhos com `flex-wrap`
- Grids de KPI e resumo quebram por colunas menores em mobile
- Tabs podem quebrar em multiplas linhas
- Tabelas devem permanecer dentro de `table-responsive`
- Grupos de botoes devem aceitar quebra de linha sem colidir

### O que nao fazer no mobile

- Transformar tabs em dropdown sem necessidade
- Remover informacoes essenciais do cabecalho
- Eliminar badges de contexto
- Achatar todos os cards em uma lista sem hierarquia

## O Que Preservar Exatamente

- Fundo geral claro `#f5f7fb`
- Navbar institucional azul escura `#0c3c60`
- Conteudo central com largura maxima de `1280px`
- Uso dominante de `card shadow-sm`
- Cabecalhos de cards com `p-4 border-bottom bg-light-subtle`
- Labels pequenas e texto de apoio em `text-muted`
- Tabelas Bootstrap com `striped` e `hover`
- Tabs em `nav-pills` com inativo azul escuro e ativo azul escuro preenchido
- Hierarquia de botoes entre primario, secundario e destrutivo
- Pagina de detalhe com resumo recolhivel acima das tabs

## O Que Nao Fazer

- Nao trocar a navbar por sidebar como padrao principal se a intencao for copiar este design
- Nao substituir cards por secoes soltas sem contorno
- Nao usar paleta nova
- Nao adicionar gradients, vidro, blur ou animacoes chamativas
- Nao transformar a tela de detalhe em varias paginas separadas se o equivalente aqui e uma pagina unica com tabs
- Nao converter as tabs em acordeoes se a referencia a ser copiada e esta pagina
- Nao exagerar na personalizacao visual fora do padrao Bootstrap existente

## Prompt Recomendado Para Reaplicar Este Design

```text
Use o app FEM como referencia visual oficial, especialmente os arquivos:
- templates/base.html
- templates/partials/_styles.html
- templates/partials/_navbar.html
- templates/ptms/ptm_list.html
- templates/ptms/dashboard.html
- templates/ptms/ptm_detail.html

Quero replicar EXATAMENTE este design no projeto atual.
Nao quero apenas um estilo parecido ou inspirado.

Antes de implementar:
1. Extraia os design tokens, componentes e regras de composicao.
2. Resuma em bullets o que define visualmente esse app.
3. Trate a pagina ptm_detail.html como referencia principal do padrao de detalhe com tabs.

Durante a implementacao:
- Preserve a navbar azul escura, o fundo claro, os cards com shadow-sm, os cabecalhos em bg-light-subtle, a hierarquia de botoes e o padrao de tabelas.
- Replique a estrutura de detalhe com: cabecalho da entidade, resumo recolhivel, barra de tabs em nav-pills e card de conteudo da tab ativa.
- Nao invente nova paleta, nova navegacao ou nova linguagem visual.

Ao final:
- Liste o que ficou 100% fiel ao design original.
- Liste qualquer ponto que tenha ficado aproximado por limitacao tecnica do projeto atual.
```

## Checklist de Fidelidade

- A primeira impressao do app parece o mesmo produto visual?
- A navbar passa a mesma sensacao institucional?
- Os cards tem o mesmo peso visual?
- O detalhe da entidade usa cabecalho rico, resumo recolhivel e tabs?
- As tabs parecem modulo de trabalho, e nao enfeite?
- Tabelas e modais seguem o mesmo padrao?
- O projeto preserva sobriedade, densidade media e clareza operacional?

Se a resposta para qualquer item acima for "nao", a implementacao nao esta fiel o suficiente.
