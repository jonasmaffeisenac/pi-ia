---
name: python-expert
description: >-
  Especialista em desenvolvimento Python moderno, arquitetura de software, boas práticas (PEP 8, tipagem, design patterns), depuração e otimização de performance. Use esta skill para projetar, refatorar, testar ou otimizar aplicações Python.
---

# Python Expert Skill

Diretrizes e padrões para atuar como especialista em desenvolvimento Python moderno.

## 1. Padrões de Código e Idiomática (Pythonic)
- **Tipagem Estática:** Utilize anotações de tipo (`typing`, `TypeVar`, `Union`, `Optional`, `tuple[...]`, `list[...]` a partir do Python 3.9+) em funções públicas e estruturas de dados.
- **PEP 8:** Nomes em `snake_case` para funções/variáveis, `PascalCase` para classes e `SCREAMING_SNAKE_CASE` para constantes.
- **Estruturas Modernas:** Prefira `dataclasses` ou `NamedTuple` para modelos de dados imutáveis/simples antes de classes genéricas.
- **Context Managers:** Utilize `with` para manipulação de arquivos, locks, conexões de banco e pools de sockets.

## 2. Tratamento de Exceções e Resiliência
- Capture exceções específicas (`except (FileNotFoundError, ValueError):`) em vez de `except Exception:` genérico, a menos que seja um handler global de último nível.
- Crie exceções customizadas herdando de `Exception` para isolar erros de domínio/negócio.
- Use `try...except...finally` para garantir liberação adequada de recursos.

## 3. Performance e Concorrência
- **Geradores e Iteradores:** Use generator expressions e `yield` para lidar com grandes volumes de dados sem estourar memória.
- **Concorrência:**
  - I/O bound (rede, scraping, APIs assíncronas): utilize `asyncio` (`aiohttp`, `async/await`).
  - CPU bound: utilize `multiprocessing` ou `concurrent.futures.ProcessPoolExecutor` para contornar o GIL quando aplicável.
  - Tarefas I/O clássicas: utilize `concurrent.futures.ThreadPoolExecutor`.
- **Profiling:** Recomende `cProfile`, `timeit` ou `tracemalloc` antes de qualquer otimização prematura.

## 4. Testes e Qualidade
- Priorize testes unitários e de integração com `pytest`.
- Use fixtures reutilizáveis e parametrização (`@pytest.mark.parametrize`).
- Mantenha linting e formatação automatizados (`ruff`, `flake8`, `black`).
