# Validação local

Data: 05/10/2026. Ambiente: Windows x64, Python 3.14.7 e SDK .NET 10.0.401 conforme aplicável.

**8 testes aprovados, sem falhas.** Instalação e comandos de execução foram conferidos conforme o README. Testes Python usam ambientes separados por projeto; testes C# usam migrations reais em SQLite em memória.

As três APIs também foram iniciadas como processos locais e verificadas por HTTP; o extrator executou os três documentos fictícios e exportou JSON, CSV e relatório (1 válido, 2 inválidos).

Links internos dos documentos foram verificados. Uma busca por padrões comuns de chaves não encontrou segredos nos fontes, e regras de exclusão do Git foram testadas. Essa busca é uma verificação limitada, não uma certificação de segurança.

Integrações reais PostgreSQL, SQL Server e LLM externo não foram executadas. Funcionalidades e limitações específicas estão no README. Workflows de CI foram incluídos, mas não executados no GitHub porque os repositórios ainda não foram publicados.
