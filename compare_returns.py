import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import glob
import os

# ──────────── 📆 INPUT ────────────
start_date = input("Start date (YYYY-MM-DD): ")
end_date = input("End date (YYYY-MM-DD): ")

try:
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
except:
    print("❌ Invalid date format.")
    exit()

# ──────────── 📁 LER DADOS ────────────
files = glob.glob("*_price_history.csv")
if not files:
    print("❌ No CSV files found.")
    exit()

all_returns = {}
summary = []

# ──────────── MÉTRICAS ────────────
def calculate_drawdown(series):
    peak = series.cummax()
    drawdown = (series - peak) / peak
    return drawdown.min() * 100  # em %

def calculate_sharpe(series):
    daily_ret = series.pct_change().dropna()
    if daily_ret.std() == 0:
        return 0
    sharpe = (daily_ret.mean() / daily_ret.std()) * np.sqrt(365)
    return sharpe

# ──────────── PROCESSAR ATIVOS ────────────
for file in files:
    try:
        df = pd.read_csv(file, parse_dates=["date"])
        df = df.set_index("date").sort_index()

        name = os.path.basename(file).replace("_price_history.csv", "").capitalize()

        full_range = pd.date_range(start=start_date, end=end_date, freq='D')
        df = df.reindex(full_range, method='ffill')
        df = df.loc[start_date:end_date]

        if df.empty or df["price"].isnull().all():
            print(f"⚠️ No valid data for {name}")
            continue

        start_price = df["price"].iloc[0]
        end_price = df["price"].iloc[-1]
        return_pct = ((end_price / start_price) - 1) * 100
        max_price = df["price"].max()
        max_ret = ((max_price / start_price) - 1) * 100
        drawdown = calculate_drawdown(df["price"])
        sharpe = calculate_sharpe(df["price"])

        df["return"] = (df["price"] / start_price - 1) * 100
        all_returns[name] = df["return"]

        summary.append(
            f"{name}: ${start_price:.4f} → ${end_price:.4f} ({return_pct:+.2f}%) | "
            f"Max return: {max_ret:.2f}% | Max Drawdown: {drawdown:.2f}% | Sharpe: {sharpe:.2f}"
        )

    except Exception as e:
        print(f"Erro ao processar {file}: {e}")

# ──────────── RESUMO NO TERMINAL ────────────
print("\n📈 Performance Summary:\n")

# Cabeçalho
print(
    f"{'Asset':<10} | {'Start Price':>12} | {'End Price':>12} | {'Return':>8} | "
    f"{'Max Return':>11} | {'Max DD':>9} | {'Sharpe':>7}"
)
print("-" * 80)

# Linhas
for file in files:
    try:
        name = os.path.basename(file).replace("_price_history.csv", "").capitalize()
        if name not in all_returns:
            continue

        df = pd.read_csv(file, parse_dates=["date"]).set_index("date").sort_index()
        df = df.loc[start_date:end_date]
        df = df.ffill()

        start_price = df["price"].iloc[0]
        end_price = df["price"].iloc[-1]
        return_pct = ((end_price / start_price) - 1) * 100
        max_price = df["price"].max()
        max_ret = ((max_price / start_price) - 1) * 100
        drawdown = calculate_drawdown(df["price"])
        sharpe = calculate_sharpe(df["price"])

        print(
            f"{name:<10} | "
            f"${start_price:>11.4f} | "
            f"${end_price:>11.4f} | "
            f"{return_pct:>7.2f}% | "
            f"{max_ret:>10.2f}% | "
            f"{drawdown:>8.2f}% | "
            f"{sharpe:>6.2f}"
        )

    except Exception as e:
        continue

# ──────────── GRÁFICO ────────────
if not all_returns:
    print("❌ No valid data to plot.")
    exit()

returns_df = pd.DataFrame(all_returns)
returns_df.index.name = "Date"

# Estilo escuro
plt.style.use('dark_background')
mpl.rcParams.update({
    'axes.facecolor': '#1e1e1e',
    'figure.facecolor': '#1e1e1e',
    'axes.edgecolor': '#cccccc',
    'axes.labelcolor': '#ffffff',
    'text.color': '#ffffff',
    'xtick.color': '#aaaaaa',
    'ytick.color': '#aaaaaa',
    'grid.color': '#444444',
    'axes.titleweight': 'bold',
    'axes.titlesize': 16,
    'axes.labelsize': 12,
    'legend.fontsize': 10,
    'font.size': 11,
    'lines.linewidth': 2.2
})

# Cores definidas por ativo
custom_colors = {
    "Bitcoin": "#ff4d4d",   # vermelho
    "Ethereum": "#32cd32",  # verde
    "Solana": "#1e90ff",    # azul
    "Qflow": "#c084fc"      # roxo
}

plt.figure(figsize=(14, 7))
ax = plt.gca()
y_max = -float('inf')

for i, col in enumerate(returns_df.columns):
    color = custom_colors.get(col, f"C{i}")
    y = returns_df[col]
    is_qflow = col.lower() == "qflow"

    ax.plot(
        returns_df.index,
        y,
        label=col,
        color=color,
        linestyle='-' if is_qflow else '--',
        linewidth=3.0 if is_qflow else 1.8
    )

    last_value = y.iloc[-1]
    y_max = max(y_max, last_value)

    # Offset ajustado
    offset = 0.5 + (i % 3) * 0.6
    ax.text(
        returns_df.index[-1],
        last_value + offset,
        f"{last_value:+.2f}%",
        color=color,
        fontsize=12 if is_qflow else 9,
        fontweight='bold' if is_qflow else 'normal',
        ha='left',
        va='center'
    )

# Limite vertical ajustado com margem
plt.ylim(None, y_max + 6)

day_count = (end_date - start_date).days + 1
plt.title(f"Cumulative Return Comparison ({day_count} Days)")
plt.ylabel("Return (%)")
plt.xlabel("Date")
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend(frameon=True, facecolor='#2e2e2e', edgecolor='#aaaaaa', loc='upper left')
plt.tight_layout()

# Exportar imagem
plt.savefig("returns_chart.png", dpi=150)
plt.show()
