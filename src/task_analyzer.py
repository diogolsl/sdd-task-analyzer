"""Módulo de processamento de métricas e análise de tarefas do TaskAnalyzer.

Este módulo implementa o contrato SDD para cálculo de tempos médios,
taxas de atraso e agrupamento de estatísticas por prioridade.
"""

from datetime import datetime
from typing import Any, Dict, List, Union


class TaskValidationError(ValueError):
    """Exceção customizada disparada quando ocorre inconsistência nas regras de negócio/contrato."""

    pass


def _parse_datetime(dt_val: Union[str, datetime], field_name: str) -> datetime:
    """Converte valores em string ISO 8601 ou mantém instâncias válidas de datetime.

    Args:
        dt_val (Union[str, datetime]): Valor a ser convertido.
        field_name (str): Nome do campo para contexto em mensagens de erro.

    Returns:
        datetime: Objeto datetime parseado.

    Raises:
        TaskValidationError: Se a data estiver em formato inválido ou tipo inadequado.
    """
    if isinstance(dt_val, datetime):
        return dt_val
    if isinstance(dt_val, str):
        try:
            # Suporta formato ISO 8601 incluindo sufixo Z
            return datetime.fromisoformat(dt_val.replace("Z", "+00:00"))
        except ValueError as exc:
            raise TaskValidationError(
                f"O campo '{field_name}' possui formato de data ISO 8601 inválido: '{dt_val}'."
            ) from exc
    raise TaskValidationError(
        f"O campo '{field_name}' deve ser uma string ISO 8601 ou objeto datetime."
    )


def analyze_tasks(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Processa uma lista de tarefas e gera indicadores consolidados de desempenho.

    Args:
        tasks (List[Dict[str, Any]]): Lista de dicionários representando as tarefas.

    Returns:
        Dict[str, Any]: Dicionário com totais, médias de tempo, taxas de atraso e detalhamento por prioridade.

    Raises:
        TaskValidationError: Se houver campos ausentes, domínios inválidos ou incoerência temporal.
    """
    valid_priorities = {"BAIXA", "MEDIA", "ALTA"}
    valid_statuses = {"PENDENTE", "CONCLUIDA", "CANCELADA"}

    total_tarefas = len(tasks)
    total_concluidas = 0
    total_atrasadas = 0
    duracoes_concluidas_horas: List[float] = []

    metricas_por_prioridade: Dict[str, Dict[str, Union[int, float]]] = {
        p: {
            "total_tarefas": 0,
            "total_concluidas": 0,
            "total_atrasadas": 0,
            "tempo_medio_conclusao_horas": 0.0,
            "taxa_atraso_percentual": 0.0,
        }
        for p in ["BAIXA", "MEDIA", "ALTA"]
    }

    duracoes_por_prioridade: Dict[str, List[float]] = {
        p: [] for p in ["BAIXA", "MEDIA", "ALTA"]
    }

    for idx, task in enumerate(tasks):
        # Validação de campos obrigatórios gerais
        required_fields = ["id", "titulo", "prioridade", "data_criacao", "data_vencimento", "status"]
        for field in required_fields:
            if field not in task or task[field] is None:
                raise TaskValidationError(
                    f"A tarefa no índice {idx} não contém o campo obrigatório '{field}'."
                )

        # Validação do título
        if not str(task["titulo"]).strip():
            raise TaskValidationError(f"A tarefa no índice {idx} (ID: {task['id']}) contém título vazio.")

        # Validação de domínio de prioridade
        prio = str(task["prioridade"]).upper()
        if prio not in valid_priorities:
            raise TaskValidationError(
                f"Prioridade inválida '{prio}' na tarefa ID {task['id']}. Domínio permitido: {sorted(valid_priorities)}"
            )

        # Validação de domínio de status
        status = str(task["status"]).upper()
        if status not in valid_statuses:
            raise TaskValidationError(
                f"Status inválido '{status}' na tarefa ID {task['id']}. Domínio permitido: {sorted(valid_statuses)}"
            )

        dt_criacao = _parse_datetime(task["data_criacao"], "data_criacao")
        dt_vencimento = _parse_datetime(task["data_vencimento"], "data_vencimento")

        metricas_por_prioridade[prio]["total_tarefas"] += 1

        if status == "CONCLUIDA":
            if "data_conclusao" not in task or task["data_conclusao"] is None:
                raise TaskValidationError(
                    f"A tarefa concluída ID {task['id']} deve conter o campo 'data_conclusao'."
                )

            dt_conclusao = _parse_datetime(task["data_conclusao"], "data_conclusao")

            # RN-04: Coerência Temporal (data_conclusao não pode ser anterior a data_criacao)
            if dt_conclusao < dt_criacao:
                raise TaskValidationError(
                    f"Incoerência temporal na tarefa ID {task['id']}: "
                    f"data_conclusao ({dt_conclusao}) é anterior à data_criacao ({dt_criacao})."
                )

            duracao_horas = (dt_conclusao - dt_criacao).total_seconds() / 3600.0
            duracoes_concluidas_horas.append(duracao_horas)
            duracoes_por_prioridade[prio].append(duracao_horas)

            total_concluidas += 1
            metricas_por_prioridade[prio]["total_concluidas"] += 1

            # RN-03: Critério de Atraso
            if dt_conclusao > dt_vencimento:
                total_atrasadas += 1
                metricas_por_prioridade[prio]["total_atrasadas"] += 1

    # RN-05: Tratamento de Entrada Vazia ou Sem Tarefas Concluidas (Prevenção de Divisão por Zero)
    tempo_medio = (
        round(sum(duracoes_concluidas_horas) / len(duracoes_concluidas_horas), 2)
        if total_concluidas > 0
        else 0.0
    )
    taxa_atraso = (
        round((total_atrasadas / total_concluidas) * 100.0, 2)
        if total_concluidas > 0
        else 0.0
    )

    # Cálculo dos indicadores por prioridade
    for prio in ["BAIXA", "MEDIA", "ALTA"]:
        p_concluidas = int(metricas_por_prioridade[prio]["total_concluidas"])
        p_atrasadas = int(metricas_por_prioridade[prio]["total_atrasadas"])
        p_duracoes = duracoes_por_prioridade[prio]

        p_tempo_medio = (
            round(sum(p_duracoes) / len(p_duracoes), 2)
            if p_concluidas > 0
            else 0.0
        )
        p_taxa_atraso = (
            round((p_atrasadas / p_concluidas) * 100.0, 2)
            if p_concluidas > 0
            else 0.0
        )

        metricas_por_prioridade[prio]["tempo_medio_conclusao_horas"] = p_tempo_medio
        metricas_por_prioridade[prio]["taxa_atraso_percentual"] = p_taxa_atraso

    return {
        "total_tarefas": total_tarefas,
        "total_concluidas": total_concluidas,
        "total_atrasadas": total_atrasadas,
        "tempo_medio_conclusao_horas": tempo_medio,
        "taxa_atraso_percentual": taxa_atraso,
        "metricas_por_prioridade": metricas_por_prioridade,
    }