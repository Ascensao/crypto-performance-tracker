# download-multi-crypto-data.py
# Version 1.0.2 - Changed proce files location to "price_data" folder

import requests
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

def get_hist_coingecko(coin_id, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        print(f"Erro ao obter dados para {coin_id}: {r.status_code}")
        return None
    data = r.json()
    df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
    # Manter como datetime, não converter para date aqui
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df[['date', 'price']].drop_duplicates(subset='date')
    return df

coins = {
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "solana": "solana"
}

for nome, coin_id in coins.items():
    file_name = os.path.join("price_data", f"{nome}_price_history.csv")
    
    # Verificar se o CSV já existe
    if os.path.exists(file_name):
        df_old = pd.read_csv(file_name, parse_dates=["date"])
        last_date = df_old["date"].max()
        
        # Correção 1: Usar datetime.now(timezone.utc) em vez de datetime.utcnow()
        # Correção 2: Comparar datetime com datetime (não date com date)
        current_datetime = pd.Timestamp.now(tz='UTC').tz_localize(None)
        delta = (current_datetime - last_date).days + 2
        
        print(f"🔄 A atualizar {nome} desde {last_date.date()} (+{delta} dias)")
        df_new = get_hist_coingecko(coin_id, days=delta)
        
        if df_new is not None:
            # Filtrar dados novos usando datetime completo
            df_new = df_new[df_new["date"] > last_date]
            if df_new.empty:
                print(f"⚠️ Nenhum dado novo para {nome}.")
                continue
            
            # Concatenar e remover duplicados
            df_all = pd.concat([df_old, df_new], ignore_index=True)
            df_all = df_all.drop_duplicates(subset="date").sort_values("date")
            df_all.to_csv(file_name, index=False)
            print(f"✅ Atualizado: {file_name} com {len(df_new)} novos dias.")
    
    else:
        # Primeiro download completo
        print(f"📥 Criar histórico inicial de {nome}")
        df = get_hist_coingecko(coin_id, days=120)
        if df is not None:
            df.to_csv(file_name, index=False)
            print(f"✅ Guardado: {file_name}")