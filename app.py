"""
Bu uygulama Binance Futures API'sinden Long/Short oranlarını çekerek
grafik halinde gösterir.
"""

import requests
import pandas as pd
import numpy as np
import datetime as dt
import streamlit as st

# Binance API base URL
BINANCE = "https://fapi.binance.com/futures/data"

# Takip edilecek semboller
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT"]

# Sayfa ayarları
st.set_page_config(page_title="Long/Short Radar", layout="wide")
st.title("📊 Long/Short Radar (Binance Futures)")

# Kullanıcıdan sembol ve zaman penceresi seçimi
sym = st.selectbox("Sembol", SYMS, index=0)
tf_choice = st.radio("Zaman Penceresi", ["12h", "24h", "1w", "1mo"], horizontal=True)

def since_ms(window):
    """Seçilen zaman penceresine göre milisaniye cinsinden başlangıç zamanını döndürür."""
    now = int(dt.datetime.utcnow().timestamp() * 1000)
    hours = {"12h": 12, "24h": 24, "1w": 7 * 24, "1mo": 30 * 24}[window]
    return now - hours * 60 * 60 * 1000

def fetch_ratio(endpoint, symbol, window):
    """Belirli endpoint ve sembol için Binance API'den veri çeker."""
    params = {"symbol": symbol, "period": "5m", "limit": 1000}
    url = f"{BINANCE}/{endpoint}"
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()

    data = r.json()
    if not isinstance(data, list) or len(data) == 0:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    if "timestamp" not in df.columns or "longShortRatio" not in df.columns:
        return pd.DataFrame()

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df[df["timestamp"].astype("int64") // 10**6 >= since_ms(window)]

    df["ratio"] = df["longShortRatio"].astype(float)
    df["long_pct"] = df["ratio"] / (1 + df["ratio"])
    df["short_pct"] = 1 - df["long_pct"]
    return df

# Sekmeler ve endpointler
tabs = st.tabs(["Tüm Hesaplar", "Top Trader (Hesap)", "Top Trader (Pozisyon)"])
endpoints = ["globalLongShortAccountRatio", "topLongShortAccountRatio", "topLongShortPositionRatio"]

summaries = []
for i, ep in enumerate(endpoints):
    with tabs[i]:
        df = fetch_ratio(ep, sym, tf_choice)
        if df.empty:
            st.warning("Veri bulunamadı.")
            continue

        # Medyan + EMA ortalaması
        long_med = df["long_pct"].median()
        long_ema = df["long_pct"].ewm(span=max(1, round(len(df) / 3))).mean().iloc[-1]
        long_pct = float((long_med + long_ema) / 2)
        short_pct = 1 - long_pct

        if long_pct > 0.53:
            dom = "📈 LONG baskın"
        elif long_pct < 0.47:
            dom = "📉 SHORT baskın"
        else:
            dom = "⚖ Nötr"

        st.metric("Dominance", dom, delta=f"Long %{long_pct * 100:.1f} / Short %{short_pct * 100:.1f}")
        st.line_chart_
