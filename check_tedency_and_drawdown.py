import pandas as pd
import matplotlib.pyplot as plt
import os

# ──────────── Selecionar ficheiro ────────────
print("Ficheiros disponíveis:")
files = [f for f in os.listdir() if f.endswith("_price_history.csv")]
for i, file in enumerate(files):
    print(f"{i + 1}: {file}")

choice = input("Escolhe um número: ")
try:
    selected_file = files[int(choice) - 1]
except:
    print("❌ Escolha inválida.")
    exit()

# ──────────── Carregar dados ────────────
df = pd.read_csv(selected_file, parse_dates=["date"])
df = df.set_index("date").sort_index()

if df["price"].isnull().all():
    print("❌ Nenhum dado válido.")
    exit()

# ──────────── Escolher intervalo de datas ────────────
print(f"\nIntervalo disponível: {df.index.min().date()} → {df.index.max().date()}")
start_date = input("Data inicial (YYYY-MM-DD): ")
end_date = input("Data final   (YYYY-MM-DD): ")

try:
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    df = df.loc[start_date:end_date]
except:
    print("❌ Datas inválidas ou fora do intervalo.")
    exit()

if df.empty:
    print("❌ Sem dados neste intervalo.")
    exit()

# ──────────── Calcular métricas ────────────
df["peak"] = df["price"].cummax()
df["drawdown"] = (df["price"] - df["peak"]) / df["peak"] * 100

# ──────────── Preparar linha de tendência com base em preços ────────────
start = df.index[0]
end = df["price"].idxmax()
start_val = df["price"].iloc[0]
end_val = df["price"].max()

# Linha de tendência baseada em slope ideal até ao ATH
trendline = pd.Series(
    index=df.index,
    data=(df.index - start).days * (end_val - start_val) / (end - start).days + start_val
)

# Calcular retorno percentual da tendência
trend_return_pct = ((end_val / start_val) - 1) * 100

# ──────────── Criar gráfico com subplots ────────────
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

# ──────────── Gráfico 1: Preço + linha tendência ────────────
asset_name = selected_file.replace("_price_history.csv", "").capitalize()
ax1.plot(df.index, df["price"], label="Price", color='white', linewidth=2)
ax1.plot(df.index, trendline, color='red', linestyle='--', linewidth=1.5, label=f"Trend to ATH (${end_val:.4f})")

# Anotar o retorno da linha de tendência no fim
#ax1.text(
    #df.index[-1], trendline.iloc[-1] + (df["price"].max() * 0.02),  # offset para cima
    #f"{trend_return_pct:+.2f}%",
    #color='red', fontsize=11, fontweight='bold',
    #ha='left', va='bottom'
#)

ax1.set_ylabel("Price (USD)")
ax1.set_title(f"{asset_name} - Price with Trend to ATH")
ax1.legend()
ax1.grid(True, linestyle="--", alpha=0.3)

# ──────────── Gráfico 2: Drawdown ────────────
ax2.fill_between(df.index, df["drawdown"], 0, where=(df["drawdown"] < 0), color='red', alpha=0.7)
ax2.set_ylabel("Drawdown (%)")
ax2.set_xlabel("Date")
ax2.set_title("Drawdown")
ax2.grid(True, linestyle="--", alpha=0.3)

plt.tight_layout()
plt.show()
