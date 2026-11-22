import streamlit as st
import pandas as pd
import yfinance as tck

st.set_page_config(page_title="Live Stock Price & Portfolio Tracker", layout="wide")
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
            latest = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else latest
            return latest, prev
    except Exception:
        pass
    return float(fallback), float(fallback)

def render_market_cards(ticker_dict):
    cols = st.columns(len(ticker_dict))
    for col, (name, symbol) in zip(cols, ticker_dict.items()):
        latest, prev = get_live_price(symbol)
        with col:
            with st.container(border=True):
                if latest > 0:
                    change = latest - prev
                    pct_change = (change / prev) * 100 if prev > 0 else 0.0
                    st.metric(
                        label=f"{name} ({symbol})",
                        value=f"{latest:,.2f}",
                        delta=f"{change:+,.2f} ({pct_change:+.2f}%)"
                    )
                else:
                    st.metric(label=name, value="N/A")

# --- TOP MARKET SUMMARY BAR ---
m_tab1, m_tab2 = st.tabs(["US Markets", "Commodities, Bonds & Crypto"])

with m_tab1:
    render_market_cards({
        "S&P 500": "^GSPC",
        "Dow 30": "^DJI",
        "Nasdaq": "^IXIC",
        "Russell 2000": "^RUT",
        "VIX": "^VIX"
    })

with m_tab2:
    render_market_cards({
        "Crude Oil": "CL=F",
        "Gold": "GC=F",
        "10-Yr Bond": "^TNX",
        "Bitcoin USD": "BTC-USD",
        "US Dollar": "DX-Y.NYB"
    })

st.divider()

# --- PAGE SWITCHER ---
active_view = st.radio(
    "Navigation",
    options=["Stock Research & Forecast", "My Portfolio"],
    horizontal=True,
    label_visibility="collapsed"
)

# ==========================================
# VIEW 1: STOCK RESEARCH, CHART, NEWS & FORECAST
# ==========================================
if active_view == "Stock Research & Forecast":
    col1, col2, col3 = st.columns(3)

    with col1:
        ticker_symbol = st.text_input("Enter a Stock Ticker (e.g., TSLA, AAPL, MSFT):", value="TSLA").upper().strip()

    with col2:
        timeframe = st.selectbox(
            "Select Date Range:",
            options=["1 Day", "5 Days", "1 Month", "6 Months", "1 Year", "5 Years", "Max"],
            index=4
        )

    with col3:
        selected_indicators = st.multiselect(
            "Chart Indicators:",
            options=["20-Period SMA", "50-Period SMA", "20-Period EMA", "Bollinger Bands"],
            default=["20-Period SMA"]
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

    if ticker_symbol:
        stock = tck.Ticker(ticker_symbol)
        history_data = stock.history(period=selected_period, interval=selected_interval).dropna(subset=["Close"])

        if not history_data.empty:
            price = float(history_data["Close"].iloc[-1])
            first_price = float(history_data["Close"].iloc[0])
            period_change = price - first_price
            period_pct = (period_change / first_price) * 100

            st.metric(
                label=f"Current {ticker_symbol} Stock Price ({timeframe} Change)",
                value=f"${price:,.2f}",
                delta=f"{period_change:+,.2f} ({period_pct:+.2f}%)"
            )

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
                    f_col1.metric(label="Analyst Rating", value=rating_label, delta=analyst_note, delta_color="off")
                    f_col2.metric(label="Low Target (12M)", value=f"${target_low:,.2f}", delta=f"{((target_low - price) / price) * 100:+.2f}% vs. current")
                    f_col3.metric(label="Average Target (12M)", value=f"${target_mean:,.2f}", delta=f"{((target_mean - price) / price) * 100:+.2f}% vs. current")
                    f_col4.metric(label="High Target (12M)", value=f"${target_high:,.2f}", delta=f"{((target_high - price) / price) * 100:+.2f}% vs. current")
                else:
                    st.info(f"Wall Street analyst price targets are not available for {ticker_symbol}.")

            st.subheader(f"{ticker_symbol} - {timeframe} Price History")
            st.dataframe(history_data[["Open", "High", "Low", "Close", "Volume"]].iloc[::-1], use_container_width=True)
        else:
            st.error(f"Could not find stock data for '{ticker_symbol}'.")

# ==========================================
# VIEW 2: PORTFOLIO WITH GUARANTEED TOTAL VALUE
# ==========================================
else:
    rows = []
    total_cost = 0.0
    total_value = 0.0
    total_day_change = 0.0
    total_shares = 0.0

    for item in st.session_state.holdings:
        sym = item["Ticker"]
        shares = float(item["Shares"])
        buy_price = float(item["Buy Price"])
        curr_price, prev_close = get_live_price(sym, fallback=buy_price)

        cost_basis = shares * buy_price
        market_value = shares * curr_price
        day_change = shares * (curr_price - prev_close)
        gain_loss = market_value - cost_basis
        gain_pct = ((curr_price - buy_price) / buy_price) * 100 if buy_price > 0 else 0.0

        total_cost += cost_basis
        total_value += market_value
        total_day_change += day_change
        total_shares += shares

        rows.append({
            "Ticker": sym,
            "Shares": shares,
            "Buy Price ($)": round(buy_price, 2),
            "Current Price ($)": round(curr_price, 2),
            "Total Value ($)": round(market_value, 2),
            "Gain / Loss ($)": round(gain_loss, 2),
            "Return (%)": round(gain_pct, 2)
        })

    total_gain = total_value - total_cost
    total_return_pct = ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0.0

