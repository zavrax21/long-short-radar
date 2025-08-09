import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from flask import Flask, request, jsonify
from threading import Thread

# ========================
# FLASK PROXY SUNUCUSU
# ========================
app_flask = Flask(__name__)

@app_flask.route("/proxy")
def proxy():
    symbol = request.args.get("symbol", "BTCUSDT")
    period = request.args.get("period", "5m")
    url = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period={period}&limit=1000"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return jsonify(r.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

def run_flask():
    app_flask.run(host="0.0.0.0", port=8000)

# Flask'i arka planda başlat
Thread(target=run_flask, daemon=True).start()

# ========================
# STREAMLIT UYGULAMASI
# ========================
st.set_page_config(page_title="Long/Short Oranları", layout="wide")

st.title("📊 Binance Long/Short Oranları")
st.markdown("Bu uygulama Binance API verilerini proxy üzerinden çekerek gösterir.")

# Kullanıcı seçimleri
symbol = st.selectbox("Sembol seç", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
period = st.selectbox("Periyot seç", ["5m", "15m", "30m", "1h", "2h", "4h", "1d"])

if st.button("Verileri Getir"):
    proxy_url = f"http://localhost:8000/proxy?symbol={symbol}&period={period}"
    try:
        r = requests.get(proxy_url)
        data = r.json()
        if "error" in data:
            st.error(f"Hata: {data['error']}")
        else:
            df = pd.DataFrame(data)
            df['longRatio'] = pd.to_numeric(df['longAccount'], errors='coerce')
            df['shortRatio'] = pd.to_numeric(df['shortAccount'], errors='coerce')
            df['time'] = pd.to_datetime(df['timestamp'], unit='ms')

            fig = px.line(df, x="time", y=["longRatio", "shortRatio"],
                          title=f"{symbol} Long/Short Oranları ({period})")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)
    except Exception as e:
        st.error(f"Veri alınamadı: {e}")
