# Em tests/bdd/test_check_all_errors.py

from __future__ import annotations

from pathlib import Path
import pytest
from pytest_bdd import given, when, then, scenario

from poetry.factory import Factory # Importe a Factory

# Liga este arquivo de teste ao nosso cenário no arquivo .feature
@scenario("features/check_all_errors.feature", "Verificando um pyproject.toml com múltiplos erros usando a flag --all-errors")
def test_check_with_all_errors():
    pass

# Cria um contexto compartilhado para os passos do cenário
@pytest.fixture
def context():
    return {}

# Implementação do passo "Dado"
@given("um arquivo \"pyproject.toml\" com um classificador inválido e um README faltando")
def given_invalid_pyproject_file(tmp_path: Path, context):
    content = """
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = ""
authors = ["Your Name <you@example.com>"]
classifiers = [
    "Topic :: Software Development :: Build Tools",
    "Unrecognized Classifier :: Should Fail"
]
readme = "README.md" # Arquivo não existe

[tool.poetry.dependencies]
python = "^3.9"
"""
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text(content, encoding="utf-8")
    context["working_dir"] = tmp_path

# Implementação do passo "Quando"
@when("eu executo o comando \"poetry check --all-errors\"")
def when_i_run_check(command_tester_factory, context):
    # CORREÇÃO FINAL: Criamos a instância do Poetry aqui
    poetry = Factory().create_poetry(context["working_dir"])
    tester = command_tester_factory("check", poetry=poetry)
    
    status_code = tester.execute("--all-errors", decorated=False)

    context["status_code"] = status_code
    context["output"] = tester.io.fetch_error()

# Implementação do passo "Então"
@then("a saída deve conter a mensagem \"Unrecognized Classifier\"")
def then_output_contains_classifier_error(context):
    assert "Unrecognized Classifier" in context["output"]

@then("a saída deve conter a mensagem \"Declared README file does not exist\"")
def then_output_contains_readme_error(context):
    assert "Declared README file does not exist" in context["output"]

@then("o comando deve terminar com um status de erro")
def then_command_fails(context):
    assert context["status_code"] == 1