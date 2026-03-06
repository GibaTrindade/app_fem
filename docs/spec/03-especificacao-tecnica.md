# Especificação Técnica Inicial (Django + SQLite)

## Stack
- Python 3.12+
- Django 6.x
- SQLite (MVP)

## Projeto
- Projeto Django: `fem_control`
- Apps sugeridos:
  - `core` (catálogos e utilitários)
  - `ptms` (entidade principal)
  - `eventos`
  - `pagamentos`
  - `vistorias`
  - `prestacao_contas`
  - `observacoes`
  - `conclusao_informal`

## Modelo de dados (alto nível)
- `PTM`
  - ordem (única), regiao, municipio, projeto, projeto_detalhado, tipo_fem,
    data_final, teto_fem, investimento_total, recurso_fem, rendimentos_fem,
    contrapartida, status_ptm_atual, status_obra_atual, data_aprovacao,
    ressalva, secretaria, area_investimento, conta_ptm, descricao.
- `EventoPTM` (N:1 PTM)
  - data_evento, descricao, status_ptm, status_obra, ordem_cronologica.
- `PagamentoPTM` (N:1 PTM)
  - parcela, dt_solicitacao, dt_envio_pg, valor_previsto, valor_realizado,
    dt_pagamento, numero_ob, numero_empenho, observacao, tipo_registro.
- `VistoriaPTM` (N:1 PTM)
  - dt_solicitacao, dt_resposta, percentual_execucao, observacao.
- `PrestacaoContaPTM` (N:1 PTM)
  - prazo_contas, data_prestacao, situacao.
- `PrestacaoContaHistorico` (N:1 PrestacaoContaPTM)
  - data, observacao.
- `ObservacaoEncaminhamentoPTM` (N:1 PTM)
  - data, observacao, origem.
- `ConclusaoInformalPTM` (N:1 PTM)
  - percentual_declarado, data, contato, observacao.
- Catálogos (`StatusPTM`, `StatusObra`, `TipoFEM`, `AreaInvestimento`, `Secretaria`).

## Regras de negócio iniciais
- `PTM.ordem` único.
- Status atual do PTM recalculado automaticamente ao inserir/editar/excluir evento.
- Valores monetários em `Decimal(14,2)`.
- Percentuais em `Decimal(5,4)` com exibição formatada em `%`.

## Migração da planilha
1. Importador lê `INF GERAIS` e cria PTMs.
2. Importador lê abas filhas e cria registros relacionados por `ORDEM`.
3. Importador grava inconsistências em log para revisão manual.

## Qualidade
- Testes de modelo e regra de atualização de status.
- Testes de importação com amostra de linhas reais.
