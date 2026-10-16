# Especificação SDD e Contrato de Interface - TaskAnalyzer

## 1. Identificação do Projeto
- **Estudante:** Diogo Lucas Sobreira de Lucena
- **Curso:** Ciência da Computação (Polo Asa Norte - B)
- **E-mail:** diogolucasdelucena@sempreceub.com

## 2. Contrato de Entrada e Saída
### Inputs (Tarefas)
- `id` (str/int): Identificador único.
- `titulo` (str): Não vazio.
- `prioridade` (str): Domain {"BAIXA", "MEDIA", "ALTA"}.
- `data_criacao` (str/datetime): ISO 8601.
- `data_vencimento` (str/datetime): ISO 8601.
- `data_conclusao` (str/datetime/Nullable): Obrigatório se status == "CONCLUIDA".
- `status` (str): Domain {"PENDENTE", "CONCLUIDA", "CANCELADA"}.

### Outputs (Relatório Consolidade)
- `total_tarefas` (int)
- `total_concluidas` (int)
- `total_atrasadas` (int)
- `tempo_medio_conclusao_horas` (float)
- `taxa_atraso_percentual` (float)
- `metricas_por_prioridade` (dict[str, dict])

## 3. Regras de Negócio
- **RN-01:** Apenas tarefas com status "CONCLUIDA" entram no tempo médio.
- **RN-02:** Duração = (data_conclusao - data_criacao) em horas decimais.
- **RN-03:** Atraso se data_conclusao > data_vencimento em concluídas.
- **RN-04:** data_conclusao >= data_criacao. Se menor, dispara TaskValidationError / ValueError.
- **RN-05:** Entradas sem concluídas retornam 0.0/0 sem erro de divisão por zero.
- **RN-06:** Domínios fora da especificação disparam TaskValidationError / ValueError.