# Publicação no GitHub

Execute no PowerShell dentro desta pasta, depois de criar um repositório vazio chamado `process-management-api` no GitHub. Substitua **SEU-USUARIO** pelo seu usuário real. Não adicione README remoto antes do primeiro push.

```powershell
cd C:\Portfolio-Backend\process-management-api
git init
git add .
git status
git commit -m "feat: implement process-management-api with tests and documentation"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/process-management-api.git
git push -u origin main
```

Revise `git status` antes do commit. Sua identidade deve estar configurada em `git config user.name` e `git config user.email`; a autenticação do GitHub é feita pelo Git, fora do código.

## Referência de evolução

Esta sequência é apenas uma sugestão para futuras implementações incrementais. Os arquivos atuais podem ser publicados em um primeiro commit único. Não recrie um histórico artificial nem altere datas.

1. Definir domínio e critérios de aceitação.
2. Configurar dependências e ambiente.
3. Adicionar modelos e contratos.
4. Implementar persistência ou leitura de documentos.
5. Implementar regras principais.
6. Adicionar interface HTTP ou CLI.
7. Tratar entradas inválidas e exceções.
8. Adicionar dados fictícios de demonstração.
9. Adicionar testes de comportamento.
10. Documentar execução e decisões técnicas.
