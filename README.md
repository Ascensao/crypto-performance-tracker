# Crypto Token Price Tracker

This project contains two Python scripts to fetch and update daily historical price data for:

- **QFLOW** (a Solana token) using the GeckoTerminal API.
- **BTC, ETH, and SOL** using the CoinGecko API.

Each script writes and updates a `.csv` file for each asset.

---

## 📁 Scripts

### `update_qflow.py`

Fetches and updates daily price data for QFLOW from the GeckoTerminal DEX API.

- Data is pulled from a specific Solana pool.
- Automatically appends only new daily prices to `qflow_price_history.csv`.

### `update_coins.py`

Fetches and updates daily price data for:

- Bitcoin (BTC)
- Ethereum (ETH)
- Solana (SOL)

Data comes from the CoinGecko API and is stored in separate files:
- `bitcoin_price_history.csv`
- `ethereum_price_history.csv`
- `solana_price_history.csv`

It updates each file incrementally, preserving historical data.

---

## 🧰 Requirements

- Python 3.7+
- Libraries: `requests`, `pandas`

Install dependencies:
```bash
pip install requests pandas
