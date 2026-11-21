import streamlit as st
import yfinance as tck

st.set_page_config(page_title="Live Stock Price Tracker", layout="wide")
st.title("Live Stock Price Tracker")

# Helper function to render Yahoo-style market cards with sparklines
def render_market_cards(ticker_dict):
    cols = st.columns(len(ticker_dict))
    for col, (name, symbol) in zip(cols, ticker_dict.items()):
        hist = tck.Ticker(symbol).history(period="5d").dropna(subset=["Close"])
        with col:
            with st.container(border=True):
                if len(hist) >= 2:
                    latest = hist["Close"].iloc[-1]
                    prev = hist["Close"].iloc[-2]
                    change = latest - prev
                    pct_change = (change / prev) * 100
                    st.metric(
                        label=f"{name} ({symbol})",
                        value=f"{latest:,.2f}",
                        delta=f"{change:+,.2f} ({pct_change:+.2f}%)",
                        chart_data=hist["Close"].tolist(),
                        chart_type="line"
                    )
                elif len(hist) == 1:
                    st.metric(label=f"{name} ({symbol})", value=f"{hist['Close'].iloc[-1]:,.2f}")
                else:
                    st.metric(label=name, value="N/A")

# --- YAHOO FINANCE TOP MARKET SUMMARY BAR ---
tab1, tab2 = st.tabs(["🇺🇸 US Markets", "🛢️ Commodities, Bonds & Crypto"])

with tab1:
    render_market_cards({
        "S&P 500": "^GSPC",
        "Dow 30": "^DJI",
        "Nasdaq": "^IXIC",
        "Russell 2000": "^RUT",
        "VIX": "^VIX"
    })

with tab2:
    render_market_cards({
        "Crude Oil": "CL=F",
        "Gold": "GC=F",
        "10-Yr Bond": "^TNX",
        "Bitcoin USD": "BTC-USD",
        "US Dollar": "DX-Y.NYB"
    })

st.divider()

# --- STOCK SEARCH, TIMEFRAME & INDICATOR SELECTOR ---
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

# --- SELECTED STOCK DATA, SPLIT CHART & NEWS, AND TABLE ---
if ticker_symbol:
    stock = tck.Ticker(ticker_symbol)
    history_data = stock.history(period=selected_period, interval=selected_interval).dropna(subset=["Close"])

    if not history_data.empty:
        price = history_data["Close"].iloc[-1]
        first_price = history_data["Close"].iloc[0]
        period_change = price - first_price
        period_pct = (period_change / first_price) * 100

        st.metric(
            label=f"Current {ticker_symbol} Stock Price ({timeframe} Change)",
            value=f"${price:,.2f}",
            delta=f"{period_change:+,.2f} ({period_pct:+.2f}%)"
        )

        # Split the screen 50/50: Left = Price Chart, Right = Company News & Catalysts
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

            # Expandable Company Profile ("What is going on with the company")
            info = stock.info
            company_name = info.get("longName", ticker_symbol)
            sector = info.get("sector", "N/A")
            summary = info.get("longBusinessSummary", "No company overview available.")
            with st.expander(f"About {company_name} ({sector})", expanded=False):
                st.write(summary)

            # Scrollable Yahoo Finance News Feed
            news_items = stock.news
            if news_items:
                with st.container(height=390, border=True):
                    for item in news_items[:8]:
                        # Handle both newer and older yfinance news dictionary structures
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

        # Full-width Price History Table below the split section
        st.subheader(f"{ticker_symbol} - {timeframe} Price History")
        st.dataframe(history_data[["Open", "High", "Low", "Close", "Volume"]].iloc[::-1], use_container_width=True)
    else:
        st.error(f"Could not find stock data for '{ticker_symbol}'. Double-check the ticker symbol and try again.")
