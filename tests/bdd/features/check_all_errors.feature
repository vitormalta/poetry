# language: pt
Funcionalidade: Verificação de pyproject.toml com múltiplos erros
  Para que eu possa corrigir meu arquivo de configuração de forma eficiente,
  Como um desenvolvedor usando Poetry,
  Eu quero que o comando "check" me mostre todos os erros de uma vez.

  Cenário: Verificando um pyproject.toml com múltiplos erros usando a flag --all-errors
    Dado um arquivo "pyproject.toml" com um classificador inválido e um README faltando
    Quando eu executo o comando "poetry check --all-errors"
    Então a saída deve conter a mensagem "Unrecognized Classifier"
    E a saída deve conter a mensagem "Declared README file does not exist"
    E o comando deve terminar com um status de erro