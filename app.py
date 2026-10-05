import streamlit as st  
import yfinance as yf  
import pandas as pd  
import numpy as np

st.set_page_config(page_title="Top-Down Bullish Stock Scanner", layout="wide")

st.title("Sector Rotation & Top Outperformer Scanner")  
st.caption("10 se 15 Din ke Bullish Swing Trades ke liye Top-Down Scanner")

# =========================
# Sector & Stock Mapping
# =========================
SECTORS = {  
    "NIFTY AUTO": {  
        "index": "^CNXAUTO",  
        "stocks": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS"]  
    },  
    "NIFTY IT": {  
        "index": "^CNXIT",  
        "stocks": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS"]  
    },  
    "NIFTY PHARMA": {  
        "index": "^CNXPHARMA",  
        "stocks": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "LUPIN.NS", "AUROPHARMA.NS"]  
    },  
    "NIFTY BANK": {  
        "index": "^NSEBANK",  
        "stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS"]  
    },  
    "NIFTY FMCG": {  
        "index": "^CNXFMCG",  
        "stocks": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS", "GODREJCP.NS"]  
    },  
    "NIFTY METAL": {  
        "index": "^CNXMETAL",  
        "stocks": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "SAIL.NS", "NMDC.NS"]  
    },  
    "NIFTY ENERGY": {  
        "index": "^CNXENERGY",  
        "stocks": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "POWERGRID.NS", "NTPC.NS"]  
    },  
    "NIFTY REALTY": {  
        "index": "^CNXREALTY",  
        "stocks": ["DLF.NS", "LODHA.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "PHOENIXLTD.NS"]  
    }  
}

# =========================
# Indicator Helper Functions
# =========================
def calculate_rsi(series, period=14):  
    delta = series.diff()  
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()  
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()  
    rs = gain / loss  
    rsi = 100 - (100 / (1 + rs))  
    return rsi

def get_data(symbol, period="3mo", interval="1d"):  
    try:  
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)  
        if df.empty:  
            return None  
        return df  
    except:  
        return None

# =========================
# Scanner Engine
# =========================
if st.button("Run Live Market Scanner"):  
    st.subheader("1. Market Situation Analysis")

    nifty = get_data("^NSEI", period="3mo")  
    if nifty is not None:  
        nifty["RSI"] = calculate_rsi(nifty["Close"])  
        latest_close = float(nifty["Close"].iloc[-1])  
        latest_rsi = float(nifty["RSI"].iloc[-1])

        trend = "Bullish" if latest_close > nifty["Close"].rolling(20).mean().iloc[-1] else "Bearish"

        col1, col2, col3 = st.columns(3)  
        col1.metric("NIFTY 50 Level", f"{latest_close:.2f}")  
        col2.metric("Market Trend", trend)  
        col3.metric("NIFTY RSI", f"{latest_rsi:.2f}")  
    else:  
        st.error("NIFTY 50 data fetch nahi ho paya.")

    st.subheader("2. Sector Strength Analysis")  
    sector_perf = []

    for sector_name, info in SECTORS.items():  
        sector_df = get_data(info["index"], period="1mo")  
        if sector_df is not None and len(sector_df) > 5:  
            perf = ((sector_df["Close"].iloc[-1] / sector_df["Close"].iloc[-6]) - 1) * 100  
            sector_perf.append([sector_name, round(float(perf), 2)])

    if sector_perf:  
        sector_df = pd.DataFrame(sector_perf, columns=["Sector", "5-Day Performance %"])  
        sector_df = sector_df.sort_values(by="5-Day Performance %", ascending=False)

        st.dataframe(sector_df, use_container_width=True)

        top_sectors = sector_df.head(2)["Sector"].tolist()  
        st.success(f"Top 2 Strongest Sectors: {', '.join(top_sectors)}")  
    else:  
        st.warning("Sector data available nahi hai.")  
        top_sectors = []

    st.subheader("3. Top Bullish Outperformer Stocks (10-15 Days)")  
    stock_results = []

    for sector in top_sectors:  
        stocks = SECTORS[sector]["stocks"]  
        for stock in stocks:  
            df = get_data(stock, period="3mo")  
            if df is not None and len(df) > 30:  
                df["RSI"] = calculate_rsi(df["Close"])  
                close = float(df["Close"].iloc[-1])  
                ma20 = float(df["Close"].rolling(20).mean().iloc[-1])  
                ma50 = float(df["Close"].rolling(50).mean().iloc[-1]) if len(df) >= 50 else ma20  
                rsi = float(df["RSI"].iloc[-1])

                bullish_score = 0  
                if close > ma20:  
                    bullish_score += 1  
                if close > ma50:  
                    bullish_score += 1  
                if 55 <= rsi <= 70:  
                    bullish_score += 1

                if bullish_score >= 2:  
                    stock_results.append([sector, stock, round(close, 2), round(rsi, 2), bullish_score])

    if stock_results:  
        result_df = pd.DataFrame(  
            stock_results,  
            columns=["Sector", "Stock", "CMP", "RSI", "Bullish Score"]  
        )  
        result_df = result_df.sort_values(by=["Bullish Score", "RSI"], ascending=[False, False]).head(5)

        st.dataframe(result_df, use_container_width=True)

        st.info("Recommended Top 5 Bullish Stocks for next 10-15 days based on trend, RSI and sector strength.")  
    else:  
        st.warning("Koi strong bullish outperformer stock abhi scan me nahi mila.")

st.markdown("---")  
st.caption("Disclaimer: Yeh tool sirf technical scanning aur educational purpose ke liye hai. Investment decision lene se pehle apna analysis zarur karein.")
