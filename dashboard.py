import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Cryptocurrency Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# ==========================================================
# Custom CSS
# ==========================================================

st.markdown("""
<style>

/* ---------- KPI Cards ---------- */

.kpi-card{
    text-align:center;
    padding:6px 0 10px 0;
}

.kpi-icon{
    font-size:52px;
    line-height:1;
    margin-bottom:8px;
}

.kpi-title{
    font-size:22px;
    font-weight:600;
    color:#5b6470;
    margin-bottom:12px;
}

.kpi-value{
    font-size:44px;
    font-weight:700;
    color:#111827;
}

/* Hide Streamlit metric styling */

[data-testid="stMetric"]{
    display:none;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# PostgreSQL Connection
# ==========================================================

engine = create_engine(
    "postgresql://itc6050:itc6050@localhost:5432/crypto_market"
)

# ==========================================================
# Load Data
# ==========================================================

daily_summary = pd.read_sql(
    "SELECT * FROM analytics.daily_market_summary",
    engine
)

coins = pd.read_sql(
    "SELECT * FROM analytics.stg_coins",
    engine
)

coin_history = pd.read_sql(
    "SELECT * FROM analytics.stg_coin_history",
    engine
)

# ==========================================================
# Header
# ==========================================================

st.title("📈 Cryptocurrency Market Dashboard")

st.markdown("""
### Live Cryptocurrency Market Analytics

Real-time market data powered by **CoinGecko API**

**Pipeline:** CoinGecko → dlt → PostgreSQL → dbt → Streamlit
""")

st.divider()


# ==========================================================
# KPI Cards
# ==========================================================

total_market_cap = daily_summary["total_market_cap"].iloc[0]
total_volume = coins["total_volume"].sum()
coins_tracked = len(coins)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">💰</div>
        <div class="kpi-title">Total Market Cap</div>
        <div class="kpi-value">${total_market_cap/1e12:.2f} T</div>
    </div>
    """, unsafe_allow_html=True)

with col2:

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📊</div>
        <div class="kpi-title">24h Volume</div>
        <div class="kpi-value">${total_volume/1e9:.2f} B</div>
    </div>
    """, unsafe_allow_html=True)

with col3:

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🪙</div>
        <div class="kpi-title">Coins Tracked</div>
        <div class="kpi-value">{coins_tracked}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================================
# Top 10 Market Capitalization
# ==========================================================

st.subheader("🏆 Top 10 Cryptocurrencies by Market Capitalization")

top10 = (
    coins
    .sort_values("market_cap", ascending=False)
    .head(10)
    .copy()
)

top10["label"] = top10["symbol"].str.upper() + "   " + top10["name"]

fig = px.bar(

    top10,

    x="market_cap",

    y="label",

    orientation="h",

    color="market_cap",

    color_continuous_scale="Blues"

)

fig.update_yaxes(

    autorange="reversed"

)

fig.update_xaxes(

    type="log",

    showticklabels=False,

    title=None

)

fig.update_layout(

    height=560,

    plot_bgcolor="white",

    paper_bgcolor="white",

    coloraxis_showscale=False,

    yaxis_title=None,

    font=dict(size=17),

    margin=dict(

        l=20,

        r=20,

        t=20,

        b=20

    )

)

fig.update_traces(

    text=[

        f"${x/1e12:.2f} T"

        if x >= 1e12

        else f"${x/1e9:.2f} B"

        for x in top10["market_cap"]

    ],

    textposition="outside",

    hovertemplate=(
        "<b>%{y}</b><br>"
        "Market Cap: %{text}"
        "<extra></extra>"
    )

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()

# ==========================================================
# Price Trend
# ==========================================================

st.subheader("📈 Cryptocurrency Price Trend")

coin_list = (
    coin_history["coin_id"]
    .drop_duplicates()
    .sort_values()
)

selected_coin = st.selectbox(

    "Select Cryptocurrency",

    coin_list,

    format_func=lambda x: x.replace("-", " ").title()

)

history = (
    coin_history[
        coin_history["coin_id"] == selected_coin
    ]
    .sort_values("date")
)

fig = px.line(

    history,

    x="date",

    y="price",

    title=f"{selected_coin.title()} - Last 90 Days",

    markers=True

)

fig.update_layout(

    height=520,

    plot_bgcolor="white",

    paper_bgcolor="white",

    font=dict(size=17),

    xaxis_title="",

    yaxis_title="Price (USD)",

    hovermode="x unified"

)

fig.update_traces(

    line=dict(width=3),

    hovertemplate=
        "<b>%{x}</b><br>"
        "Price: $%{y:,.2f}"
        "<extra></extra>"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()

# ==========================================================
# Biggest Gainers & Losers
# ==========================================================

st.subheader("📊 Biggest 24h Gainers & Losers")

col1, col2 = st.columns(2)

# ----------------------------------------------------------
# Top Gainers
# ----------------------------------------------------------

gainers = (
    coins
    .sort_values(
        "price_change_percentage_24h",
        ascending=False
    )
    .head(10)
    .copy()
)

gainers = gainers[
    [
        "symbol",
        "image",
        "name",
        "current_price",
        "price_change_percentage_24h"
    ]
]

gainers["symbol"] = gainers["symbol"].str.upper()

gainers["current_price"] = gainers["current_price"].map(
    lambda x: f"${x:,.2f}"
)

gainers["price_change_percentage_24h"] = gainers[
    "price_change_percentage_24h"
].map(
    lambda x: f"🟢 {x:.2f}%"
)

with col1:

    st.markdown("### 🟢 Top 10 Gainers")

    st.dataframe(

        gainers,

        hide_index=True,

        use_container_width=True,

        column_config={

            "symbol": st.column_config.TextColumn(
                "Symbol",
                width="small"
            ),

            "image": st.column_config.ImageColumn(
                "Logo",
                width="small"
            ),

            "name": st.column_config.TextColumn(
                "Name",
                width="medium"
            ),

            "current_price": st.column_config.TextColumn(
                "Price",
                width="small"
            ),

            "price_change_percentage_24h": st.column_config.TextColumn(
                "24h Change",
                width="small"
            )

        }

    )

# ----------------------------------------------------------
# Top Losers
# ----------------------------------------------------------

losers = (
    coins
    .sort_values(
        "price_change_percentage_24h",
        ascending=True
    )
    .head(10)
    .copy()
)

losers = losers[
    [
        "symbol",
        "image",
        "name",
        "current_price",
        "price_change_percentage_24h"
    ]
]

losers["symbol"] = losers["symbol"].str.upper()

losers["current_price"] = losers["current_price"].map(
    lambda x: f"${x:,.2f}"
)

losers["price_change_percentage_24h"] = losers[
    "price_change_percentage_24h"
].map(
    lambda x: f"🔴 {x:.2f}%"
)

with col2:

    st.markdown("### 🔴 Top 10 Losers")

    st.dataframe(

        losers,

        hide_index=True,

        use_container_width=True,

        column_config={

            "symbol": st.column_config.TextColumn(
                "Symbol",
                width="small"
            ),

            "image": st.column_config.ImageColumn(
                "Logo",
                width="small"
            ),

            "name": st.column_config.TextColumn(
                "Name",
                width="medium"
            ),

            "current_price": st.column_config.TextColumn(
                "Price",
                width="small"
            ),

            "price_change_percentage_24h": st.column_config.TextColumn(
                "24h Change",
                width="small"
            )

        }

    )

st.divider()

# ==========================================================
# Sidebar Filters
# ==========================================================

'''st.sidebar.header("⚙ Dashboard Filters")

top_n = st.sidebar.slider(

    "Top N Coins",

    min_value=5,

    max_value=50,

    value=10,

    step=5

)

coin_history["date"] = pd.to_datetime(coin_history["date"])

min_date = coin_history["date"].min().date()
max_date = coin_history["date"].max().date()

date_range = st.sidebar.date_input(

    "Date Range",

    value=(min_date, max_date),

    min_value=min_date,

    max_value=max_date

)
'''

