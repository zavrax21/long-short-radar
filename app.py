# pip install streamlit requests pandas numpy
import requests, pandas as pd, numpy as np, datetime as dt
import streamlit as st

BINANCE = "fapi.binance.com/futures/data"

SYMS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","DOGEUSDT","ADAUSDT"]

st.set_page_config(page_title="Long/Short Radar", layout="wide")
st.title("Long/Short Radar (Binance Futures)")

sym = st.selectbox("Sembol", SYMS, index=0)
tf_choice = st.radio("Zaman Penceresi", ["12h","24h","1w","1mo"], horizontal=True)

def since_ms(window):
    now = int(dt.datetime.utcnow().timestamp()*1000)
    hours = {"12h":12,"24h":24,"1w":7*24,"1mo":30*24}[window]
    return now - hours*60*60*1000

def fetch_ratio(endpoint, symbol, window):
    params = {"symbol": symbol, "period": "5m", "limit": 1000}
    url = f"{BINANCE}/{endpoint}"
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df[df["timestamp"].astype("int64")//10**6 >= since_ms(window)]
    # longShortRatio = long/short; long% = ratio/(1+ratio)
    df["ratio"] = df["longShortRatio"].astype(float)
    df["long_pct"] = df["ratio"]/(1+df["ratio"])
    df["short_pct"] = 1 - df["long_pct"]
    return df

tabs = st.tabs(["Tüm Hesaplar","Top Trader (Hesap)","Top Trader (Pozisyon)"])
endpoints = ["globalLongShortAccountRatio","topLongShortAccountRatio","topLongShortPositionRatio"]

summaries = []
for i,ep in enumerate(endpoints):
    with tabs[i]:
        df = fetch_ratio(ep, sym, tf_choice)
        if df.empty:
            st.warning("Veri yok.")
            continue
        # Ağırlıklı ortalama (işlem adedi yerine zaman ağırlığı → medyan + EMA karışımı)
        long_med = df["long_pct"].median()
        long_ema = df["long_pct"].ewm(span=round(len(df)/3)).mean().iloc[-1]
        long_pct = float((long_med+long_ema)/2)
        short_pct = 1-long_pct
        dom = "LONG baskın" if long_pct>0.53 else "SHORT baskın" if long_pct<0.47 else "Nötr"
        st.metric("Dominance", dom, delta=f"Long %{long_pct*100:.1f} / Short %{short_pct*100:.1f}")
        st.line_chart(df.set_index("timestamp")[["long_pct","short_pct"]])
        summaries.append((ep, long_pct, short_pct, dom))

st.subheader("Özet")
for name,lp,sp,dom in summaries:
    label = {"globalLongShortAccountRatio":"Tüm Hesaplar",
             "topLongShortAccountRatio":"Top Trader (Hesap)",
             "topLongShortPositionRatio":"Top Trader (Pozisyon)"}[name]
    st.write(f"*{label}* – {dom} (Long %{lp*100:.1f} / Short %{sp*100:.1f})")

st.caption("Not: 53% üstü LONG, 47% altı SHORT baskın
