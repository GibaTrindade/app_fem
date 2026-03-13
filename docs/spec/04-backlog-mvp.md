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

## Fase 3.1 - Documentação Pública
1. Gerar link público por PTM com código hash exclusivo.
2. Criar página pública resumida para envio de documentação sem login.
3. Registrar documentos enviados em modelo próprio vinculado ao PTM.
4. Criar catálogo de status de análise da documentação.
5. Exibir aba interna para analistas consultarem anexos e atualizarem o status da análise.

## Fase 4 - Importação de Dados
1. Comando `manage.py import_fem_excel --file <path>`.
2. Importação idempotente por `ORDEM`.
3. Relatório final de linhas importadas, atualizadas e rejeitadas.

## Critério de pronto do MVP
- Usuário consegue operar 100% do fluxo principal sem depender da planilha.
- Histórico por PTM preservado e consultável.
- Dados de lista centralizados em catálogos.
