# download-qflow-data.py
# Version 1.0.2 - Changed price files location to "price_data" folder
# 2025-08-24

import requests
import pandas as pd
import os
from datetime import datetime

BASE = "https://api.geckoterminal.com/api/v2"
POOL = "2utzyuC6hzPXyzMAW9dNhr3oB11H2GLkrfCsdMfKMp6r"
CSV_FILE = os.path.join("price_data", "qflow_price_history.csv")

def get_qflow_history(pool_address, network="solana", timeframe="day"):
    url = f"{BASE}/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}"
    print("A consultar:", url)
    r = requests.get(url)
    if r.status_code != 200:
        print("Erro HTTP", r.status_code, r.text)
        return None
    
    resp = r.json().get("data", {})
    ohlcv = resp.get("attributes", {}).get("ohlcv_list", [])
    if not ohlcv:
        print("Sem dados OHLCV.")
        return None
    
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    # Correção: Manter como datetime completo, não converter para date
    df["date"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df[["date", "close"]].rename(columns={"close": "price"})
    return df

# Obter novos dados
df_new = get_qflow_history(POOL)
if df_new is None:
    print("❌ Falhou ao obter novos dados.")
    exit()

# Verificar se ficheiro já existe
if os.path.exists(CSV_FILE):
    df_old = pd.read_csv(CSV_FILE, parse_dates=["date"])
    last_date = df_old["date"].max()
    
    # Correção: Comparar datetime com datetime
    df_new = df_new[df_new["date"] > last_date]
    
    if df_new.empty:
        print("⚠️ Nenhum dado novo a adicionar.")
    else:
        df_updated = pd.concat([df_old, df_new], ignore_index=True)
        df_updated = df_updated.drop_duplicates(subset="date").sort_values("date")
        df_updated.to_csv(CSV_FILE, index=False)
        print(f"✅ Adicionados {len(df_new)} novos registos. Atualizado {CSV_FILE}.")
else:
    df_new.to_csv(CSV_FILE, index=False)
    print("✅ Ficheiro criado com dados iniciais:", CSV_FILE)