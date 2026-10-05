# Guia de entrevista — process-management-api

## Problema, arquitetura e decisões

O problema é acompanhar processos e identificar risco de prazo com uma regra reproduzível. A requisição percorre routes → schemas → services → repositories/models → Session SQLAlchemy. FastAPI oferece OpenAPI; Pydantic valida contratos; SQLAlchemy permite SQLite local e opção PostgreSQL. O banco relaciona owners, processes e movements, com exclusão lógica e histórico transacional. As rotas e exemplos estão no README. Estude principalmente `app/services/processes.py` para SLA, conclusão e atomicidade, e `tests/test_processes.py` para os limites. Não há autenticação, paginação, migrations incrementais ou controle de concorrência; essas são prioridades para produção.

## Roteiro de estudo

1. Execute os comandos do [README](README.md) e observe as saídas.
2. Execute os testes e leia os casos antes de alterar as regras.
3. Acompanhe uma entrada desde o contrato até a persistência ou saída.
4. Reproduza uma falha de validação e explique sua resposta.
5. Distinga o que foi implementado, o que foi validado e o que é melhoria futura.

## 15 perguntas com respostas

### 1. Como os prazos são calculados?

`present` usa `date.today()` e subtrai datas, produzindo dias corridos. O vencimento é excedido apenas depois da data limite. Nos testes, uma data explícita evita dependência do relógio.

### 2. Qual a diferença entre vencimento e SLA?

Vencimento usa `due_date`. SLA mede dias desde `start_date` e compara com `sla_days`. Um processo pode ultrapassar o SLA antes de vencer.

### 3. Como a conclusão afeta os indicadores?

`completed_date` congela a referência de atraso e SLA. Um processo concluído no prazo não passa a atrasado quando o relógio avança.

### 4. Por que usar validação de modelo?

Pydantic valida campos individuais e `model_validator` aplica relações entre datas e situação antes de entrar no serviço. Isso evita persistir combinações inconsistentes.

### 5. Como funciona a exclusão lógica?

`deleted=True` mantém a linha e o histórico. O repository filtra linhas excluídas em listas e buscas. Indicadores dependem da mesma lista filtrada.

### 6. A movimentação e a atualização podem divergir?

O serviço grava ambas na mesma sessão e realiza um commit conjunto. `flush` obtém o ID sem confirmar a transação. Uma falha antes do commit impede a confirmação do conjunto.

### 7. Como o responsável é validado?

O serviço consulta `Owner` antes de gravar. A coluna também tem chave estrangeira; SQLite ativa foreign keys na conexão de produção. Os testes atualmente verificam a validação pelo serviço.

### 8. Por que separar repository e service?

Repository concentra consultas e filtros; service conhece regras e transações. Rotas ficam focadas em HTTP e contratos. A divisão é pequena e específica ao domínio.

### 9. Como evitar overposting?

O contrato de entrada não contém ID, deleted ou campos calculados. O serviço só atribui campos de `ProcessInput`; o cliente não controla campos internos.

### 10. Como os erros são apresentados?

DomainError transporta status e mensagem seguros. Falhas SQLAlchemy recebem resposta genérica 500 e log interno. Entradas inválidas são respondidas pelo FastAPI com 422.

### 11. Como os testes isolam o banco?

Cada fixture cria SQLite em memória com StaticPool e substitui `get_session`. Isso compartilha o banco entre conexões do teste, mas não entre testes. A substituição é removida ao final.

### 12. O que muda no PostgreSQL?

A URL seleciona Psycopg; entidades e consultas continuam SQLAlchemy. É necessário criar o banco e validar comportamento no servidor real. A demonstração não afirma testes PostgreSQL.

### 13. Por que não há migrations?

`create_all` simplifica a execução inicial, mas não modifica tabelas existentes. Alembic seria necessário para evoluções controladas em ambientes persistentes.

### 14. Como tratar concorrência?

Hoje atualizações usam último commit vencedor. Em produção, uma coluna de versão e atualização condicional impediriam perda silenciosa de alterações. Essa proteção ainda não está implementada.

### 15. Como escalar os indicadores?

A implementação carrega a lista e agrega em Python. Para volumes grandes, usaria agregações SQL, índices nos filtros e paginação das listagens. Mediria consultas antes de otimizar.

