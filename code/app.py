import os
import streamlit as st
from dotenv import load_dotenv
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuración de entorno
load_dotenv()
token = os.getenv('BANXICO_TOKEN')

# Función para obtener series de Banxico
def get_banxico_series(series_id, start_date, end_date):
    url = f'https://www.banxico.org.mx/SieAPIRest/service/v1/series/{series_id}/datos/{start_date}/{end_date}'
    headers = {'Bmx-Token': token}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    df = pd.json_normalize(data['bmx'], record_path=['series', 'datos'])
    df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
    df['dato'] = pd.to_numeric(df['dato'], errors='coerce')
    return df.dropna().sort_values('fecha')

# Configuración general
st.set_page_config(layout="wide")
st.title("Tasa Real Ex-Ante y Reducción Esperada - API Banxico")

# Selectores de fecha
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Fecha de inicio", value=pd.to_datetime("2020-01-01"))
with col2:
    end_date = st.date_input("Fecha de fin", value=datetime.today())

start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# Series a consultar
series_ids = {
    'exp_inf_12m': 'SR14194',
    'tiie_1d': 'SF331451',
    'objetivo': 'SF61745',
    'cierre24': 'SR14680'
}

try:
    # Descargar series
    df_exp = get_banxico_series(series_ids['exp_inf_12m'], start_date_str, end_date_str)
    df_tiie = get_banxico_series(series_ids['tiie_1d'], start_date_str, end_date_str)
    df_obj = get_banxico_series(series_ids['objetivo'], start_date_str, end_date_str)
    df_cierre = get_banxico_series(series_ids['cierre24'], start_date_str, end_date_str)

    # Procesamiento
    df_exp['month'] = df_exp['fecha'] + pd.DateOffset(months=1)
    df_exp = df_exp.rename(columns={'dato': 'exp'})[['month', 'exp']]

    df_tiie['month'] = df_tiie['fecha'].dt.to_period('M').dt.to_timestamp()
    df_tiie = df_tiie.groupby('month')['dato'].mean().reset_index(name='tiieod')

    df_obj['month'] = df_obj['fecha'].dt.to_period('M').dt.to_timestamp()
    df_obj = df_obj.groupby('month')['dato'].mean().reset_index(name='objetivo')

    dfF = pd.merge(df_tiie, df_exp, on='month', how='left')
    dfF['exp'] = dfF['exp'].fillna(method='ffill')
    dfF['exante'] = dfF['tiieod'] - dfF['exp']
    dfF['date'] = dfF['month']
    dfF = dfF.dropna()

    df_cierre = df_cierre.rename(columns={'dato': 'Cierre24'})
    df_cierre['month'] = df_cierre['fecha'] + pd.DateOffset(months=1)

    df_obj_cierre = pd.merge(df_obj, df_cierre[['month', 'Cierre24']], on='month', how='left')
    df_obj_cierre['Diff'] = df_obj_cierre['objetivo'] - df_obj_cierre['Cierre24']
    df_obj_cierre = df_obj_cierre.sort_values('month')
    ultima = df_obj_cierre.dropna(subset=['Diff']).tail(1).copy()
    ultima['NumJuntas'] = 5
    ultima['downavg'] = ultima['Diff'] / ultima['NumJuntas']

    # Gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=dfF, x='date', y='exante', ax=ax, label='Tasa Real Ex-Ante', linewidth=2, color='#00BFC4')
    ax.scatter(dfF['date'], dfF['exante'], color='#F8766D', s=25)
    ax.axhline(y=1.8, linestyle='--', color='blue', linewidth=1, label='1.8% Neutral')
    ax.axhline(y=2.6, linestyle='--', color='green', linewidth=1, label='2.6% Neutral')
    ax.axhline(y=3.4, linestyle='--', color='red', linewidth=1, label='3.4% Neutral')
    ax.set_title("Tasa Real Ex-Ante", fontsize=14)
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Tasa (%)")
    ax.legend()
    st.pyplot(fig)

    # 🔘 Botón para descargar CSV
    st.subheader("📥 Descargar datos de tasa ex-ante")
    csv = dfF.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name='tasa_real_ex_ante.csv',
        mime='text/csv'
    )

    # 📊 Reducción esperada promedio
    st.subheader("📉 Reducción esperada promedio por junta")
    st.dataframe(ultima[['month', 'objetivo', 'Cierre24', 'Diff', 'NumJuntas', 'downavg']])

except Exception as e:
    st.error(f"❌ Error: {e}")
