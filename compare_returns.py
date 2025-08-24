# compare_returns.py
# Version 2.0.1 - Some visual issues fixed.
# 2025-08-24

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch
import numpy as np
import glob
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ──────────── Diretório dos dados ────────────
DATA_DIR = "price_data"
if not os.path.exists(DATA_DIR):
    print(f"❌ Pasta {DATA_DIR} não encontrada. Corre primeiro os scripts de download.")
    exit()

# ──────────── 📅 MENU DE PERÍODOS ────────────
def show_period_menu():
    print("\n" + "="*60)
    print("📊 ANÁLISE DE RETORNOS CRYPTO")
    print("="*60)
    print("\n📅 Selecione o período de análise:")
    print("\n1️⃣  1 Dia")
    print("2️⃣  1 Semana (7 dias)")
    print("3️⃣  15 Dias")
    print("4️⃣  1 Mês (30 dias)")
    print("5️⃣  3 Meses (90 dias)")
    print("6️⃣  6 Meses (180 dias)")
    print("7️⃣  1 Ano (365 dias)")
    print("8️⃣  Desde o início (todos os dados)")
    print("9️⃣  Data personalizada")
    print("\n❌ Q - Sair do programa")
    print("-"*60)

def get_date_range():
    show_period_menu()
    
    while True:
        try:
            choice = input("\n➡️  Escolha uma opção (1-9 ou Q): ").strip().upper()
            
            if choice == "Q":
                return None, None, None
            
            today = datetime.now().date()
            
            if choice == "1":
                start_date = today - timedelta(days=1)
                end_date = today
                period_name = "1 Day"
                break
            elif choice == "2":
                start_date = today - timedelta(days=7)
                end_date = today
                period_name = "1 Week"
                break
            elif choice == "3":
                start_date = today - timedelta(days=15)
                end_date = today
                period_name = "15 Days"
                break
            elif choice == "4":
                start_date = today - timedelta(days=30)
                end_date = today
                period_name = "1 Month"
                break
            elif choice == "5":
                start_date = today - timedelta(days=90)
                end_date = today
                period_name = "3 Months"
                break
            elif choice == "6":
                start_date = today - timedelta(days=180)
                end_date = today
                period_name = "6 Months"
                break
            elif choice == "7":
                start_date = today - timedelta(days=365)
                end_date = today
                period_name = "1 Year"
                break
            elif choice == "8":
                files = glob.glob(os.path.join(DATA_DIR, "*_price_history.csv"))
                earliest_date = None
                
                for file in files:
                    try:
                        df = pd.read_csv(file, parse_dates=["date"])
                        file_earliest = df["date"].min().date()
                        if earliest_date is None or file_earliest < earliest_date:
                            earliest_date = file_earliest
                    except:
                        continue
                
                if earliest_date:
                    start_date = earliest_date
                    end_date = today
                    period_name = "All Time"
                else:
                    print("❌ Erro ao encontrar dados históricos")
                    continue
                break
            elif choice == "9":
                print("\nInsira as datas personalizadas:")
                start_input = input("Data de início (YYYY-MM-DD): ")
                end_input = input("Data de fim (YYYY-MM-DD): ")
                
                try:
                    start_date = pd.to_datetime(start_input).date()
                    end_date = pd.to_datetime(end_input).date()
                    
                    if start_date >= end_date:
                        print("❌ A data de início deve ser anterior à data de fim")
                        continue
                        
                    period_name = f"{start_date} to {end_date}"
                except:
                    print("❌ Formato de data inválido. Use YYYY-MM-DD")
                    continue
                break
            else:
                print("❌ Opção inválida. Escolha entre 1-9 ou Q")
                continue
                
        except KeyboardInterrupt:
            print("\n👋 Operação cancelada")
            return None, None, None
        except Exception as e:
            print(f"❌ Erro: {e}")
            continue
    
    print(f"\n✅ Período selecionado: {period_name}")
    print(f"📅 De {start_date} até {end_date}")
    
    return start_date, end_date, period_name

# ──────────── MÉTRICAS ────────────
def calculate_drawdown(series):
    peak = series.cummax()
    drawdown = (series - peak) / peak
    return drawdown.min() * 100

def calculate_sharpe(series):
    daily_ret = series.pct_change().dropna()
    if daily_ret.std() == 0:
        return 0
    sharpe = (daily_ret.mean() / daily_ret.std()) * np.sqrt(365)
    return sharpe

def process_and_plot_data(start_date, end_date, period_name):
    # ──────────── 📁 LER DADOS ────────────
    files = glob.glob(os.path.join(DATA_DIR, "*_price_history.csv"))
    if not files:
        print("❌ No CSV files found in", DATA_DIR)
        return
    
    all_returns = {}
    all_prices = {}
    summary_data = []
    
    # ──────────── PROCESSAR ATIVOS ────────────
    for file in files:
        try:
            df = pd.read_csv(file, parse_dates=["date"])
            df = df.set_index("date").sort_index()
            
            name = os.path.basename(file).replace("_price_history.csv", "").capitalize()
            # Renomear Qflow para Quantum Flow
            if name.lower() == "qflow":
                name = "Quantum Flow"
            
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
            all_prices[name] = df["price"]
            
            summary_data.append({
                'name': name,
                'start_price': start_price,
                'end_price': end_price,
                'return_pct': return_pct,
                'max_ret': max_ret,
                'drawdown': drawdown,
                'sharpe': sharpe
            })
            
        except Exception as e:
            print(f"Erro ao processar {file}: {e}")
    
    # ──────────── RESUMO NO TERMINAL ────────────
    print(f"\n📈 Performance Summary - {period_name}:\n")
    print(f"{'Asset':<10} | {'Start Price':>12} | {'End Price':>12} | {'Return':>8} | {'Max Return':>11} | {'Max DD':>9} | {'Sharpe':>7}")
    print("-" * 95)
    
    for data in summary_data:
        print(
            f"{data['name']:<10} | "
            f"${data['start_price']:>11.4f} | "
            f"${data['end_price']:>11.4f} | "
            f"{data['return_pct']:>7.2f}% | "
            f"{data['max_ret']:>10.2f}% | "
            f"{data['drawdown']:>8.2f}% | "
            f"{data['sharpe']:>6.2f}"
        )
    
    # ──────────── GRÁFICO MELHORADO ────────────
    if not all_returns:
        print("❌ No valid data to plot.")
        return
    
    returns_df = pd.DataFrame(all_returns)
    returns_df.index.name = "Date"
    
    # Configuração do estilo profissional
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Cores gradientes profissionais - TROCADAS Ethereum e Solana
    custom_colors = {
        "Bitcoin": "#FF6B35",      # Laranja vibrante
        "Ethereum": "#10B981",     # Verde menta (trocado com Solana)
        "Solana": "#3B82F6",       # Azul moderno (trocado com Ethereum)
        "Quantum Flow": "#8B5CF6"  # Roxo premium
    }
    
    # Criar figura com layout profissional
    fig = plt.figure(figsize=(18, 10))  # Aumentado de 16 para 18 de largura
    gs = fig.add_gridspec(3, 2, height_ratios=[2.5, 0.8, 0.5], width_ratios=[3, 1], hspace=0.3, wspace=0.2)
    
    # Gráfico principal
    ax_main = fig.add_subplot(gs[0, :])
    ax_main.set_facecolor('#0F0F0F')
    
    # Adicionar gradiente de fundo
    gradient = np.linspace(0, 1, 100).reshape(1, -1)
    ax_main.imshow(gradient, extent=[returns_df.index[0], returns_df.index[-1], 
                                     returns_df.min().min() - 10, returns_df.max().max() + 10],
                   aspect='auto', cmap='gray', alpha=0.1, zorder=0)
    
    # Plotar linhas com efeito glow
    for i, col in enumerate(returns_df.columns):
        color = custom_colors.get(col, f"C{i}")
        y = returns_df[col]
        is_quantum = col == "Quantum Flow"
        
        # Efeito glow
        for glow_width in [8, 5, 3]:
            ax_main.plot(returns_df.index, y, color=color, alpha=0.1, 
                        linewidth=glow_width, zorder=1)
        
        # Linha principal
        line = ax_main.plot(
            returns_df.index, y,
            label=col,
            color=color,
            linewidth=3.5 if is_quantum else 2.5,
            alpha=0.95,
            zorder=2
        )[0]
        
        # Marcador no último ponto
        ax_main.scatter(returns_df.index[-1], y.iloc[-1], 
                        color=color, s=150 if is_quantum else 100, 
                        zorder=3, edgecolors='white', linewidth=2)
        
        # Calcular posição mais inteligente para as labels
        x_pos = returns_df.index[-1]
        y_pos = y.iloc[-1]
        
        # Ajustar horizontalmente para evitar corte
        # Em vez de adicionar dias, usar coordenadas de dados mais precisas
        x_offset = pd.Timedelta(hours=6)  # Offset menor
        
        # Ajustar verticalmente para evitar sobreposição
        label_spacing = 2.5  # Espaçamento vertical entre labels
        sorted_final_values = sorted([(col, returns_df[col].iloc[-1]) for col in returns_df.columns], 
                                    key=lambda x: x[1], reverse=True)
        
        # Encontrar a posição desta crypto na lista ordenada
        position_index = next(i for i, (name, _) in enumerate(sorted_final_values) if name == col)
        
        # Se as labels estão muito próximas, ajustar verticalmente
        if len(returns_df.columns) > 1:
            y_range = returns_df.iloc[-1].max() - returns_df.iloc[-1].min()
            if y_range < 10:  # Se a diferença entre valores finais é pequena
                # Distribuir labels verticalmente
                base_y = returns_df.iloc[-1].mean()
                y_pos = base_y + (position_index - len(returns_df.columns)/2 + 0.5) * label_spacing
        
        # Label do valor final com caixa estilizada - posição corrigida
        bbox_props = dict(boxstyle="round,pad=0.3", 
                        facecolor=color, alpha=0.8, 
                        edgecolor='white', linewidth=1)
        
        label_text = ax_main.text(
            x_pos + x_offset,  # Posição X ajustada
            y_pos,             # Posição Y ajustada
            f"{col}: {returns_df[col].iloc[-1]:+.1f}%",
            color='white',
            fontsize=11 if is_quantum else 10,
            fontweight='bold',
            va='center',
            ha='left',  # Adicionado alinhamento horizontal
            bbox=bbox_props,
            clip_on=False  # Importante: permite que o texto apareça fora da área do plot
        )
    
    # Configuração do gráfico principal
    ax_main.set_title(f"PERFORMANCE COMPARISON - {period_name.upper()}", 
                     fontsize=20, fontweight='bold', color='white', pad=20)
    ax_main.set_xlabel("Date", fontsize=14, color='#CCCCCC')
    ax_main.set_ylabel("Cumulative Return (%)", fontsize=14, color='#CCCCCC')
    
    # Mudar cor dos valores dos eixos para branco
    ax_main.tick_params(axis='x', colors='white')
    ax_main.tick_params(axis='y', colors='white')
    
    # Grid estilizado
    ax_main.grid(True, linestyle='--', alpha=0.2, color='#444444')
    ax_main.axhline(y=0, color='#666666', linestyle='-', linewidth=1, alpha=0.5)
    
    # Legenda estilizada
    legend = ax_main.legend(loc='upper left', frameon=True, fancybox=True, 
                           shadow=True, fontsize=12)
    legend.get_frame().set_facecolor('#1A1A1A')
    legend.get_frame().set_alpha(0.9)
    legend.get_frame().set_edgecolor('#444444')
    
    # Mudar cor do texto da legenda para branco
    for text in legend.get_texts():
        text.set_color('white')
    
    # Adicionar linha de tendência suave para o melhor performer
    best_performer = returns_df.iloc[-1].idxmax()
    z = np.polyfit(range(len(returns_df)), returns_df[best_performer], 2)
    p = np.poly1d(z)
    ax_main.plot(returns_df.index, p(range(len(returns_df))), 
                '--', alpha=0.3, color='yellow', linewidth=1, 
                label='Trend')
    
    # Tabela de métricas
    ax_table = fig.add_subplot(gs[1, :])
    ax_table.axis('tight')
    ax_table.axis('off')
    
    # Preparar dados da tabela
    table_data = []
    headers = ['Asset', 'Return', 'Max DD', 'Sharpe', 'Status']
    
    for data in sorted(summary_data, key=lambda x: x['return_pct'], reverse=True):
        status = "↑" if data['return_pct'] > 50 else "+" if data['return_pct'] > 0 else "↓"
        table_data.append([
            data['name'],
            f"{data['return_pct']:+.2f}%",
            f"{data['drawdown']:.2f}%",
            f"{data['sharpe']:.2f}",
            status
        ])
    
    table = ax_table.table(cellText=table_data, colLabels=headers,
                          cellLoc='center', loc='center',
                          colWidths=[0.2, 0.2, 0.2, 0.2, 0.1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)
    
    # Estilizar tabela
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#2E2E2E')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            # Highlight para Quantum Flow sempre
            if table_data[i-1][0] == "Quantum Flow":
                table[(i, j)].set_facecolor('#3B1E6B')  # Roxo escuro para Quantum Flow
            elif i == 1 and table_data[0][0] != "Quantum Flow":  # Melhor performer (se não for Quantum Flow)
                table[(i, j)].set_facecolor('#1B4332')
            else:
                table[(i, j)].set_facecolor('#1A1A1A')
            table[(i, j)].set_text_props(color='white')
    
    # Rodapé com informações
    ax_footer = fig.add_subplot(gs[2, :])
    ax_footer.axis('off')
    
    day_count = (end_date - start_date).days + 1
    footer_text = (f"Period: {start_date} to {end_date} ({day_count} days) | "
                  f"Best: {best_performer} ({returns_df[best_performer].iloc[-1]:+.1f}%) | "
                  f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    ax_footer.text(0.5, 0.5, footer_text, ha='center', va='center',
                  fontsize=12, color='#888888', style='italic',
                  bbox=dict(boxstyle="round,pad=0.5", facecolor='#1A1A1A', 
                           edgecolor='#444444', alpha=0.8))
    
    x_min, x_max = ax_main.get_xlim()
    y_min, y_max = ax_main.get_ylim()

    # Expandir limite direito para acomodar as labels
    x_padding = (x_max - x_min) * 0.15  # 15% de padding à direita
    ax_main.set_xlim(x_min, x_max + x_padding)

    # Expandir limites verticais se necessário
    y_padding = (y_max - y_min) * 0.05  # 5% de padding vertical
    ax_main.set_ylim(y_min - y_padding, y_max + y_padding)
    
    # Configuração geral da figura
    fig.patch.set_facecolor('#0A0A0A')
    plt.suptitle("CRYPTO RETURNS ANALYSIS", fontsize=24, fontweight='bold', 
                color='white', y=0.98)
    
    # Salvar com alta qualidade
    safe_period_name = period_name.replace(" ", "_").replace("/", "-")
    filename = f"crypto_returns_{safe_period_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    plt.savefig(filename, dpi=300, facecolor='#0A0A0A', edgecolor='none', 
               bbox_inches='tight', pad_inches=0.3)
    
    print(f"\n✅ Gráfico guardado como: {filename}")
    plt.show()

    
    return True

# ──────────── LOOP PRINCIPAL ────────────
def main():
    print("\n" + "="*60)
    print("🚀 BEM-VINDO AO ANALISADOR DE RETORNOS CRYPTO")
    print("="*60)
    
    while True:
        start_date, end_date, period_name = get_date_range()
        
        if start_date is None:  # User chose to quit
            print("\n" + "="*60)
            print("👋 Obrigado por usar o analisador!")
            print("🚀 Até à próxima!")
            print("="*60)
            break
        
        try:
            process_and_plot_data(start_date, end_date, period_name)
            
            print("\n" + "-"*60)
            input("📊 Prima ENTER para voltar ao menu principal...")
            
        except Exception as e:
            print(f"\n❌ Erro durante o processamento: {e}")
            input("Prima ENTER para continuar...")

if __name__ == "__main__":
    main()