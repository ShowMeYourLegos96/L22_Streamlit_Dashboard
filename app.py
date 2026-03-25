#[Christopher Ponds]
#[U0000011844]
#{Python Programming}

from datetime import datetime

import streamlit as st
import pandas as pd
import requests


# Page configuration
st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Title and description
st.title("📊 Cryptocurrency Market Dashboard")
st.markdown("Real-time cryptocurrency data from CoinGecko API")
st.markdown("---")

# Sidebar for user inputs
st.sidebar.header("🔧 Dashboard Controls")


@st.cache_data
def fetch_coin_list():
    # Fetch list of all CoinGecko top-level endpoints (used for quick diagnostics)
    try:
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch coin list: {e}")
        return {}


@st.cache_data
def fetch_market_data(vs_currency, order, per_page, page):
    """Fetch current market data for cryptocurrencies"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": order,
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
            "price_change_percentage": "24h,7d"
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch market data: {e}")
        return []


@st.cache_data(ttl=300)
def fetch_global_data():
    """Fetch global cryptocurrency market statistics"""
    try:
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch global data: {e}")
        return None
@st.cache_data  
def fetch_historical_data(coin_id, vs_currency, days):
    """Fetch historical market chart data for a specific cryptocurrency"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "interval": "daily" if days > 90 else "hourly"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch historical data: {e}")
        return None
# Sidebar widgets
st.sidebar.markdown("### 📈 Market Configuration")
vs_currency = st.sidebar.selectbox(
    "Currency",
    options=["usd", "eur", "gbp", "jpy", "cad", "aud", "cny"],
    index=0,
    help="Select the base currency for price display"
)

order_by = st.sidebar.selectbox(
    "Sort By",
    options=["market_cap_desc", "volume_desc", "price_change_percentage_24h_desc", "id_asc"],
    format_func=lambda x: {
        "market_cap_desc": "Market Cap (High to Low)",
        "volume_desc": "Trading Volume (High to Low)",
        "price_change_percentage_24h_desc": "24h Price Change (High to Low)",
        "id_asc": "Name (A to Z)"
    }[x],
    help="Sort cryptocurrencies by different metrics"
)
items_per_page = st.sidebar.slider(
    "Items per page",
    min_value=5,
    max_value=50,
    value=10,
    step=5,
    help="Number of cryptocurrencies to display"
)
# Time series configuration
st.sidebar.markdown("### 📊 Time Series Settings")
available_coins = fetch_coin_list()
if available_coins:
    # Get top coins for quick selection
    top_coins = ["bitcoin", "ethereum", "cardano", "solana", "ripple", "dogecoin", "polkadot", "chainlink"]
    coin_options = [coin for coin in available_coins if coin["id"] in top_coins]
    coin_options = [{"id": coin["id"], "symbol": coin["symbol"], "name": coin["name"]} 
                    for coin in coin_options if coin["id"] in top_coins]
    
    selected_coin = st.sidebar.selectbox(
        "Select Cryptocurrency",
        options=coin_options,
        format_func=lambda x: f"{x['name']} ({x['symbol'].upper()})",
        help="Choose a cryptocurrency to view historical data"
    )
    
    time_range = st.sidebar.selectbox(
        "Time Range",
        options=[7, 14, 30, 90, 180, 365],
        format_func=lambda x: f"{x} days",
        index=2,
        help="Select the historical time range"
    )
else:
    selected_coin = {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}
    time_range = 30

# Main dashboard layout
st.markdown("## 📊 Market Overview")

global_data = fetch_global_data()
if global_data:
    total_market_cap = global_data["data"]["total_market_cap"].get(vs_currency, 0)
    total_volume = global_data["data"]["total_volume"].get(vs_currency, 0)
    market_cap_change_24h = global_data["data"]["market_cap_change_percentage_24h_usd"]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Market Cap", f"${total_market_cap:,.0f}", f"{market_cap_change_24h:.2f}%")
    col2.metric("Total Volume", f"${total_volume:,.0f}")
    col3.metric("Active Cryptocurrencies", global_data["data"]["active_cryptocurrencies"])
st.markdown("---")

market_data =fetch_market_data(vs_currency, order_by, items_per_page, page=1)
if market_data:
    df = pd.DataFrame(market_data)
    df["price_change_percentage_24h"] = df["price_change_percentage_24h"].round(2)
    df["price_change_percentage_7d_in_currency"] = df["price_change_percentage_7d_in_currency"].round(2)
    
    st.dataframe(df[["name", "symbol", "current_price", "market_cap", "total_volume", 
                      "price_change_percentage_24h", "price_change_percentage_7d_in_currency"]])
    #format for display 
    df_display = df[["name", "symbol", "current_price", "market_cap", "total_volume", 
                      "price_change_percentage_24h", "price_change_percentage_7d_in_currency"]].copy()
    df_display["current_price"] = df_display["current_price"].apply(lambda x: f"${x:,.2f}")
    df_display["market_cap"] = df_display["market_cap"].apply(lambda x: f"${x:,.0f}")
    df_display["total_volume"] = df_display["total_volume"].apply(lambda x: f"${x:,.0f}")
    df_display["price_change_percentage_24h"] = df_display["price_change_percentage_24h"].apply(lambda x: f"{x:.2f}%")
    df_display["price_change_percentage_7d_in_currency"] = df_display["price_change_percentage_7d_in_currency"].apply(lambda x: f"{x:.2f}%")
    
    #display data table
    st.markdown("### Top Cryptocurrencies")
    st.dataframe(df_display[['name', 'symbol', 'price', 'price_change_24h', 'price_change_7d', 'market_cap', 'volume_24h']],
        use_container_width=True,
        column_config={
            "name": "Name",
            "symbol": "Symbol",
            "price": "Price",
            "price_change_24h": "24h Change",
            "price_change_7d": "7d Change",
            "market_cap": "Market Cap",
            "volume_24h": "24h Volume"
        }
    )

#Footer 
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Data provided by CoinGecko API | Dashboard created for CS 2850 - Intermediate Python Programming</p>
    <p>Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)