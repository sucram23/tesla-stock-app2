import streamlit as st
import yfinance as tck

st.title("Live Stock Price Tracker")

# 1. Text box to enter any stock ticker (defaults to TSLA)
ticker_symbol = st.text_input("Enter a Stock Ticker (e.g., TSLA, AAPL, MSFT):", value="TSLA").upper().strip()

# 2. Refresh button
if st.button("Refresh Price"):
    st.rerun()

# 3. Fetch data and display price, line chart, and table
if ticker_symbol:
    stock = tck.Ticker(ticker_symbol)
    history_data = stock.history(period="1mo").dropna(subset=["Close"])

    if not history_data.empty:
        price = history_data["Close"].iloc[-1]
        st.metric(label=f"Current {ticker_symbol} Stock Price", value=f"${price:,.2f}")

        # Interactive line chart of closing prices
        st.subheader(f"{ticker_symbol} - 30-Day Price Chart")
        st.line_chart(history_data["Close"])

        # Data table of recent trading days
        st.subheader(f"{ticker_symbol} - Recent Price History")
        st.dataframe(history_data[["Open", "High", "Low", "Close", "Volume"]].tail(10))
    else:
        st.error(f"Could not find stock data for '{ticker_symbol}'. Double-check the ticker symbol and try again.")
