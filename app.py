import streamlit as st
import yfinance as tck

st.set_page_config(page_title="Live Stock Price Tracker", layout="wide")
st.title("Live Stock Price Tracker")

# --- TOP MARKET INDICATORS KEYCARD ---
with st.container(border=True):
    st.subheader("Market Overview")
    indices = {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "Nasdaq": "^IXIC",
        "Russell 2000": "^RUT"
    }

    idx_cols = st.columns(len(indices))

    for col, (name, symbol) in zip(idx_cols, indices.items()):
        idx_hist = tck.Ticker(symbol).history(period="5d").dropna(subset=["Close"])
        if len(idx_hist) >= 2:
            latest = idx_hist["Close"].iloc[-1]
            prev = idx_hist["Close"].iloc[-2]
            change = latest - prev
            pct_change = (change / prev) * 100
            col.metric(
                label=name,
                value=f"{latest:,.2f}",
                delta=f"{change:+,.2f} ({pct_change:+.2f}%)"
            )
        elif len(idx_hist) == 1:
            col.metric(label=name, value=f"{idx_hist['Close'].iloc[-1]:,.2f}")
        else:
            col.metric(label=name, value="N/A")

st.divider()

# --- STOCK SEARCH & TIMEFRAME SELECTOR ---
col1, col2 = st.columns()

with col1:
    ticker_symbol = st.text_input("Enter a Stock Ticker (e.g., TSLA, AAPL, MSFT):", value="TSLA").upper().strip()

with col2:
    timeframe = st.selectbox(
        "Select Date Range:",
        options=["1 Day", "5 Days", "1 Month", "6 Months", "1 Year", "5 Years", "Max"],
        index=2  # Defaults to "1 Month"
    )

period_map = {
    "1 Day": ("1d", "5m"),
    "5 Days": ("5d", "30m"),
    "1 Month": ("1mo", "1d"),
    "6 Months": ("6mo", "1d"),
    "1 Year": ("1y", "1d"),
    "5 Years": ("5y", "1wk"),
    "Max": ("max", "1mo")
}

selected_period, selected_interval = period_map[timeframe]

if st.button("Refresh Price"):
    st.rerun()

# --- SELECTED STOCK DATA, CHART & TABLE ---
if ticker_symbol:
    stock = tck.Ticker(ticker_symbol)
    history_data = stock.history(period=selected_period, interval=selected_interval).dropna(subset=["Close"])

    if not history_data.empty:
        price = history_data["Close"].iloc[-1]
        st.metric(label=f"Current {ticker_symbol} Stock Price", value=f"${price:,.2f}")

        st.subheader(f"{ticker_symbol} - {timeframe} Price Chart")
        st.line_chart(history_data["Close"])

        st.subheader(f"{ticker_symbol} - {timeframe} Price History")
        st.dataframe(history_data[["Open", "High", "Low", "Close", "Volume"]].iloc[::-1], use_container_width=True)
    else:
        st.error(f"Could not find stock data for '{ticker_symbol}'. Double-check the ticker symbol and try again.")
