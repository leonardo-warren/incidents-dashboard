import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard de Incidentes", layout="wide")

st.title("Dashboard de Incidentes - Produto Digital (Junho/2025)")

# --- Carregamento dos dados ---
df = pd.read_csv("warren.csv")

# Padronização de colunas
df.rename(columns={
    "Issue Type": "Issue_Type",
    "Reporter": "Reporter",
    "Priority": "Priority",
    "Created": "Created",
    "Custom field (Segmento do cliente)": "Segmento",
    "Custom field (Produto afetado)": "Produto",
    "Labels": "Labels",
    "Labels.1": "Labels_1",
    "Labels.2": "Labels_2",
}, inplace=True)

# Parse de datas
df["Created"] = pd.to_datetime(df["Created"], format="%d/%b/%y %I:%M %p")

# Unindo labels em uma coluna só
df["All_Labels"] = df[["Labels", "Labels_1", "Labels_2"]].astype(str).agg(';'.join, axis=1)
df["All_Labels"] = df["All_Labels"].str.replace("nan;", "").str.replace(";nan", "").str.replace("nan", "")
df["All_Labels"] = df["All_Labels"].apply(lambda x: [l for l in x.split(";") if l])

# Sidebar: filtros opcionais
with st.sidebar:
    st.header("Filtros")
    tipos = st.multiselect("Issue Type", options=df["Issue_Type"].unique(), default=df["Issue_Type"].unique())
    prioridades = st.multiselect("Prioridade", options=df["Priority"].unique(), default=df["Priority"].unique())
    df = df[df["Issue_Type"].isin(tipos) & df["Priority"].isin(prioridades)]

# --- 1. Issue Type vs Reporter ---
st.subheader("1. Issue Type vs Reporter")
data1 = df.groupby(["Issue_Type", "Reporter"]).size().unstack(fill_value=0)
st.bar_chart(data1)

# --- 2. Issue Type vs Priority ---
st.subheader("2. Issue Type vs Priority")
data2 = df.groupby(["Issue_Type", "Priority"]).size().unstack(fill_value=0)
st.bar_chart(data2)

# --- 3. Issue Type vs Created (Linha temporal) ---
st.subheader("3. Issue Type vs Data de Criação")
df["Date"] = df["Created"].dt.date
data3 = df.groupby(["Date", "Issue_Type"]).size().unstack(fill_value=0)
st.line_chart(data3)

# --- 4. Issue Type vs Segmento do Cliente ---
st.subheader("4. Issue Type vs Segmento do Cliente")
data4 = df.groupby(["Issue_Type", "Segmento"]).size().unstack(fill_value=0)
st.bar_chart(data4)

# --- 5. Issue Type vs Produto Afetado ---
st.subheader("5. Issue Type vs Produto Afetado")
data5 = df.groupby(["Issue_Type", "Produto"]).size().unstack(fill_value=0)
st.bar_chart(data5)

# --- 6. Issue Type vs Labels ---
st.subheader("6. Issue Type vs Labels")
# Explodir labels
exploded = df.explode("All_Labels")
data6 = exploded.groupby(["Issue_Type", "All_Labels"]).size().unstack(fill_value=0)
st.bar_chart(data6)

# --- MoM: Redução de incidentes ---
st.subheader("Comparativo MoM (Maio x Junho)")
junho_incidentes = len(df)
maio_incidentes = st.number_input("Número de incidentes em Maio", min_value=0, value=266)
if maio_incidentes > 0:
    percent = (maio_incidentes - junho_incidentes) / maio_incidentes * 100
    st.metric("Redução (%) de incidentes Junho vs Maio", f"{percent:.2f}%")
else:
    st.warning("Informe o total de incidentes de maio para cálculo.")

# --- Projeção de Incidentes para Julho (dias úteis) ---
st.subheader("Projeção de Incidentes para Julho (até fim do mês)")

# Cálculo dias úteis em julho
ano = 2025
mes = 7
hoje = datetime.now()
# lista de todos os dias de julho
dias_julho = pd.date_range(start=f"{ano}-{mes:02d}-01", end=f"{ano}-{mes:02d}-31")
dias_uteis_julho = [d for d in dias_julho if d.weekday() < 5]
# média diária de incidentes em dias úteis de junho
dias_uteis_junho = df[df["Created"].dt.month == 6]["Created"].dt.date.nunique()
incidentes_uteis_junho = df[df["Created"].dt.month == 6].shape[0]
media_diaria = incidentes_uteis_junho / dias_uteis_junho if dias_uteis_junho else 0
proj_julho = int(round(media_diaria * len(dias_uteis_julho)))
st.write(f"Média diária de incidentes em junho: **{media_diaria:.2f}**")
st.write(f"Dias úteis em julho: **{len(dias_uteis_julho)}**")
st.metric("Projeção total para julho", proj_julho)

st.markdown("---")
st.caption("Dashboard desenvolvido pelo time de Produto Warren | Compartilhe esse link com seu time.")
