# TaskAnalyzer - SDD & AI Assisted Development

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](#executando-os-testes)

**Autor:** Diogo Lucas Sobreira de Lucena  
**Curso:** Ciência da Computação - CEUB (Asa Norte - B)  
**Disciplina:** Bootcamp III (Fase 2)  

## Sobre o Projeto
O **TaskAnalyzer** é um componente de software moderno para consolidação de métricas de produtividade, calculando tempo médio de conclusão, taxa de atrasos e agregação por níveis de prioridade.

## Governança e Ética (Critical-in-the-Loop)
Este sistema foi desenvolvido sob rígidas regras de contexto (`CONTEXT_RULES.md`) e um Documento de Design de Sistema (SDD). O código gerado por IA passou por homologação humana ativa, garantindo que lógicas fora do contrato de negócio ou bibliotecas não autorizadas fossem bloqueadas. 

## Como Executar

### 1. Clonar o repositório
```bash
git clone [https://github.com/SEU_USUARIO/sdd-task-analyzer.git](https://github.com/SEU_USUARIO/sdd-task-analyzer.git)
cd sdd-task-analyzer
```
### 2. Execução via Docker
```bash
docker compose build
docker compose run testes
```

### 3. Execução local
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows
pip install -r requirements.txt
pytest tests/test_harness.py -v
````

