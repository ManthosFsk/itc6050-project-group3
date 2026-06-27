import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Crypto Market Dashboard",
    page_icon="₿",
    layout="wide"
)

# ==========================================================
# Dark Mode CSS
# ==========================================================

st.markdown("""
<style>

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}

[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d;
}

[data-testid="stSidebar"] * {
    color: #e6edf3 !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 24px 16px 20px 16px;
    text-align: center;
    margin: 4px;
}

.kpi-icon {
    font-size: 36px;
    line-height: 1;
    margin-bottom: 10px;
}

.kpi-title {
    font-size: 13px;
    font-weight: 500;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 36px;
    font-weight: 700;
    color: #58a6ff;
    letter-spacing: -0.02em;
}

/* ── Section Headers ── */
h2, h3, .stSubheader {
    color: #e6edf3 !important;
}

/* ── Divider ── */
hr {
    border-color: #30363d !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    background-color: #161b22 !important;
}

/* ── Selectbox / Slider ── */
[data-testid="stSelectbox"] > div,
[data-testid="stSlider"] {
    background-color: #161b22 !important;
    color: #e6edf3 !important;
}

[data-testid="stMetric"] { display: none; }

/* ── Equal KPI columns ── */
[data-testid="column"] {
    padding: 0 4px !important;
}

[data-testid="column"] > div {
    height: 100%;
}

.kpi-card {
    height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%) !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    padding: 24px 16px 20px 16px !important;
    text-align: center !important;
    margin: 4px !important;
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

@st.cache_data(ttl=300)
def load_data():
    daily_summary = pd.read_sql(
        "SELECT * FROM analytics.daily_market_summary ORDER BY date DESC",
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
    coin_analytics = pd.read_sql(
        "SELECT * FROM analytics.coin_price_analytics",
        engine
    )
    coin_history["date"] = pd.to_datetime(coin_history["date"])
    coin_analytics["date"] = pd.to_datetime(coin_analytics["date"])
    return daily_summary, coins, coin_history, coin_analytics

daily_summary, coins, coin_history, coin_analytics = load_data()

# ==========================================================
# Sidebar Filters
# ==========================================================

st.sidebar.markdown("## ⚙️ Filters")
st.sidebar.markdown("---")

top_n = st.sidebar.selectbox(
    "Top N Coins",
    [5, 10, 15, 20, 25, 50],
    index=1
)

st.sidebar.markdown("")

start_date = coin_history["date"].min().date()
end_date = coin_history["date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(start_date, end_date),
    min_value=start_date,
    max_value=end_date
)

# ==========================================================
# Header
# ==========================================================

st.markdown("""
<h1 style='color:#58a6ff; font-size:2.2rem; font-weight:800; margin-bottom:0;'>
₿ Cryptocurrency Market Dashboard
</h1>
<p style='color:#8b949e; font-size:0.95rem; margin-top:4px;'>
Real-time analytics powered by CoinGecko API &nbsp;·&nbsp;
Pipeline: CoinGecko → dlt → PostgreSQL → dbt → Streamlit
</p>
""", unsafe_allow_html=True)

st.divider()

# ==========================================================
# KPI Cards
# ==========================================================

# Filter daily_summary by date range
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered_summary = daily_summary[
        (pd.to_datetime(daily_summary["date"]) >= start) &
        (pd.to_datetime(daily_summary["date"]) <= end)
    ]
else:
    filtered_summary = daily_summary

# KPIs react to filters
total_market_cap = filtered_summary["total_market_cap"].mean()
total_volume = coins.nlargest(top_n, "market_cap")["total_volume"].sum()
coins_tracked = top_n
top_coin = (
    filtered_summary
    .sort_values("total_market_cap", ascending=False)
    ["top_coin_by_volume"]
    .iloc[0]
    if len(filtered_summary) > 0
    else "N/A"
)

col1, col2, col3, col4 = st.columns(4)

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

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🏆</div>
        <div class="kpi-title">Top by Volume</div>
        <div class="kpi-value" style="font-size:24px;">{top_coin.title()}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================================
# Top N Market Capitalization — Bar Chart + Table
# ==========================================================

st.subheader(f"🏆 Top {top_n} Cryptocurrencies by Market Cap")

top_coins = (
    coins
    .sort_values("market_cap", ascending=False)
    .head(top_n)
    .copy()
)

top_coins["label"] = top_coins["symbol"].str.upper() + "  " + top_coins["name"]

fig_bar = px.bar(
    top_coins,
    x="market_cap",
    y="label",
    orientation="h",
    color="market_cap",
    color_continuous_scale=[[0, "#1f4068"], [0.5, "#1b6ca8"], [1, "#58a6ff"]]
)

fig_bar.update_yaxes(autorange="reversed")
fig_bar.update_xaxes(type="log", showticklabels=False, title=None, showgrid=False)
fig_bar.update_yaxes(showgrid=False, tickfont=dict(size=13, color="#e6edf3"))

fig_bar.update_layout(
    height=max(400, top_n * 48),
    plot_bgcolor="#0d1117",
    paper_bgcolor="#0d1117",
    coloraxis_showscale=False,
    yaxis_title=None,
    font=dict(size=13, color="#e6edf3"),
    margin=dict(l=10, r=80, t=10, b=10)
)

fig_bar.update_traces(
    text=[
        f"${x/1e12:.2f} T" if x >= 1e12 else f"${x/1e9:.2f} B"
        for x in top_coins["market_cap"]
    ],
    textposition="outside",
    textfont=dict(color="#e6edf3", size=12),
    hovertemplate="<b>%{y}</b><br>Market Cap: %{text}<extra></extra>"
)

st.plotly_chart(fig_bar, use_container_width=True)

# Table with Logos
top_table = (
    coins
    .sort_values("market_cap", ascending=False)
    .head(top_n)
    [["image", "symbol", "name", "current_price", "market_cap", "price_change_percentage_24h"]]
    .copy()
)

top_table["symbol"] = top_table["symbol"].str.upper()
top_table["current_price"] = top_table["current_price"].map(lambda x: f"${x:,.2f}")
top_table["market_cap"] = top_table["market_cap"].map(
    lambda x: f"${x/1e12:.2f} T" if x >= 1e12 else f"${x/1e9:.2f} B"
)
top_table["price_change_percentage_24h"] = top_table["price_change_percentage_24h"].map(
    lambda x: f"🟢 {x:.2f}%" if x >= 0 else f"🔴 {x:.2f}%"
)

st.dataframe(
    top_table,
    hide_index=True,
    use_container_width=True,
    column_config={
        "image": st.column_config.ImageColumn("Logo", width="small"),
        "symbol": st.column_config.TextColumn("Symbol", width="small"),
        "name": st.column_config.TextColumn("Name", width="medium"),
        "current_price": st.column_config.TextColumn("Price", width="small"),
        "market_cap": st.column_config.TextColumn("Market Cap", width="small"),
        "price_change_percentage_24h": st.column_config.TextColumn("24h Change", width="small"),
    }
)

st.divider()

# ==========================================================
# Price Trend — Line Chart with 7-Day Rolling Average
# ==========================================================

st.subheader("📈 Price Trend — Last 90 Days")

coin_list = coin_analytics["coin_id"].drop_duplicates().sort_values()

selected_coin = st.selectbox(
    "Select Cryptocurrency",
    coin_list,
    format_func=lambda x: x.replace("-", " ").title()
)

# Apply date filter
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered = coin_analytics[
        (coin_analytics["date"] >= start) &
        (coin_analytics["date"] <= end)
    ]
else:
    filtered = coin_analytics

history = (
    filtered[filtered["coin_id"] == selected_coin]
    .sort_values("date")
)

fig_line = go.Figure()

fig_line.add_trace(go.Scatter(
    x=history["date"],
    y=history["price"],
    mode="lines",
    name="Price",
    line=dict(color="#58a6ff", width=2),
    fill="tozeroy",
    fillcolor="rgba(88, 166, 255, 0.06)",
    hovertemplate="<b>%{x}</b><br>Price: $%{y:,.2f}<extra></extra>"
))

fig_line.add_trace(go.Scatter(
    x=history["date"],
    y=history["price_7d_rolling_avg"],
    mode="lines",
    name="7-Day Rolling Avg",
    line=dict(color="#f78166", width=2, dash="dot"),
    hovertemplate="<b>%{x}</b><br>7D Avg: $%{y:,.2f}<extra></extra>"
))

fig_line.update_layout(
    title=dict(
        text=f"{selected_coin.replace('-', ' ').title()} — Price vs 7-Day Rolling Average",
        font=dict(size=15, color="#e6edf3")
    ),
    height=440,
    plot_bgcolor="#0d1117",
    paper_bgcolor="#0d1117",
    font=dict(size=13, color="#8b949e"),
    legend=dict(
        bgcolor="#161b22",
        bordercolor="#30363d",
        borderwidth=1,
        font=dict(color="#e6edf3")
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#21262d",
        title=None,
        tickfont=dict(color="#8b949e")
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#21262d",
        title="Price (USD)",
        tickfont=dict(color="#8b949e"),
        tickprefix="$"
    ),
    hovermode="x unified",
    margin=dict(l=10, r=10, t=40, b=10)
)

st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# ==========================================================
# Volatility Ranking
# ==========================================================

st.subheader("⚡ Volatility Ranking — 90-Day Standard Deviation")

st.markdown(
    "<p style='color:#8b949e; font-size:0.9rem;'>"
    "Higher volatility score = larger price swings over the last 90 days.</p>",
    unsafe_allow_html=True
)

volatility_df = (
    coin_analytics
    .groupby("coin_id")[["volatility_score", "avg_price_90d"]]
    .first()
    .reset_index()
    .sort_values("volatility_score", ascending=False)
    .head(top_n)
    .copy()
)

# Merge with coin names and logos
coin_meta = coins[["id", "image", "name", "symbol"]].rename(columns={"id": "coin_id"})
volatility_df = volatility_df.merge(coin_meta, on="coin_id", how="left")

volatility_df = volatility_df[[
    "image", "symbol", "name", "avg_price_90d", "volatility_score"
]]

volatility_df["symbol"] = volatility_df["symbol"].str.upper()
volatility_df["avg_price_90d"] = volatility_df["avg_price_90d"].map(
    lambda x: f"${x:,.4f}" if x < 1 else f"${x:,.2f}"
)
volatility_df["volatility_score"] = volatility_df["volatility_score"].map(
    lambda x: f"${x:,.4f}" if x < 1 else f"${x:,.2f}"
)

st.dataframe(
    volatility_df,
    hide_index=True,
    use_container_width=True,
    column_config={
        "image": st.column_config.ImageColumn("Logo", width="small"),
        "symbol": st.column_config.TextColumn("Symbol", width="small"),
        "name": st.column_config.TextColumn("Name", width="medium"),
        "avg_price_90d": st.column_config.TextColumn("Avg Price (90D)", width="small"),
        "volatility_score": st.column_config.TextColumn("Volatility Score (σ)", width="small"),
    }
)

st.divider()

# ==========================================================
# Biggest 24h Gainers & Losers
# ==========================================================

st.subheader("📊 Biggest 24h Gainers & Losers")

col1, col2 = st.columns(2)

def build_table(df, ascending):
    result = (
        df
        .sort_values("price_change_percentage_24h", ascending=ascending)
        .head(10)
        [["image", "symbol", "name", "current_price", "price_change_percentage_24h"]]
        .copy()
    )
    result["symbol"] = result["symbol"].str.upper()
    result["current_price"] = result["current_price"].map(lambda x: f"${x:,.2f}")
    result["price_change_percentage_24h"] = result["price_change_percentage_24h"].map(
        lambda x: f"🔴 {x:.2f}%" if ascending else f"🟢 {x:.2f}%"
    )
    return result

col_config = {
    "image": st.column_config.ImageColumn("Logo", width="small"),
    "symbol": st.column_config.TextColumn("Symbol", width="small"),
    "name": st.column_config.TextColumn("Name", width="medium"),
    "current_price": st.column_config.TextColumn("Price", width="small"),
    "price_change_percentage_24h": st.column_config.TextColumn("24h Change", width="small"),
}

with col1:
    st.markdown("### 🟢 Top Gainers")
    st.dataframe(
        build_table(coins, ascending=False),
        hide_index=True,
        use_container_width=True,
        column_config=col_config
    )

with col2:
    st.markdown("### 🔴 Top Losers")
    st.dataframe(
        build_table(coins, ascending=True),
        hide_index=True,
        use_container_width=True,
        column_config=col_config
    )

st.divider()

st.markdown("""
<p style='text-align:center; color:#30363d; font-size:0.8rem;'>
Data sourced from CoinGecko API · ITC6050 Group 3 · Spring 2026
</p>
""", unsafe_allow_html=True)