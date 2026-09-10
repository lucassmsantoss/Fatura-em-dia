## Purpose

Garante que cada pessoa tenha uma conta própria e que os dados financeiros de uma conta nunca sejam visíveis ou alteráveis por outra. É a base de isolamento sobre a qual todas as demais capacidades operam.

## Requirements

### Requirement: Cadastro de conta
O sistema SHALL permitir a criação de uma conta a partir de nome, email e senha, e MUST recusar email já cadastrado.

#### Scenario: Cadastro com dados válidos
- **GIVEN** que não existe conta com o email informado
- **WHEN** a pessoa envia nome, email válido e senha de ao menos 6 caracteres
- **THEN** a conta é criada e devolvida sem expor a senha em nenhuma forma

#### Scenario: Email já cadastrado
- **GIVEN** que já existe uma conta com o email informado
- **WHEN** a pessoa tenta se cadastrar com esse mesmo email
- **THEN** o sistema recusa a criação e informa que já existe conta com esse email

#### Scenario: Caso de borda — senha curta demais
- **GIVEN** uma pessoa preenchendo o cadastro
- **WHEN** ela informa senha com menos de 6 caracteres
- **THEN** o sistema recusa a criação e nenhuma conta é persistida

### Requirement: Autenticação e sessão
O sistema SHALL autenticar por email e senha e emitir uma credencial de sessão com prazo de validade, sem nunca armazenar a senha em texto claro.

#### Scenario: Login com credenciais corretas
- **GIVEN** uma conta existente
- **WHEN** a pessoa informa o email e a senha corretos
- **THEN** o sistema devolve uma credencial de sessão utilizável nas requisições seguintes

#### Scenario: Caso de borda — senha incorreta não distingue de email inexistente
- **GIVEN** um email cadastrado e uma senha errada
- **WHEN** a pessoa tenta entrar
- **THEN** o sistema recusa com a mesma mensagem usada para email inexistente, sem revelar qual dos dois campos falhou

### Requirement: Isolamento de dados por conta
Toda leitura ou escrita de dados financeiros SHALL ser restrita à conta autenticada. Recurso pertencente a outra conta MUST ser tratado como inexistente.

#### Scenario: Requisição sem credencial
- **GIVEN** uma requisição a qualquer recurso financeiro
- **WHEN** ela não apresenta credencial válida
- **THEN** o sistema recusa o acesso e não devolve nenhum dado

#### Scenario: Caso de borda — recurso de outra conta
- **GIVEN** o identificador de um recurso que pertence a outra conta
- **WHEN** a pessoa autenticada tenta lê-lo, editá-lo ou removê-lo
- **THEN** o sistema responde como se o recurso não existisse e nada é alterado
