# Process Management API

API REST de acompanhamento de processos com responsáveis, prazos, histórico e indicadores. Demonstra separação entre persistência, regras de negócio, contratos e transporte HTTP.

## Tecnologias

Python, FastAPI, SQLAlchemy, Pydantic, SQLite, Psycopg, OpenAPI/Swagger e Pytest. PostgreSQL é uma alternativa configurável pelo SQLAlchemy; a validação local utiliza SQLite.

## Funcionalidades

- Cadastro e consulta de responsáveis; CRUD de processos com exclusão lógica.
- Situações `open`, `in_progress` e `completed`, com data de conclusão obrigatória na última.
- Filtros de situação, responsável, vencimento máximo e atraso.
- Cálculo de dias restantes, vencimento e SLA em dias corridos.
- Movimentações automáticas nas alterações e registro manual de observações.
- Indicadores de volume, atraso, SLA e distribuição por situação.

## Instalação

Requisitos: Python 3.11 ou superior e acesso à internet para instalar as dependências. Execute na raiz deste repositório. Os comandos abaixo usam PowerShell e não exigem ativar o ambiente virtual.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Em Linux/macOS, use `python3` na criação do ambiente e `.venv/bin/python` no lugar de `.\.venv\Scripts\python.exe`.

## Execução e demonstração

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 18000
```

Abra [Swagger](http://127.0.0.1:18000/docs). O seed cria um responsável e dois processos explicitamente fictícios, com datas relativas ao dia de execução. Repetir o seed não duplica dados: ele é ignorado quando já existe algum responsável.

O banco SQLite é criado na raiz pelo seed ou pela inicialização da API. Não há migrations neste projeto: `create_all` cria tabelas ausentes, sem atualizar tabelas existentes. Para evoluir o schema, adote Alembic.

## Exemplos HTTP

No PowerShell, após iniciar a API:

```powershell
$owner = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:18000/owners -ContentType 'application/json' -Body '{"name":"Responsible FICTITIOUS B"}'
$body = @{title='FICTITIOUS review'; owner_id=$owner.id; status='open'; start_date='2025-01-01'; due_date='2025-01-10'; sla_days=5} | ConvertTo-Json
$process = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:18000/processes -ContentType 'application/json' -Body $body
Invoke-RestMethod -Uri 'http://127.0.0.1:18000/processes?status=open&overdue=true'
Invoke-RestMethod -Uri http://127.0.0.1:18000/indicators
Invoke-RestMethod -Uri "http://127.0.0.1:18000/processes/$($process.id)/movements"
```

Resposta de criação, ilustrativa para um banco novo e execução em 2025-01-11 (datas de exemplo fictícias):

```json
{"id":1,"title":"FICTITIOUS review","owner_id":1,"status":"open","start_date":"2025-01-01","due_date":"2025-01-10","sla_days":5,"completed_date":null,"days_until_due":-1,"overdue":true,"outside_sla":true}
```

IDs e dias restantes variam conforme o banco e a data da execução. `PUT /processes/{id}` substitui os campos editáveis com o mesmo contrato da criação. `DELETE /processes/{id}` retorna 204; depois, consultas retornam 404. `POST /processes/{id}/movements` aceita `{"description":"FICTITIOUS observation"}`. `GET /owners` lista responsáveis.

Erros: entrada inválida retorna 422, recurso inexistente retorna 404 com `detail`, e falha de persistência retorna 500 sem detalhes internos.

## Regras de SLA

O vencimento é excedido quando a data de referência é **posterior** a `due_date`. O SLA é excedido quando os dias corridos desde `start_date` são **maiores** que `sla_days`; no limite ainda está dentro. Para processos concluídos, a referência é `completed_date`; para ativos, é a data atual. `days_until_due` sempre representa a distância entre hoje e o vencimento. Processos excluídos não entram nos indicadores.

## Arquitetura

`app/database.py` configura sessões; `models/` define tabelas; `schemas/` valida contratos; `repositories/` consulta dados; `services/` aplica regras e grava movimentações na mesma transação; `routes/` expõe HTTP; `main.py` centraliza erros. `tests/` utiliza SQLite em memória isolado.

## PostgreSQL

Defina `DATABASE_URL=postgresql+psycopg://USUARIO:SENHA@localhost:5432/portfolio` no `.env`, usando credenciais próprias apenas no ambiente. Crie previamente o banco e instale `requirements.txt`. Este é um exemplo de configuração com placeholders, sem credenciais reais. A mesma camada SQLAlchemy seleciona o driver. Integração PostgreSQL não foi executada na validação local.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Os testes são locais e não exigem credenciais nem serviços externos.

São cobertos CRUD, histórico, filtros, exclusão lógica, indicadores, responsável ausente, datas inconsistentes, campos vazios e limites de SLA.

## Limitações e melhorias futuras

Adicionar autenticação/autorização, paginação, Alembic, controle de concorrência e índices orientados ao volume real. Os indicadores materializam a lista de processos; para grande volume, calcular agregações SQL. Não há calendário de dias úteis, anexos, exclusão de responsáveis ou trilha imutável auditável.

## Documentação adicional

- [Guia de entrevista](INTERVIEW_GUIDE.md)
- [Comandos de publicação](GIT_SETUP.md)
- [Licença MIT](LICENSE)

Todos os dados de demonstração são fictícios. As aplicações foram projetadas para demonstração local; não possuem autenticação de usuários.
