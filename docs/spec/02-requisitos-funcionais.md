# Requisitos Funcionais (MVP) - App FEM

## Escopo do MVP
Substituir a operação da planilha por aplicação web Django com persistência SQLite, mantendo rastreabilidade histórica.

## Módulos
1. Cadastro PTM
- Criar/editar PTM com dados de identificação e financeiros principais.
- Campos de lista com validação por catálogo.
- Pesquisa por ORDEM, município, status, secretaria e área.

2. Eventos
- Registrar eventos cronológicos de PTM com data, descrição, status PTM e status obra.
- Exibir timeline por PTM.
- Calcular status atual do PTM/obra a partir do último evento.

3. Pagamentos
- Registrar solicitação, envio, valor previsto/realizado, data de pagamento, OB, empenho e observações.
- Suportar múltiplas parcelas por PTM (não fixar em 4 para evitar limitação de layout Excel).
- Consolidar total repassado e saldo a receber.

4. Vistoria
- Registrar solicitações e respostas de vistoria com percentual de execução e observação.
- Exibir evolução de execução por PTM.

5. Prestação de Contas
- Registrar prazo, data de prestação, situação e histórico de observações datadas.

6. Observações/Encaminhamentos
- Registrar histórico livre com data para tratativas administrativas.

7. Conclusão Informal
- Registrar percentual declarado, contato e observação em múltiplos apontamentos.

8. Resumo
- Painel consolidado por PTM com principais indicadores e último andamento.

## Requisitos transversais
- Auditoria básica: `created_at`, `updated_at`, `created_by`, `updated_by`.
- Integridade: operações por chave de PTM (não por posição de linha).
- Controle de acesso simples no MVP:
  - Administrador: gerencia catálogos e usuários.
  - Operador: mantém dados operacionais.
  - Leitor: consulta.

## Fora do MVP (fase 2)
- Importação incremental automática por Excel.
- Assinaturas/documentos digitais.
- Workflow formal com SLAs e notificações.
- Banco PostgreSQL e deploy em produção.
