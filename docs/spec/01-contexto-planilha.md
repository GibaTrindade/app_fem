# Contexto da Planilha FEM 2013

## Objetivo observado
A planilha `CONTROLE FEM _ 2013.xlsm` controla o ciclo de vida de PTMs (projetos municipais) do FEM, com foco em:
- dados cadastrais do PTM;
- trilha de eventos e evolução de status;
- repasses/pagamentos por parcelas;
- vistorias e percentual de execução;
- prestação de contas;
- observações/encaminhamentos e conclusão informal.

## Estrutura macro (abas)
- `INF GERAIS`: base principal por PTM (465 registros ativos observados).
- `RESUMO`: indicadores consolidados (majoritariamente fórmulas).
- `EVENTOS`: histórico de eventos por PTM (até 15 blocos de evento no layout atual).
- `PAGAMENTOS`: repasses e pagamentos em parcelas (1ª a 4ª + blocos extras).
- `VISTORIA`: até 5 vistorias por PTM.
- `PRESTAÇÃO DE CONTAS`: prazo, situação e até 11 observações datadas.
- `OBS  ENC`: observações e encaminhamentos (até 20 pares observação/data).
- `CONCLUSÃO INFORMAL`: até 3 registros de percentual declarado/contato.
- `APOIO`: listas de referência, usuários e parâmetros auxiliares.
- `TERMO DE ADESÃO`: visão auxiliar com vínculos à base principal.

## Chave lógica identificada
Cada linha (faixa 7..471) representa um PTM. As abas de processo repetem os dados-base da mesma linha da aba `INF GERAIS`, mantendo correlação por posição de linha e pelo campo `ORDEM`.

## Listas controladas detectadas
- Tipo FEM: `NORMAL`, `MULHER`, `EMENDA`.
- Status PTM (26 valores), incluindo: `APROVADO`, `AGUARDANDO ...`, `CONCLUÍDO`, `PC APROVADA`, `PC REPROVADA`, `TERMO DE ENCERRAMENTO`, `EM CONFERÊNCIA PARA TEMAI`.
- Status Obra: `NÃO INICIADA`, `EM ANDAMENTO`, `PARALISADA`, `CONCLUÍDA`, `CANCELADA`.
- Área de Investimento (7 valores).
- Secretaria Finalística (17 valores).
- Parcela (pagamentos extras): `1ª`, `2ª`, `3ª`, `4ª`.

## Regras implícitas observadas
- Status atual do PTM/obra em `INF GERAIS` é derivado do último evento válido em `EVENTOS`.
- `RESUMO` centraliza cálculos de repasse, saldo, parcela pendente e situação com base em `PAGAMENTOS` e `VISTORIA`.
- Há uso de macros e fórmulas para navegação/consistência e sufixo visual em `ORDEM`.

## Volumetria observada
- PTMs na base: 465.
- Municípios únicos: 184.
- Capacidade no layout atual por PTM: 19 eventos, 6 registros de parcela em pagamentos, 5 vistorias, 11 observações de prestação, 20 observações/encaminhamentos.
