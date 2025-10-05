
"""
simulador_smart_office.py
-------------------------
Gera dados simulados de sensores para o projeto Smart Office.

Requisitos atendidos:
- 3 tipos de sensores: temperatura (°C), luminosidade (lux) e ocupacao (0/1)
- Período de 7 dias, registros a cada 15 minutos
- Variação lógica: noite mais fria, luminosidade ~0 à noite, maior ocupação no horário comercial
- Colunas: timestamp (YYYY-MM-DD HH:MM), sensor_id, tipo, valor
- Saída: smart_office_data.csv no mesmo diretório do script
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# ---------- Parâmetros gerais ----------
SEED = 42
np.random.seed(SEED)

# Janela de simulação (7 dias, 15 min)
start_date = datetime(2025, 10, 1, 0, 0, 0)
end_date = start_date + timedelta(days=7)
freq_minutes = 15

# Sensores (3 por tipo para parecer mais realista)
temp_sensors = ["T01", "T02", "T03"]
light_sensors = ["L01", "L02", "L03"]
occ_sensors = ["O01", "O02", "O03"]

# Gera a grade temporal
timestamps = pd.date_range(start=start_date, end=end_date, freq=f"{freq_minutes}min", inclusive="left")

registros = []

for ts in timestamps:
    dow = ts.weekday()  # 0 = segunda ... 6 = domingo
    hour = ts.hour

    # Flags de período
    is_day = 7 <= hour <= 18
    is_business = 8 <= hour <= 18 and dow < 5  # horário comercial em dias úteis

    # --------- Temperatura (°C) ---------
    # Base mais alta de dia, mais baixa à noite; pequena sazonalidade aleatória
    base_temp = 23.0 if is_day else 20.0
    for sid in temp_sensors:
        temp = np.random.normal(loc=base_temp, scale=0.8)
        registros.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
            "sensor_id": sid,
            "tipo": "temperatura",
            "valor": round(float(temp), 2)
        })

    # --------- Luminosidade (lux) ---------
    # De noite ~0; de dia média 550–650 com ruído
    base_lux = 0.0 if not is_day else np.random.normal(loc=600, scale=80)
    base_lux = max(0.0, base_lux)
    for sid in light_sensors:
        lux = max(0.0, np.random.normal(loc=base_lux, scale=50))
        registros.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
            "sensor_id": sid,
            "tipo": "luminosidade",
            "valor": round(float(lux), 2)
        })

    # --------- Ocupação (0/1) ---------
    # Dias úteis em horário comercial: prob. alta de 1; fora disso, prob. baixa
    if is_business:
        p_occ = 0.8
    elif dow < 5 and (7 <= hour < 8 or 18 < hour <= 20):
        p_occ = 0.3  # transição/limpeza
    else:
        p_occ = 0.05  # madrugada e fins de semana

    for sid in occ_sensors:
        occ = 1 if np.random.rand() < p_occ else 0
        registros.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
            "sensor_id": sid,
            "tipo": "ocupacao",
            "valor": int(occ)
        })

df = pd.DataFrame(registros, columns=["timestamp", "sensor_id", "tipo", "valor"])

# Garante ordenação consistente
df.sort_values(["timestamp", "sensor_id", "tipo"], inplace=True)
df.reset_index(drop=True, inplace=True)

# Salva CSV no mesmo diretório
out_path = os.path.join(os.path.dirname(__file__), "smart_office_data.csv")
df.to_csv(out_path, index=False)
print(f"Gerado: {out_path}  | Linhas: {len(df)}")
