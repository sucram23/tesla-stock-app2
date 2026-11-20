import streamlit as st
import yfinance as tck

st.title("Tesla (TSLA) Stock Tracker")

# 1. Get Tesla stock data
tesla_stock = tck.Ticker("TSLA")
todays_data = tesla_stock.history(period="5d")

# 2. Pull out the latest closing price
price = todays_data['Close'].iloc[-1]

# 3. Display the price and table on the webpage
st.metric(label="Current Tesla Stock Price", value=f"${price:,.2f}")
st.subheader("Last 5 Days Price History")
st.dataframe(todays_data[["Open", "High", "Low", "Close", "Volume"]])
