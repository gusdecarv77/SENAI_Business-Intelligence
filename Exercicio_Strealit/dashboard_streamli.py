# --- AULA 8: DASHBOARD PYTHON STREAMLIT ---
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Configuração da página (deve ser o primeiro comando do Streamlit) ---
st.set_page_config(layout="wide")

# --- Carregar os dados (Slide 12) ---
try:
    df = pd.read_csv("FinanciamentoPecuaria.csv", encoding='utf-8', sep=';')
except FileNotFoundError:
    st.error("❌ Erro: Arquivo 'FinanciamentoPecuaria.csv' não encontrado. Verifique se o arquivo está no diretório correto.")
    st.stop()
except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")
    st.stop()

# --- Limpeza Preventiva ---
# Remove espaços invisíveis nos nomes das colunas (MUITO importante para evitar erros de índice)
df.columns = df.columns.str.strip()

# --- Tratamento dos dados (Slide 13) ---
df = df.replace('-', '0')

# --- Tratamento dos dados: Identificar colunas de anos (numéricas) ---
# Pega apenas colunas que representam anos
colunas_anos = [col for col in df.columns if col.isnumeric()]

if not colunas_anos:
    st.error("❌ Nenhuma coluna de ano encontrada. Verifique o separador do seu CSV.")
    st.stop()

# --- Tratamento dos dados: Conversão para Float (Slide 16) ---
for col in colunas_anos:
    df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# --- Tratamento dos dados: Arredondamento (Slide 18) ---
df[colunas_anos] = df[colunas_anos].round(2)

# --- Tratamento dos dados: Média de Investimentos (Slide 19) ---
# AQUI ESTAVA O SEU ERRO ANTES. 
# O comando abaixo calcula a média já forçando ela a ser um número real (float) e arredondando na mesma linha.
df["Md_Invest"] = df[colunas_anos].mean(axis=1, numeric_only=True).astype(float).round(2)

# --- Tratamento dos dados: Linha de Média Geral (Slide 20) ---
mean_values = df[colunas_anos].mean()
media_geral_md = df[df["Localidade"] != "Média"]["Md_Invest"].mean()

# Criar linha média com tipos consistentes
nova_linha_dict = {"Localidade": "Média"}
for col in colunas_anos:
    nova_linha_dict[col] = mean_values[col]
nova_linha_dict["Md_Invest"] = media_geral_md

linha_media = pd.DataFrame([nova_linha_dict])
df = pd.concat([df, linha_media], ignore_index=True)

# Limpando espaços na localidade
df["Localidade"] = df["Localidade"].astype(str).str.strip()

# --- Estrutura inicial do Dashboard (Slide 21) ---
st.title('Dashboard Financeiro Agro Goiás 2014-2024')
st.write('Dashboard Financeiro - Tabela')
st.dataframe(df.style.format({'Md_Invest': '{:.2f}'}))

# --- Widgets de Seleção (Slide 23) ---
localidades = df.loc[df["Localidade"] != "Média", "Localidade"].unique().tolist()
opcoes_localidade = ["Todos"] + localidades
localidade_selecionada = st.sidebar.selectbox("Selecione a Localidade:", opcoes_localidade)

# --- Layout do Dashboard: Colunas (Slide 25) ---
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# --- Lógica da Coluna 1: Gráfico de Barras (Slide 26) ---
with col1:
    if localidade_selecionada == "Todos":
        df_plot = df[df["Localidade"] != "Média"]
        investimentos_ano = df_plot[colunas_anos].mean()
        st.write("### Média dos investimentos por ano (Todas as localidades):")
        st.bar_chart(pd.Series(investimentos_ano, index=colunas_anos))
    else:
        df_local = df[df["Localidade"] == localidade_selecionada]
        if not df_local.empty:
            investimentos_local = df_local.iloc[0][colunas_anos]
            st.write(f"Evolução dos investimentos para {localidade_selecionada}:")
            st.bar_chart(pd.Series(investimentos_local.values, index=colunas_anos))
        else:
            st.error("Nenhum dado encontrado para essa localidade.")

# --- Lógica da Coluna 2: Gráfico de Linhas (Slide 27) ---
with col2:
    st.write("### Gráfico de Linhas: Evolução dos Investimentos")
    if localidade_selecionada == "Todos":
        investimentos_ano_lin = df[df["Localidade"] != "Média"][colunas_anos].mean()
    else:
        investimentos_ano_lin = df[df["Localidade"] == localidade_selecionada].iloc[0][colunas_anos]
    st.line_chart(pd.Series(investimentos_ano_lin.values, index=colunas_anos))

# --- Lógica da Coluna 3: Comparação (Slide 28) ---
with col3:
    st.write("### Comparação da Cidade com a Média Geral")
    if localidade_selecionada != "Todos":
        df_local_comp = df[df["Localidade"] == localidade_selecionada]
        if not df_local_comp.empty:
            investimentos_local = df_local_comp.iloc[0][colunas_anos].values
            investimentos_media = df[df["Localidade"] != "Média"][colunas_anos].mean().values
            
            df_comparacao = pd.DataFrame({
                localidade_selecionada: investimentos_local,
                "Média Geral": investimentos_media
            }, index=colunas_anos)
            st.bar_chart(df_comparacao)
    else:
        st.info("Selecione uma localidade para visualizar a comparação.")

# --- Lógica da Coluna 4: KPI Ano Máximo (Slide 29) ---
with col4:
    st.write("### Ano com Maior Investimento")
    if localidade_selecionada != "Todos":
        df_local_kpi = df[df["Localidade"] == localidade_selecionada]
        if not df_local_kpi.empty:
            investimentos_local = df_local_kpi.iloc[0][colunas_anos]
            ano_max = investimentos_local.idxmax()
            valor_max = investimentos_local.max()
            st.metric(label="Ano com Maior Investimento", value=ano_max, delta=f"Valor: {valor_max:.2f}")
    else:
        st.info("Selecione uma localidade específica para visualizar o ano com maior investimento.")
