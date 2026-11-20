import streamlit as st
import yfinance as tck

st.title("Live Stock Price Tracker")

# 1. Add a text box where users can type any stock ticker (defaults to TSLA)
ticker_symbol = st.text_input("Enter a Stock Ticker (e.g., TSLA, AAPL, MSFT):", value="TSLA").upper().strip()

# 2. Add a refresh button
if st.button("Refresh Price"):
    st.rerun()

# 3. Fetch data for whatever ticker was typed in the box
if ticker_symbol:
    stock = tck.Ticker(ticker_symbol)
    todays_data = stock.history(period="5d").dropna(subset=["Close"])

    if not todays_data.empty:
        price = todays_data["Close"].iloc[-1]
        st.metric(label=f"Current {ticker_symbol} Stock Price", value=f"${price:,.2f}")
        st.subheader(f"{ticker_symbol} - Last 5 Days Price History")
        st.dataframe(todays_data[["Open", "High", "Low", "Close", "Volume"]])
    else:
        st.error(f"Could not find stock data for '{ticker_symbol}'. Double-check the ticker symbol and try again.")
