# Diretrizes de Governança e Regras de Contexto de IA (CONTEXT_RULES)

## Arquitetura e Estilo
1. **Linguagem:** Python 3.11+.
2. **Tipagem:** 100% Type Hints em parâmetros e retornos.
3. **Padrões:** PEP 8 com Google Style Docstrings.
4. **Exceções:** Utilização de TaskValidationError (herdando de ValueError).

## Proibições Explícitas
1. Proibido adicionar dependências externas não autorizadas.
2. Proibido alterar os cenários BDD do Test Harness.
3. Proibido persistir dados em disco ou banco de dados (processamento em memória).
4. Proibido modificar a assinatura principal `analyze_tasks(tasks: list[dict]) -> dict`.
5. Proibido ignorar/suprimir exceções de divisão por zero através de try-except genéricos sem validação de tamanho.