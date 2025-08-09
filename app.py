import requests
import pandas as pd
import numpy as np
import datetime as dt
import streamlit as st

# Binance Futures veri URL'si (Proxy ile)
PROXY = "https://api.allorigins.win/raw?url="
BINANCE = "https://fapi.binance.com/futures/data"

# İzlenecek coin çiftleri
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT"]

# Streamlit ayarları
st.set_page_config(page_title="Long/Short Radar", layout="wide")
st.title("📊 Long/Short Radar (Binance Futures)")

# Kullanıcı seçimleri
sym = st.selectbox("Sembol", SYMS, index=0)
tf_choice = st.radio("Zaman Penceresi", ["12h", "24h", "1w", "1mo"], horizontal=True)

# Zaman filtresi
def since_ms(window):
    now = int(dt.datetime.utcnow().timestamp() * 1000)
    hours = {"12h": 12, "24h": 24, "1w": 7 * 24, "1mo": 30 * 24}[window]
    return now - hours * 60 * 60 * 1000

# Binance verisi çekme fonksiyonu
def fetch_ratio(endpoint, symbol, window):
    params = {"symbol": symbol, "period": "5m", "limit": 1000}
    url = PROXY + f"{BINANCE}/{endpoint}?symbol={symbol}&period=5m&limit=1000"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df[df["timestamp"].astype("int64") // 10**6 >= since_ms(window)]
    df["ratio"] = df["longShortRatio"].astype(float)
    df["long_pct"] = df["ratio"] / (1 + df["ratio"])
    df["short_pct"] = 1 - df["long_pct"]
    return df

# Sekmeler
tabs = st.tabs(["Tüm Hesaplar", "Top Trader (Hesap)", "Top Trader (Pozisyon)"])
endpoints = ["globalLongShortAccountRatio", "topLongShortAccountRatio", "topLongShortPositionRatio"]

summaries = []
for i, ep in enumerate(endpoints):
    with tabs[i]:
        df = fetch_ratio(ep, sym, tf_choice)
        if df.empty:
            st.warning("Veri yok veya API erişimi engellendi.")
            continue
