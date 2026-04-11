import pandas as pd
import matplotlib.pyplot as plt

# =============================================================================
# EXTRAÇÃO E TRANSFORMAÇÃO DE DADOS (ETL)
# Fonte: Dados Abertos TSE - Perfil do Eleitorado Atual (Goiás)
# =============================================================================

# Leitura do dataset
df_tse = pd.read_csv('perfil_eleitor_secao_ATUAL_GO.csv', sep=';', encoding='latin1')

# Padronização dos nomes das colunas para uppercase (evitar erros de case-sensitivity)
df_tse.columns = df_tse.columns.str.upper()

# Filtro geográfico: delimitando para o estado de GO e as cidades em análise
df_go = df_tse[df_tse['SG_UF'] == 'GO'] if 'SG_UF' in df_tse.columns else df_tse
cidades_alvo = ['GOIÂNIA', 'ANÁPOLIS']
df_filtrado = df_go[df_go['NM_MUNICIPIO'].isin(cidades_alvo)].copy()

# =============================================================================
# ANÁLISE EXPLORATÓRIA DE DADOS (EDA)
# =============================================================================

print("\n--- Estrutura do Dataset ---")
print(df_filtrado[['NM_MUNICIPIO', 'DS_GRAU_INSTRUCAO', 'QT_ELEITORES']].info())

print("\n--- Verificando Valores Nulos ---")
print(df_filtrado[['NM_MUNICIPIO', 'DS_GRAU_INSTRUCAO', 'QT_ELEITORES']].isnull().sum())

# =============================================================================
# MODELAGEM DE DADOS PARA BI
# =============================================================================

# 1. Agrupamento do total geral de eleitores por município
total_por_cidade = df_filtrado.groupby('NM_MUNICIPIO')['QT_ELEITORES'].sum().reset_index()
total_por_cidade.rename(columns={'QT_ELEITORES': 'Total_Eleitores'}, inplace=True)

# 2. Segmentação de eleitores com acesso ao Ensino Superior (Completo e Incompleto)
filtro_superior = df_filtrado['DS_GRAU_INSTRUCAO'].str.contains('SUPERIOR', na=False, case=False)
superior_por_cidade = df_filtrado[filtro_superior].groupby('NM_MUNICIPIO')['QT_ELEITORES'].sum().reset_index()
superior_por_cidade.rename(columns={'QT_ELEITORES': 'Eleitores_Superior'}, inplace=True)

# 3. Merge das tabelas agregadas para cálculo dos indicadores
df_kpi = pd.merge(total_por_cidade, superior_por_cidade, on='NM_MUNICIPIO')

# =============================================================================
# CÁLCULO DE INDICADORES (KPIs ESTRATÉGICOS)
# =============================================================================

# KPI 1: Índice de Formação Superior (IFS) - Percentual
df_kpi['KPI_1_IFS_Percentual'] = (df_kpi['Eleitores_Superior'] / df_kpi['Total_Eleitores']) * 100

# KPI 2: Gap de Formação (Volume absoluto de eleitores sem diploma superior)
df_kpi['KPI_2_Gap_Formacao_Absoluto'] = df_kpi['Total_Eleitores'] - df_kpi['Eleitores_Superior']

# KPI 3: Densidade (Proporção de formação superior a cada 10 mil habitantes)
df_kpi['KPI_3_Superior_por_10k'] = (df_kpi['Eleitores_Superior'] / df_kpi['Total_Eleitores']) * 10000

print("\n--- Resultados Estratégicos (KPIs) ---")
print(df_kpi.round(2)) 

# =============================================================================
# VISUALIZAÇÃO DE DADOS (DATA STORYTELLING)
# =============================================================================

## Configuração do Gráfico Comparativo para o KPI 1: Índice de Formação Superior (IFS) - Percentual
plt.figure(figsize=(8, 5))
cores = ['#2c3e50', '#e74c3c'] 
grafico = plt.bar(df_kpi['NM_MUNICIPIO'], df_kpi['KPI_1_IFS_Percentual'], color=cores)

plt.title('KPI 1: % da População com Acesso ao Ensino Superior\n(Goiânia x Anápolis)', fontsize=14)
plt.ylabel('Percentual (%)', fontsize=12)

# Inserção dos rótulos de dados (data labels) sobre as barras
for bar in grafico:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Limpeza visual (remoção das bordas superior e direita para um design mais limpo)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)

plt.show()

## Configuração do Gráfico Comparativo para o KPI 2: Gap de Formação (Volume absoluto de eleitores sem diploma superior)
plt.figure(figsize=(8, 5))
cores_gap = ['#3498db', '#9b59b6']
grafico_gap = plt.bar(df_kpi['NM_MUNICIPIO'], df_kpi['KPI_2_Gap_Formacao_Absoluto'], color=cores_gap)
plt.title('KPI 2: Gap de Formação (Eleitores sem Ensino Superior)\n(Goiânia x Anápolis)', fontsize=14)
plt.ylabel('Número de Eleitores', fontsize=12)
# Inserção dos rótulos de dados (data labels) sobre as barras
for bar in grafico_gap:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + (yval * 0.02), f'{int(yval):_}'.replace('_', '.'), ha='center', va='bottom', fontsize=11, fontweight='bold')    
# Limpeza visual (remoção das bordas superior e direita para um design mais limpo)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.show()

## Configuração do Gráfico Comparativo para o KPI 3: Densidade de Eleitores com Ensino Superior por 10k Habitantes
plt.figure(figsize=(8, 5))
cores_densidade = ['#1abc9c', '#f39c12']
grafico_densidade = plt.bar(df_kpi['NM_MUNICIPIO'], df_kpi['KPI_3_Superior_por_10k'], color=cores_densidade)
plt.title('KPI 3: Densidade de Eleitores com Ensino Superior por 10k Habitantes\n(Goiânia x Anápolis)', fontsize=14)
plt.ylabel('Número de Eleitores por 10k Habitantes', fontsize=12)
# Inserção dos rótulos de dados (data labels) sobre as barras
for bar in grafico_densidade:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
# Limpeza visual (remoção das bordas superior e direita para um design mais limpo)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.show()

## Fim
