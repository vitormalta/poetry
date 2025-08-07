# Em tests/bdd/conftest.py

# Importa todas as "ferramentas" que precisamos da sua localização original
# para torná-las visíveis para os nossos testes BDD.
from tests.console.conftest import (
    app,
    command_tester_factory,
    env,
    poetry,
    project_directory,
)

# A linha abaixo é uma boa prática para que as ferramentas de análise
# de código saibam que as fixtures estão sendo usadas intencionalmente.
__all__ = ["app", "command_tester_factory", "env", "poetry", "project_directory"]