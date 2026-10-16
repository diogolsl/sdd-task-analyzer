"""Suíte de testes automatizada (Test Harness) para o TaskAnalyzer.

Mapeia diretamente os Cenários de Aceite (Dado-Quando-Então) definidos no SDD.
"""

import pytest
from src.task_analyzer import TaskValidationError, analyze_tasks


@pytest.fixture
def massa_dados_valida():
    """Fixture com conjunto diversificado de tarefas válidas."""
    return [
        {
            "id": 1,
            "titulo": "Implementar login OAuth",
            "prioridade": "ALTA",
            "data_criacao": "2026-03-01T08:00:00",
            "data_vencimento": "2026-03-01T12:00:00",
            "data_conclusao": "2026-03-01T10:00:00",  # Duração: 2h (No prazo)
            "status": "CONCLUIDA",
        },
        {
            "id": 2,
            "titulo": "Corrigir bug de renderização",
            "prioridade": "ALTA",
            "data_criacao": "2026-03-01T08:00:00",
            "data_vencimento": "2026-03-01T10:00:00",
            "data_conclusao": "2026-03-01T14:00:00",  # Duração: 6h (Atrasada em 4h)
            "status": "CONCLUIDA",
        },
        {
            "id": 3,
            "titulo": "Atualizar documentação de API",
            "prioridade": "MEDIA",
            "data_criacao": "2026-03-01T09:00:00",
            "data_vencimento": "2026-03-01T17:00:00",
            "data_conclusao": "2026-03-01T13:00:00",  # Duração: 4h (No prazo)
            "status": "CONCLUIDA",
        },
        {
            "id": 4,
            "titulo": "Refatorar módulo de banco de dados",
            "prioridade": "BAIXA",
            "data_criacao": "2026-03-01T10:00:00",
            "data_vencimento": "2026-03-05T18:00:00",
            "data_conclusao": None,
            "status": "PENDENTE",
        },
    ]


def test_cenario_1_sucesso_metricas_gerais_e_por_prioridade(massa_dados_valida):
    """Cenário 1: Sucesso no Processamento de Métricas.

    Dado uma lista de tarefas válidas
    Quando o analisador for executado
    Então as métricas gerais e por prioridade devem ser calculadas corretamente.
    """
    resultado = analyze_tasks(massa_dados_valida)

    # Métricas Gerais
    assert resultado["total_tarefas"] == 4
    assert resultado["total_concluidas"] == 3
    assert resultado["total_atrasadas"] == 1
    # Duracoes: 2h, 6h, 4h -> Média = (2 + 6 + 4) / 3 = 4.0h
    assert resultado["tempo_medio_conclusao_horas"] == 4.0
    # Taxa de Atraso Geral: (1 / 3) * 100 = 33.33%
    assert resultado["taxa_atraso_percentual"] == 33.33

    # Métricas Prioridade ALTA (2 concluidas: 1 atrasada, 1 no prazo)
    alta = resultado["metricas_por_prioridade"]["ALTA"]
    assert alta["total_tarefas"] == 2
    assert alta["total_concluidas"] == 2
    assert alta["total_atrasadas"] == 1
    assert alta["tempo_medio_conclusao_horas"] == 4.0  # (2 + 6) / 2
    assert alta["taxa_atraso_percentual"] == 50.0

    # Métricas Prioridade MEDIA (1 concluída no prazo)
    media = resultado["metricas_por_prioridade"]["MEDIA"]
    assert media["total_tarefas"] == 1
    assert media["total_concluidas"] == 1
    assert media["total_atrasadas"] == 0
    assert media["tempo_medio_conclusao_horas"] == 4.0
    assert media["taxa_atraso_percentual"] == 0.0

    # Métricas Prioridade BAIXA (1 pendente)
    baixa = resultado["metricas_por_prioridade"]["BAIXA"]
    assert baixa["total_tarefas"] == 1
    assert baixa["total_concluidas"] == 0
    assert baixa["total_atrasadas"] == 0
    assert baixa["tempo_medio_conclusao_horas"] == 0.0
    assert baixa["taxa_atraso_percentual"] == 0.0


def test_cenario_2_excecao_datas_incoerentes():
    """Cenário 2: Exceção para Datas Incoerentes (RN-04).

    Dado uma tarefa onde data_conclusao < data_criacao
    Quando o analisador for executado
    Então deve disparar TaskValidationError e ValueError.
    """
    tarefa_invalida = [
        {
            "id": 99,
            "titulo": "Tarefa com viagem no tempo",
            "prioridade": "ALTA",
            "data_criacao": "2026-03-02T10:00:00",
            "data_vencimento": "2026-03-05T10:00:00",
            "data_conclusao": "2026-03-01T10:00:00",  # Conclusão anterior à criação!
            "status": "CONCLUIDA",
        }
    ]

    with pytest.raises((TaskValidationError, ValueError)) as exc_info:
        analyze_tasks(tarefa_invalida)

    assert "anterior à data_criacao" in str(exc_info.value)


def test_cenario_3_casos_de_borda_entrada_vazia_ou_apenas_pendentes():
    """Cenário 3: Entrada Vazia ou Sem Concluídas (RN-05).

    Dado lista vazia ou contendo apenas tarefas pendentes
    Quando o analisador for executado
    Então deve retornar métricas zeradas sem disparar ZeroDivisionError.
    """
    # Caso 3a: Lista Vazia
    res_vazio = analyze_tasks([])
    assert res_vazio["total_tarefas"] == 0
    assert res_vazio["total_concluidas"] == 0
    assert res_vazio["tempo_medio_conclusao_horas"] == 0.0
    assert res_vazio["taxa_atraso_percentual"] == 0.0

    # Caso 3b: Apenas Pendentes
    apenas_pendentes = [
        {
            "id": 10,
            "titulo": "Apenas pendente",
            "prioridade": "MEDIA",
            "data_criacao": "2026-03-01T08:00:00",
            "data_vencimento": "2026-03-02T08:00:00",
            "data_conclusao": None,
            "status": "PENDENTE",
        }
    ]
    res_pendentes = analyze_tasks(apenas_pendentes)
    assert res_pendentes["total_tarefas"] == 1
    assert res_pendentes["total_concluidas"] == 0
    assert res_pendentes["tempo_medio_conclusao_horas"] == 0.0
    assert res_pendentes["taxa_atraso_percentual"] == 0.0


def test_cenario_4_excecao_dominio_e_atributos_invalidos():
    """Cenário 4: Exceção para Atributos e Domínios Inválidos (RN-06).

    Dado valores fora do domínio de prioridade/status ou títulos vazios
    Quando o analisador for executado
    Então deve disparar exceção de validação.
    """
    # Prioridade inválida
    prio_invalida = [
        {
            "id": 11,
            "titulo": "Prioridade customizada não permitida",
            "prioridade": "URGENTE",
            "data_criacao": "2026-03-01T08:00:00",
            "data_vencimento": "2026-03-02T08:00:00",
            "status": "PENDENTE",
        }
    ]
    with pytest.raises((TaskValidationError, ValueError)):
        analyze_tasks(prio_invalida)

    # Status inválido
    status_invalido = [
        {
            "id": 12,
            "titulo": "Status não reconhecido",
            "prioridade": "ALTA",
            "data_criacao": "2026-03-01T08:00:00",
            "data_vencimento": "2026-03-02T08:00:00",
            "status": "EM_ANDAMENTO",
        }
    ]
    with pytest.raises((TaskValidationError, ValueError)):
        analyze_tasks(status_invalido)