import streamlit as st
import pandas as pd
import yfinance as tck

st.set_page_config(page_title="Stock & Portfolio Tracker", layout="wide")
import hmac

def check_password():
    if st.session_state.get("password_correct", False):
        return True

    st.title("🔒 Private Stock & Portfolio Tracker")
    pwd = st.text_input("Enter Password to View App:", type="password")

    if st.button("Unlock App", type="primary"):
        if hmac.compare_digest(pwd, st.secrets["APP_PASSWORD"]):
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    return False

if not check_password():
    st.stop()

st.title("Live Stock Price & Portfolio Tracker")

if "holdings" not in st.session_state:
    st.session_state.holdings = [
        {"Ticker": "TSLA", "Shares": 10.0, "Buy Price": 250.00},
        {"Ticker": "AAPL", "Shares": 5.0, "Buy Price": 180.00}
    ]

def get_live_price(symbol, fallback=0.0):
    try:
        hist = tck.Ticker(symbol).history(period="5d").dropna(subset=["Close"])
        if not hist.empty:
            closes = hist["Close"].tolist()
            latest = float(closes[-1])
            prev = float(closes[-2]) if len(closes) >= 2 else latest
            return latest, prev
    except Exception:
        pass
    return float(fallback), float(fallback)

# --- 1. TOP MARKET SUMMARY BAR ---
m_tab1, m_tab2 = st.tabs(["US Markets", "Commodities, Bonds & Crypto"])

with m_tab1:
    cols = st.columns(5)
    us_indices = [("S&P 500", "^GSPC"), ("Dow 30", "^DJI"), ("Nasdaq", "^IXIC"), ("Russell 2000", "^RUT"), ("VIX", "^VIX")]
    for col, (name, sym) in zip(cols, us_indices):
        latest, prev = get_live_price(sym)
        with col:
            with st.container(border=True):
                if latest > 0:
                    change = latest - prev
                    pct = (change / prev) * 100 if prev > 0 else 0.0
                    st.metric(f"{name} ({sym})", f"{latest:,.2f}", f"{change:+,.2f} ({pct:+.2f}%)")
                else:
                    st.metric(name, "N/A")

with m_tab2:
    cols2 = st.columns(5)
    other_indices = [("Crude Oil", "CL=F"), ("Gold", "GC=F"), ("10-Yr Bond", "^TNX"), ("Bitcoin USD", "BTC-USD"), ("US Dollar", "DX-Y.NYB")]
    for col, (name, sym) in zip(cols2, other_indices):
        latest, prev = get_live_price(sym)
        with col:
            with st.container(border=True):
                if latest > 0:
                    change = latest - prev
                    pct = (change / prev) * 100 if prev > 0 else 0.0
                    st.metric(f"{name} ({sym})", f"{latest:,.2f}", f"{change:+,.2f} ({pct:+.2f}%)")
                else:
                    st.metric(name, "N/A")

st.divider()

# --- 2. STOCK RESEARCH, CHART, NEWS & FORECAST ---
st.header("Stock Research & Forecast")

col1, col2, col3 = st.columns(3)
ticker_symbol = col1.text_input("Enter a Stock Ticker (e.g., TSLA, AAPL, MSFT):", value="TSLA").upper().strip()
timeframe = col2.selectbox("Select Date Range:", ["1 Day", "5 Days", "1 Month", "6 Months", "1 Year", "5 Years", "Max"], index=4)
selected_indicators = col3.multiselect("Chart Indicators:", ["20-Period SMA", "50-Period SMA", "20-Period EMA", "Bollinger Bands"], default=["20-Period SMA"])

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

if ticker_symbol:
    stock = tck.Ticker(ticker_symbol)
    history_data = stock.history(period=selected_period, interval=selected_interval).dropna(subset=["Close"])

    if not history_data.empty:
        close_list = history_data["Close"].tolist()
        price = float(close_list[-1])
        first_price = float(close_list[-len(close_list)])
        period_change = price - first_price
        period_pct = (period_change / first_price) * 100

        st.metric(f"Current {ticker_symbol} Stock Price ({timeframe} Change)", f"${price:,.2f}", f"{period_change:+,.2f} ({period_pct:+.2f}%)")

        chart_col, news_col = st.columns(2)

        with chart_col:
            st.subheader(f"{ticker_symbol} - {timeframe} Price Chart")
            chart_df = history_data[["Close"]].copy()
            if "20-Period SMA" in selected_indicators:
                chart_df["SMA 20"] = history_data["Close"].rolling(window=20).mean()
            if "50-Period SMA" in selected_indicators:
                chart_df["SMA 50"] = history_data["Close"].rolling(window=50).mean()
            if "20-Period EMA" in selected_indicators:
                chart_df["EMA 20"] = history_data["Close"].ewm(span=20, adjust=False).mean()
            if "Bollinger Bands" in selected_indicators:
                sma20 = history_data["Close"].rolling(window=20).mean()
                std20 = history_data["Close"].rolling(window=20).std()
                chart_df["Upper Band"] = sma20 + (std20 * 2)
                chart_df["Lower Band"] = sma20 - (std20 * 2)
            st.line_chart(chart_df, height=450)

        with news_col:
            st.subheader(f"Why {ticker_symbol} Is Moving & Latest News")
            info = stock.info
            company_name = info.get("longName", ticker_symbol)
            sector = info.get("sector", "N/A")
            summary = info.get("longBusinessSummary", "No company overview available.")
            with st.expander(f"About {company_name} ({sector})", expanded=False):
                st.write(summary)

            news_items = stock.news
            if news_items:
                with st.container(height=390, border=True):
                    for item in news_items[:8]:
                        content = item.get("content", item)
                        title = content.get("title", "Headline unavailable")
                        summary_text = content.get("summary", "")
                        provider = content.get("provider", {})
                        publisher = provider.get("displayName") if isinstance(provider, dict) else content.get("publisher", "Yahoo Finance")
                        canonical = content.get("canonicalUrl", {})
                        link = canonical.get("url") if isinstance(canonical, dict) else content.get("link", "#")

                        st.markdown(f"**[{title}]({link})**")
                        st.caption(f"Source: {publisher}")
                        if summary_text:
                            st.write(summary_text[:180] + ("..." if len(summary_text) > 180 else ""))
                        st.divider()
            else:
                st.info(f"No recent Yahoo Finance news articles found for {ticker_symbol}.")

        st.subheader(f"Wall Street Forecast & 12-Month Price Targets ({ticker_symbol})")
        with st.container(border=True):
            target_low = info.get("targetLowPrice")
            target_mean = info.get("targetMeanPrice")
            target_high = info.get("targetHighPrice")
            rec_key = info.get("recommendationKey", "N/A")
            num_analysts = info.get("numberOfAnalystOpinions")

            if target_mean:
                f_col1, f_col2, f_col3, f_col4 = st.columns(4)
                rating_label = rec_key.replace("_", " ").upper() if isinstance(rec_key, str) else "N/A"
                analyst_note = f"Based on {num_analysts} analysts" if num_analysts else "Analyst consensus"
                f_col1.metric("Analyst Rating", rating_label, analyst_note, delta_color="off")
                f_col2.metric("Low Target (12M)", f"${target_low:,.2f}", f"{((target_low - price) / price) * 100:+.2f}% vs. current")
                f_col3.metric("Average Target (12M)", f"${target_mean:,.2f}", f"{((target_mean - price) / price) * 100:+.2f}% vs. current")
                f_col4.metric("High Target (12M)", f"${target_high:,.2f}", f"{((target_high - price) / price) * 100:+.2f}% vs. current")
            else:
                st.info(f"Wall Street analyst price targets are not available for {ticker_symbol}.")

        st.subheader(f"{ticker_symbol} - {timeframe} Price History")
        st.dataframe(history_data[["Open", "High", "Low", "Close", "Volume"]].iloc[::-1], use_container_width=True)
    else:
        st.error(f"Could not find stock data for '{ticker_symbol}'.")

st.divider()

# --- 3. MY PORTFOLIO SECTION (ALWAYS VISIBLE BELOW STOCKS) ---
st.header("My Portfolio")

rows = []
total_value = 0.0
total_cost = 0.0
total_day_change = 0.0

for item in st.session_state.holdings:
    sym = item["Ticker"]
    sh = float(item["Shares"])
    bp = float(item["Buy Price"])
    curr, prev = get_live_price(sym, fallback=bp)
    val = sh * curr
    cost = sh * bp
    day_chg = sh * (curr - prev)
    total_value += val
    total_cost += cost
    total_day_change += day_chg
    rows.append({
        "Ticker": sym,
        "Shares": sh,
        "Buy Price ($)": round(bp, 2),
        "Current Price ($)": round(curr, 2),
        "Total Value ($)": round(val, 2),
        "Profit / Loss ($)": round(val - cost, 2),
        "Return (%)": round(((curr - bp) / bp) * 100, 2) if bp > 0 else 0.0
    })

# Top Portfolio Keycard
with st.container(border=True):
    st.subheader("Portfolio Summary Keycard")
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Portfolio Value", f"${total_value:,.2f}", f"{total_day_change:+,.2f} Today")
    k2.metric("Total Invested Cost", f"${total_cost:,.2f}", f"{len(rows)} Holdings", delta_color="off")
    k3.metric("Total Profit / Loss", f"${total_value - total_cost:+,.2f}")

# Add Stock Controls
c1, c2, c3, c4 = st.columns(4, vertical_alignment="bottom")
new_sym = c1.text_input("Add Ticker (e.g., NVDA)").upper().strip()
new_sh = c2.number_input("Shares", min_value=0.01, value=1.0)
new_bp = c3.number_input("Buy Price ($)", min_value=0.01, value=100.0)
if c4.button("Add Stock", use_container_width=True):
    if new_sym:
        st.session_state.holdings.append({"Ticker": new_sym, "Shares": new_sh, "Buy Price": new_bp})
        st.rerun()

# Portfolio Table + Total Estimated Value Directly Below
if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.success(f"Total Estimated Portfolio Value: ${total_value:,.2f} (Invested: ${total_cost:,.2f} | Profit/Loss: ${total_value - total_cost:+,.2f})")

    rem_col1, rem_col2 = st.columns(2, vertical_alignment="bottom")
