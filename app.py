# pip install streamlit requests pandas numpy
import requests, pandas as pd, numpy as np, datetime as dt, urllib.parse
import streamlit as st

# Binance API + Proxy ayarı (451 hatası almamak için)
BINANCE = "fapi.binance.com/futures/data"
PROXY = "https://api.allorigins.win/raw?url="  # proxy

SYMS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","DOGEUSDT","ADAUSDT"]

st.set_page_config(page_title="Long/Short Radar", layout="wide")
st.title("📊 Long/Short Radar (Binance Futures)")

sym = st.selectbox("Sembol", SYMS, index=0)
tf_choice = st.radio("Zaman Penceresi", ["12h","24h","1w","1mo"], horizontal=True)

def since_ms(window):
    now = int(dt.datetime.utcnow().timestamp()*1000)
    hours = {"12h":12,"24h":24,"1w":7*24,"1mo":30*24}[window]
    return now - hours*60*60*1000

def fetch_ratio(endpoint, symbol, window):
    try:
        base_url = f"{BINANCE}/{endpoint}?symbol={symbol}&period=5m&limit=1000"
        encoded_url = PROXY + urllib.parse.quote(base_url, safe="")
        r = requests.get(encoded_url, timeout=15)
        r.raise_for_status()
        data = r.json()

        if not isi
