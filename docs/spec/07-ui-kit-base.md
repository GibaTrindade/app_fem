# UI Kit Base

## Objetivo

Este UI kit base transforma o design do app em uma fundacao reutilizavel. Ele nao substitui a spec detalhada; ele operacionaliza a spec em tokens e classes-base para acelerar replicacoes futuras.

Arquivos relacionados:

- `templates/partials/_styles.html`
- `templates/partials/_ui_kit_theme.html`
- `docs/spec/05-design-spec.md`
- `docs/spec/06-prompt-mestre-replicacao.md`

## Estrategia

- A spec continua sendo a fonte de verdade conceitual.
- O prompt mestre continua sendo a instrucao operacional para novos projetos.
- O UI kit base oferece nomes reutilizaveis para nao depender apenas de memoria ou inferencia.
- A implementacao e aditiva: o visual atual continua funcionando como antes.

## Tokens

Definidos em `templates/partials/_ui_kit_theme.html`.

- `--fem-bg`
- `--fem-surface`
- `--fem-surface-soft`
- `--fem-surface-soft-2`
- `--fem-border`
- `--fem-text`
- `--fem-text-muted`
- `--fem-primary`
- `--fem-primary-rgb`
- `--fem-shadow-sm`
- `--fem-radius`
- `--fem-content-max`
- `--fem-gap`
- `--fem-gap-lg`

## Classes-base

### Shell e layout

- `.fem-shell-card`
- `.app-main`
- `.fem-toolbar`
- `.fem-actions`

### Cabecalhos e texto

- `.fem-section-header`
- `.fem-eyebrow`
- `.fem-meta-label`
- `.fem-page-title`
- `.fem-page-subtitle`

### Blocos de informacao

- `.fem-kpi-card`
- `.fem-kpi-label`
- `.fem-kpi-value`
- `.fem-detail-summary-card`
- `.fem-detail-summary-card.is-soft`

### Navegacao por tabs

- `.fem-tab-bar`

### Tabelas e modais

- `.fem-table-wrap`
- `.fem-modal-note`

## Como usar em outros projetos

### Passo 1

Copiar os tokens e classes-base do partial `_ui_kit_theme.html`.

### Passo 2

Recriar a estrutura visual nesta ordem:

1. Navbar institucional
2. Container principal centralizado
3. Cards como superficie dominante
4. Cabecalhos contextuais
5. Tela de detalhe com resumo recolhivel
6. Barra de tabs
7. Card de conteudo da tab ativa

### Passo 3

Aplicar o prompt mestre junto com a spec detalhada para evitar reinterpretacao.

## Exemplo de composicao de detalhe

```html
<div class="card shadow-sm mb-3 fem-shell-card">
  <div class="card-body p-0">
    <div class="fem-section-header">
      <div class="d-flex justify-content-between align-items-start flex-wrap gap-3">
        <div>
          <div class="d-flex align-items-center gap-2 flex-wrap mb-2">
            <span class="badge text-bg-light border">Entidade 123</span>
            <span class="badge text-bg-secondary">Contexto</span>
          </div>
          <h1 class="h4 mb-1">Titulo principal</h1>
          <p class="text-muted mb-0">Metadados resumidos da entidade.</p>
        </div>
        <div class="fem-actions">
          <button class="btn btn-outline-secondary">Mostrar Resumo</button>
          <a class="btn btn-outline-secondary" href="#">Voltar</a>
          <a class="btn btn-primary" href="#">Editar</a>
        </div>
      </div>
    </div>
    <div class="collapse show">
      <div class="p-4">
        <div class="row g-3">
          <div class="col-12 col-md-6 col-xl-3">
            <div class="fem-detail-summary-card">
              <div class="fem-meta-label mb-1">Status</div>
              <div class="fw-semibold">Ativo</div>
            </div>
          </div>
          <div class="col-12 col-md-6 col-xl-3">
            <div class="fem-detail-summary-card is-soft">
              <div class="fem-meta-label mb-1">Valor</div>
              <div class="fw-semibold">R$ 0,00</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="card shadow-sm mb-3 fem-shell-card fem-tab-bar">
  <div class="card-body">
    <ul class="nav nav-pills gap-2">
      <li class="nav-item"><a class="nav-link active" href="#">Tab 1</a></li>
      <li class="nav-item"><a class="nav-link" href="#">Tab 2</a></li>
      <li class="nav-item"><a class="nav-link" href="#">Tab 3</a></li>
    </ul>
  </div>
</div>

<div class="card shadow-sm fem-shell-card">
  <div class="card-body">
    <div class="mb-3">
      <button class="btn btn-primary">Novo Item</button>
    </div>
    <div class="table-responsive fem-table-wrap">
      <table class="table table-striped table-hover">
        <thead class="table-light">
          <tr>
            <th>Coluna</th>
            <th class="text-end">Acoes</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Conteudo</td>
            <td class="text-end">
              <button class="btn btn-sm btn-outline-primary">Editar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
```

## Garantia de nao perda

Criar este UI kit base nao remove nada do que ja existe.

- A spec detalhada continua intacta.
- O CSS atual continua funcionando.
- O novo partial apenas encapsula tokens e nomes reutilizaveis.
- A adocao pode ser gradual, tela a tela, sem migracao forcada.

Se um projeto futuro usar apenas este UI kit sem ler a spec, a fidelidade melhora, mas ainda fica menor do que usar UI kit + spec + prompt mestre juntos.
