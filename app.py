import streamlit as st
import yfinance as tck

st.title("Live Stock Price Tracker")

# 1. Put the stock ticker input and date range selector side-by-side
col1, col2 = st.columns([2, 1])

with col1:
    ticker_symbol = st.text_input("Enter a Stock Ticker (e.g., TSLA, AAPL, MSFT):", value="TSLA").upper().strip()

with col2:
    timeframe = st.selectbox(
        "Select Date Range:",
        options=["1 Day", "5 Days", "1 Month", "6 Months", "1 Year", "5 Years", "Max"],
        index=2  # Defaults to "1 Month"
    )

# 2. Map user-friendly labels to Yahoo Finance period & interval settings
period_map = {
    "1 Day": ("1d", "5m"),       # 5-minute intervals for today's intraday chart
    "5 Days": ("5d", "30m"),    # 30-minute intervals for 5 days
    "1 Month": ("1mo", "1d"),   # Daily intervals for 1 month
    "6 Months": ("6mo", "1d"),
    "1 Year": ("1y", "1d"),
    "5 Years": ("5y", "1wk"),   # Weekly intervals for 5 years
    "Max": ("max", "1mo")       # Monthly intervals for all-time history
}

selected_period, selected_interval = period_map[timeframe]

# 3. Refresh button
if st.button("Refresh Price"):
    st.rerun()

# 4. Fetch data and display price, line chart, and table
if ticker_symbol:
    stock = tck.Ticker(ticker_symbol)
    history_data = stock.history(period=selected_period, interval=selected_interval).dropna(subset=["Close"])

    if not history_data.empty:
        price = history_data["Close"].iloc[-1]
        st.metric(label=f"Current {ticker_symbol} Stock Price", value=f"${price:,.2f}")

        # Interactive line chart
        st.subheader(f"{ticker_symbol} - {timeframe} Price Chart")
        st.line_chart(history_data["Close"])

        # Data table (newest rows at the top)
        st.subheader(f"{ticker_symbol} - {timeframe} Price History")
        st.dataframe(history_data[["Open", "High", "Low", "Close", "Volume"]].iloc[::-1])
    else:
        st.error(f"Could not find stock data for '{ticker_symbol}'. Double-check the ticker symbol and try again.")
