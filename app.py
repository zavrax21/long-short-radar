import requests, pandas as pd, numpy as np, datetime as dt
import streamlit as st

# Proxy üzerinden Binance'e bağlanmak için (AllOrigins kullanıyoruz)
PROXY = "https://api.allorigins.win/raw?url="
BINANCE = "https://fapi.binance.com/futures/data"

SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT"]

st.set_page_config(page_title="Long/Short Radar", layout="wide")
st.title("Long/Short Radar (Binance Futures)")

sym = st.selectbox("Sembol", SYMS, index=0)
tf_choice = st.radio("Zaman Penceresi", ["12h", "24h", "1w", "1mo"], horizontal=True)

def since_ms(window):
    now = int(dt.datetime.utcnow().timestamp() * 1000)
    hours = {"12h": 12, "24h": 24, "1w": 7 * 24, "1mo": 30 * 24}[window]
    return now - hours * 60 * 60 * 1000

def fetch_ratio(endpoint, symbol, window):
    params = {"symbol": symbol, "period": "5m", "limit": 1000}
    url = f"{PROXY}{BINANCE}/{endpoint}"
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df[df["timestamp"].astype("int64") // 10**6 >= since_ms(window)]
    df["ratio"] = df["longShortRatio"].astype(float)
    df["long_pct"] = df["ratio"] / (1 + df["ratio"])
    df["short_pct"] = 1 - df["long_pct"]
    return df

tabs = st.tabs(["Tüm Hesaplar", "Top Trader (Hesap)", "Top Trader (Pozisyon)"])
endpoints = ["globalLongShortAccountRatio", "topLongShortAccountRatio", "topLongShortPositionRatio"]

summaries = []
for i, ep in enumerate(endpoints):
    with tabs[i]:
        try:
            df = fetch_ratio(ep, sym, tf_choice)
        except Exception as e:
            st.error(f"Veri çekilemedi: {e}")
            continue
        if df.empty:
            st.warning("Veri yok.")
            continue
        long_med = df["long_pct"].median()
        long_ema = df["long_pct"].ewm(span=round(len(df) / 3)).mean()_]()_

