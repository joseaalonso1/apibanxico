import os
from dotenv import load_dotenv
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar token desde .env
load_dotenv()
token = os.getenv('BANXICO_TOKEN')

# Función de descarga
def get_banxico_series(series_id, start_date, end_date):
    url = f'https://www.banxico.org.mx/SieAPIRest/service/v1/series/{series_id}/datos/{start_date}/{end_date}'
    headers = {'Bmx-Token': token}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    df = pd.json_normalize(data['bmx'], record_path=['series', 'datos'])
    df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
    df['dato'] = pd.to_numeric(df['dato'], errors='coerce')
    df = df.dropna().sort_values('fecha')
    print(f"✅ {series_id} descargada correctamente con {len(df)} registros")
    return df

# Fechas y series
start_date = '2020-01-01'
end_date = '2024-06-13'
series_ids = {
    'exp_inf_12m': 'SR14194',
    'tiie_1d': 'SF331451',
    'objetivo': 'SF61745',
    'cierre24': 'SR14680'
}

# Descarga
df_exp = get_banxico_series(series_ids['exp_inf_12m'], start_date, end_date)
df_tiie = get_banxico_series(series_ids['tiie_1d'], start_date, end_date)
df_obj = get_banxico_series(series_ids['objetivo'], start_date, end_date)
df_cierre = get_banxico_series(series_ids['cierre24'], start_date, end_date)

# Procesamiento de tasa ex-ante
df_exp['month'] = df_exp['fecha'] + pd.DateOffset(months=1)
df_exp = df_exp.rename(columns={'dato': 'exp'})[['month', 'exp']]

df_tiie['month'] = df_tiie['fecha'].dt.to_period('M').dt.to_timestamp()
df_tiie = df_tiie.groupby('month')['dato'].mean().reset_index(name='tiieod')

df_obj['month'] = df_obj['fecha'].dt.to_period('M').dt.to_timestamp()
df_obj = df_obj.groupby('month')['dato'].mean().reset_index(name='objetivo')

dfF = pd.merge(df_tiie, df_exp, on='month', how='left')
dfF = dfF.sort_values('month')
dfF['exp'] = dfF['exp'].fillna(method='ffill')
dfF['exante'] = dfF['tiieod'] - dfF['exp']
dfF = dfF.dropna(subset=['exante'])
dfF['date'] = dfF['month']

# Gráfico de ex-ante
sns.set_theme(style="whitegrid")
plt.figure(figsize=(12, 6))
plt.plot(dfF['date'], dfF['exante'], color="#00BFC4", linewidth=2, label='Tasa Real Ex-Ante')
plt.scatter(dfF['date'], dfF['exante'], color="#F8766D", s=30)
plt.axhline(y=1.8, linestyle='--', color='blue', linewidth=1, label='1.8% Neutral')
plt.axhline(y=2.6, linestyle='--', color='green', linewidth=1, label='2.6% Neutral')
plt.axhline(y=3.4, linestyle='--', color='red', linewidth=1, label='3.4% Neutral')
plt.title("Short-Term Ex-Ante Real Rate", fontsize=14, fontweight='bold')
plt.xlabel("Fecha", fontsize=12)
plt.ylabel("Tasa Ex-Ante (%)", fontsize=12)
plt.xticks(rotation=90)
plt.legend()
plt.tight_layout()
plt.show()

# Cierre esperado 2024: procesamiento
df_cierre = df_cierre.rename(columns={'dato': 'Cierre24'})
df_cierre['month'] = df_cierre['fecha'] + pd.DateOffset(months=1)

# Unión con objetivo
df_obj_cierre = pd.merge(df_obj, df_cierre[['month', 'Cierre24']], on='month', how='left')
df_obj_cierre['Diff'] = df_obj_cierre['objetivo'] - df_obj_cierre['Cierre24']
df_obj_cierre = df_obj_cierre.sort_values('month')

# Cálculo final: reducción promedio
ultima = df_obj_cierre.dropna(subset=['Diff']).tail(1).copy()
ultima['NumJuntas'] = 5
ultima['downavg'] = ultima['Diff'] / ultima['NumJuntas']

# Resultado
print("\n📉 Reducción esperada promedio por junta:\n")
print(ultima[['month', 'objetivo', 'Cierre24', 'Diff', 'NumJuntas', 'downavg']])
