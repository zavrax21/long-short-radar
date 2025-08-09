import requests
import pandas as pd
import streamlit as st
import plotly.express as px

"""
Bu uygulama Binance API'sinden Long/Short oranlarını çekerek
grafik halinde gösterir.
"""

# API'den veri çekme fonksiyonu
def fetch_ratio(ep, symbol, tf):
    url = f"{ep}?symbol={symbol}&period={tf}&limit=1000"

    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()  # HTTP hatası varsa burada durur
        data = r.json()

        if not data:
            st.warning("API veri döndürmedi.")
            return pd.DataFrame()

        df = pd.DataFrame(data)

        # Tarih formatlama
        if 'timestamp' in df.columns:
            df["time"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Long/Short yüzdesi hesaplama
        if 'longAccount' in df.columns and 'shortAccount' in df.columns:
            df["long_pct"] = df["longAccount"].astype(float) * 100
            df["short_pct"] = df["shortAccount"].astype(float) * 100

        return df

    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP hatası: {e}")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"İstek hatası: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Bilinmeyen hata: {e}")
        return pd.DataFrame()

# Streamlit başlığı
st.title("📊 Binance Long / Short Oran Takip")

# Kullanıcı seçenekleri
symbol = st.selectbox("Sembol Seçin", ["BTCUSDT", "ETHUSDT", "BNBUSDT"])
tf_choice = st.selectbox("Zaman Aralığı", ["5m", "15m", "30m", "1h", "4h", "1d"])

# Binance API endpoint
ep = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio"

# Veri çekme
df = fetch_ratio(ep, symbol, tf_choice)

if not df.empty:
    st.success(f"Veriler başarıyla alındı: {symbol} - {tf_choice}")

    # Grafik çizimi
    fig = px.line(df, x="time", y=["long_pct", "short_pct"],
                  labels={"value": "Yüzde (%)", "time": "Zaman"},
                  title=f"{symbol} Long / Short Oranları ({tf_choice})")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Gösterilecek veri yok.")
