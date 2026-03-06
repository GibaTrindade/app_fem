# Backlog de Implementação (MVP)

## Fase 1 - Fundação
1. Criar apps Django e registrar em `INSTALLED_APPS`.
2. Implementar modelos de catálogo e PTM.
3. Criar admin com filtros básicos.
4. Criar migrações iniciais.

## Fase 2 - Histórico Operacional
1. Implementar modelos de eventos, pagamentos, vistorias, prestação, observações e conclusão.
2. Implementar regra de atualização de status atual por último evento.
3. Criar telas CRUD iniciais (Django templates).

## Fase 3 - Resumo e Busca
1. Lista de PTMs com filtros combinados.
2. Página detalhe PTM com abas de histórico.
3. Painel resumo com métricas de repasse e andamento.

## Fase 4 - Importação de Dados
1. Comando `manage.py import_fem_excel --file <path>`.
2. Importação idempotente por `ORDEM`.
3. Relatório final de linhas importadas, atualizadas e rejeitadas.

## Critério de pronto do MVP
- Usuário consegue operar 100% do fluxo principal sem depender da planilha.
- Histórico por PTM preservado e consultável.
- Dados de lista centralizados em catálogos.
