import streamlit as st
import pandas as pd
import yfinance as tck

st.set_page_config(page_title="Stock & Portfolio Tracker", layout="wide")
st.title("Stock & Portfolio Tracker (V2)")

if "holdings" not in st.session_state:
    st.session_state.holdings = [
        {"Ticker": "TSLA", "Shares": 10.0, "Buy Price": 250.00},
        {"Ticker": "AAPL", "Shares": 5.0, "Buy Price": 180.00}
    ]

# --- TOP MARKET SUMMARY BAR ---
cols = st.columns(5)
indices = [("S&P 500", "^GSPC"), ("Dow 30", "^DJI"), ("Nasdaq", "^IXIC"), ("Russell 2000", "^RUT"), ("VIX", "^VIX")]
for col, (name, sym) in zip(cols, indices):
    hist = tck.Ticker(sym).history(period="5d").dropna(subset=["Close"])
    if len(hist) >= 2:
        latest = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2])
        col.metric(name, f"{latest:,.2f}", f"{latest - prev:+,.2f}")

st.divider()

# --- PORTFOLIO SECTION (ALWAYS VISIBLE, NO HIDDEN TABS) ---
st.header("My Portfolio")

# 1. Calculate Portfolio Values
rows = []
total_value = 0.0
total_cost = 0.0

for item in st.session_state.holdings:
    sym = item["Ticker"]
    sh = float(item["Shares"])
    bp = float(item["Buy Price"])
    hist = tck.Ticker(sym).history(period="5d").dropna(subset=["Close"])
    curr = float(hist["Close"].iloc[-1]) if not hist.empty else bp
    val = sh * curr
    cost = sh * bp
    total_value += val
    total_cost += cost
    rows.append({
        "Ticker": sym,
        "Shares": sh,
        "Buy Price": bp,
        "Current Price": round(curr, 2),
        "Total Value": round(val, 2),
        "Profit/Loss": round(val - cost, 2)
    })

# 2. TOP PORTFOLIO KEYCARD
with st.container(border=True):
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Portfolio Value", f"${total_value:,.2f}")
    k2.metric("Total Invested", f"${total_cost:,.2f}")
    k3.metric("Total Profit / Loss", f"${total_value - total_cost:+,.2f}")

# 3. ADD STOCK INPUTS
c1, c2, c3, c4 = st.columns(4)
new_sym = c1.text_input("Ticker (e.g. NVDA)").upper().strip()
new_sh = c2.number_input("Shares", min_value=0.01, value=1.0)
new_bp = c3.number_input("Buy Price ($)", min_value=0.01, value=100.0)
if c4.button("Add Stock"):
    if new_sym:
        st.session_state.holdings.append({"Ticker": new_sym, "Shares": new_sh, "Buy Price": new_bp})
        st.rerun()

# 4. PORTFOLIO TABLE + TOTAL WORTH DIRECTLY BELOW
if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.success(f"Total Estimated Portfolio Value: ${total_value:,.2f}")

    # Remove stock
    rem = st.selectbox("Remove stock:", [r["Ticker"] for r in rows])
    if st.button("Remove Selected"):
        st.session_state.holdings = [h for h in st.session_state.holdings if h["Ticker"] != rem]
        st.rerun()
