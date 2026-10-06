# Process Management API

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![Pytest](https://img.shields.io/badge/Tests-Pytest-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

API REST para **gestão e acompanhamento de processos**, com responsáveis, prazos, histórico de movimentações, regras de SLA e indicadores operacionais.

O projeto foi desenvolvido como portfólio de backend para demonstrar organização em camadas, modelagem de regras de negócio, persistência com SQLAlchemy, validação com Pydantic, documentação OpenAPI/Swagger e testes automatizados.

## Problema de negócio

Em operações que acompanham muitos processos simultaneamente, não basta armazenar registros. É necessário identificar rapidamente:

- quem é o responsável por cada processo;
- quais processos estão vencidos;
- quais estão fora do SLA;
- qual é o histórico de movimentações;
- como o volume está distribuído por situação.

A **Process Management API** transforma essas necessidades em uma API estruturada, permitindo registrar processos, acompanhar prazos e consultar indicadores de forma padronizada.

## Principais funcionalidades

- Cadastro e consulta de responsáveis.
- CRUD de processos com exclusão lógica (*soft delete*).
- Situações `open`, `in_progress` e `completed`.
- Validação de datas e regras de conclusão.
- Filtros por situação, responsável, data de vencimento e atraso.
- Cálculo automático de dias restantes para o vencimento.
- Identificação de processos vencidos e fora do SLA.
- Registro automático de movimentações em alterações de processo.
- Inclusão manual de observações no histórico.
- Indicadores de volume, atraso, SLA e distribuição por situação.
- Documentação interativa via Swagger/OpenAPI.
- Testes automatizados com Pytest.
- Validação automática por GitHub Actions em `push` e `pull_request`.

## Stack

| Tecnologia | Uso no projeto |
|---|---|
| Python | Linguagem principal |
| FastAPI | API REST e documentação OpenAPI |
| Pydantic | Validação e contratos de entrada/saída |
| SQLAlchemy | ORM e camada de persistência |
| SQLite | Banco utilizado na execução e nos testes locais |
| PostgreSQL / Psycopg | Alternativa configurável de banco relacional |
| Pytest | Testes automatizados |
| Uvicorn | Servidor ASGI |
| GitHub Actions | Execução automatizada dos testes |

## Arquitetura

O projeto separa transporte HTTP, validação, regras de negócio e persistência.

```mermaid
flowchart LR
    Client[Cliente / Frontend] --> API[FastAPI Routes]
    API --> Schemas[Pydantic Schemas]
    API --> Services[Service Layer]
    Services --> Repositories[Repository Layer]
    Repositories --> ORM[SQLAlchemy ORM]
    ORM --> DB[(SQLite / PostgreSQL)]
    Services --> History[Movimentações / Histórico]
```

### Estrutura do projeto

```text
app/
├── main.py                 # Inicialização da API e tratamento de erros
├── database.py             # Engine, sessão e configuração do banco
├── seed.py                 # Dados fictícios para demonstração
├── models/
│   └── entities.py         # Entidades SQLAlchemy
├── schemas/
│   └── processes.py        # Contratos e validações Pydantic
├── repositories/
│   └── processes.py        # Consultas e persistência
├── services/
│   └── processes.py        # Regras de negócio e transações
└── routes/
    └── processes.py        # Endpoints HTTP

tests/
└── test_processes.py       # Testes automatizados

.github/workflows/
└── tests.yml               # Pipeline de validação
```

## Endpoints

| Método | Endpoint | Finalidade |
|---|---|---|
| `POST` | `/owners` | Criar responsável |
| `GET` | `/owners` | Listar responsáveis |
| `POST` | `/processes` | Criar processo |
| `GET` | `/processes` | Listar e filtrar processos |
| `GET` | `/processes/{id}` | Consultar processo |
| `PUT` | `/processes/{id}` | Atualizar processo |
| `DELETE` | `/processes/{id}` | Excluir processo logicamente |
| `GET` | `/processes/{id}/movements` | Consultar histórico |
| `POST` | `/processes/{id}/movements` | Adicionar movimentação |
| `GET` | `/indicators` | Consultar indicadores operacionais |

A documentação completa dos contratos pode ser explorada pela interface Swagger em `/docs` após iniciar a aplicação.

## Filtros disponíveis

`GET /processes` aceita filtros opcionais:

- `status`: `open`, `in_progress` ou `completed`;
- `owner_id`: identificador do responsável;
- `due_before`: vencimento máximo;
- `overdue`: filtra processos vencidos ou não vencidos.

Exemplo:

```http
GET /processes?status=open&overdue=true
```

## Regras de negócio

### Vencimento

Um processo é considerado vencido quando a data de referência é **posterior** à `due_date`.

### SLA

O SLA é considerado excedido quando a quantidade de dias corridos desde `start_date` é **maior** que `sla_days`. No próprio limite, o processo ainda está dentro do SLA.

Para processos concluídos, a referência é `completed_date`. Para processos ativos, a referência é a data atual.

### Conclusão

- `status="completed"` exige `completed_date`.
- Processos ativos não podem possuir `completed_date`.
- `due_date` não pode ser anterior a `start_date`.
- `completed_date`, quando informada, deve estar entre `start_date` e a data atual.

### Exclusão lógica

A exclusão de um processo não remove fisicamente o registro. Processos excluídos deixam de aparecer nas consultas e não participam dos indicadores.

## Instalação

### Requisitos

- Python 3.11 ou superior
- Git

Clone o repositório e acesse a pasta do projeto:

```bash
git clone https://github.com/barcelosneto/process-management-api.git
cd process-management-api
```

Crie o ambiente virtual:

```bash
python -m venv .venv
```

### Windows / PowerShell

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m app.seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 18000
```

### Linux / macOS

```bash
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python -m app.seed
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 18000
```

Depois, acesse:

```text
http://127.0.0.1:18000/docs
```

O seed utiliza dados explicitamente fictícios e datas relativas ao momento da execução. Ele não duplica os dados quando já existe responsável cadastrado.

## Exemplo de uso

### Criar responsável

```http
POST /owners
Content-Type: application/json

{
  "name": "Responsible FICTITIOUS B"
}
```

### Criar processo

```http
POST /processes
Content-Type: application/json

{
  "title": "FICTITIOUS review",
  "owner_id": 1,
  "status": "open",
  "start_date": "2025-01-01",
  "due_date": "2025-01-10",
  "sla_days": 5,
  "completed_date": null
}
```

### Resposta ilustrativa

```json
{
  "id": 1,
  "title": "FICTITIOUS review",
  "owner_id": 1,
  "status": "open",
  "start_date": "2025-01-01",
  "due_date": "2025-01-10",
  "sla_days": 5,
  "completed_date": null,
  "days_until_due": -1,
  "overdue": true,
  "outside_sla": true
}
```

Os IDs e os campos calculados variam conforme o banco e a data da execução.

## Indicadores

`GET /indicators` consolida uma visão operacional dos processos ativos no banco.

Exemplo de estrutura de resposta:

```json
{
  "total": 12,
  "overdue": 3,
  "outside_sla": 4,
  "by_status": {
    "open": 5,
    "in_progress": 4,
    "completed": 3
  }
}
```

## Tratamento de erros

A API utiliza respostas HTTP coerentes com cada cenário:

| Status | Situação |
|---|---|
| `404` | Recurso não encontrado |
| `422` | Dados de entrada inválidos |
| `500` | Falha de persistência, sem exposição de detalhes internos |

## Testes

No Windows / PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

No Linux / macOS:

```bash
.venv/bin/python -m pytest -q
```

Os testes utilizam SQLite em memória e não dependem de credenciais ou serviços externos.

A suíte cobre, entre outros cenários:

- criação, consulta e atualização de processos;
- histórico de movimentações;
- filtros;
- exclusão lógica;
- indicadores;
- responsável inexistente;
- inconsistências de datas;
- campos vazios;
- limites das regras de SLA.

## PostgreSQL

A camada SQLAlchemy permite utilizar PostgreSQL por meio da variável `DATABASE_URL`.

Exemplo:

```env
DATABASE_URL=postgresql+psycopg://USUARIO:SENHA@localhost:5432/portfolio
```

Utilize credenciais próprias somente no ambiente local. O banco deve existir previamente.

> A integração PostgreSQL está prevista pela configuração do projeto, mas não foi executada na validação local atual.

## Decisões técnicas

- **Service Layer:** concentra regras de negócio fora das rotas HTTP.
- **Repository Layer:** isola consultas e operações de persistência.
- **Pydantic:** mantém validações próximas aos contratos da API.
- **Soft delete:** preserva registros em vez de removê-los fisicamente.
- **Histórico transacional:** alterações de processos podem gerar movimentações dentro do fluxo de persistência.
- **SQLite em memória nos testes:** mantém a suíte independente de infraestrutura externa.

## Limitações atuais e roadmap

O projeto foi desenhado para demonstração local e ainda não representa uma aplicação pronta para produção em larga escala.

Próximas evoluções planejadas:

- [ ] autenticação e autorização;
- [ ] paginação das consultas;
- [ ] migrations com Alembic;
- [ ] índices orientados ao volume real de dados;
- [ ] agregações SQL para indicadores em grandes volumes;
- [ ] controle de concorrência;
- [ ] logging estruturado;
- [ ] trilha de auditoria imutável;
- [ ] calendário de dias úteis;
- [ ] anexos aos processos.

## CI

O repositório possui workflow do GitHub Actions para executar a suíte de testes automaticamente em `push` e `pull_request`.

Arquivo:

```text
.github/workflows/tests.yml
```

## Documentação adicional

- [Guia de entrevista](INTERVIEW_GUIDE.md)
- [Comandos de publicação](GIT_SETUP.md)
- [Validação do projeto](VALIDATION.md)
- [Licença MIT](LICENSE)

## Autor

**Pedro Moacyr Barcelos Neto**  
Backend Developer — Python | C# / ASP.NET Core | REST APIs | Automação | IA

- GitHub: [github.com/barcelosneto](https://github.com/barcelosneto)
- LinkedIn: adicione aqui a URL personalizada do seu perfil LinkedIn

---

Este projeto utiliza somente dados fictícios para demonstração e não contém informações reais de processos, responsáveis ou organizações.
