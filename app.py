import yfinance as tck

# 1. Choose your favorite company (Tesla!)
tesla_stock = tck.Ticker("TSLA")

# 2. Get today's live pricing information
todays_data = tesla_stock.history(period="1d")

# 3. Pull out the exact closing price (add [0] after iloc!)
price = todays_data['Close'].iloc[0]

# 4. Print it out like magic!
print(f"The current Tesla stock price is: ${price:.2f}")

