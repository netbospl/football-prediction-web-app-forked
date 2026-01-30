import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.utils.config import Config as cfg
from src.frontend.data import load_data, aggregate_df, aggregate_by_date
from src.frontend.metrics import get_metrics, metric_dashboard
from src.frontend.match_report import ResultReport, FixtureReport
from src.trades.recommend import get_recommended_trades, TradeConfig
from src.db.client import init_db, create_run, save_predictions, save_trades, get_trade_performance


METRICS = ["Finished Games",
           "Accuracy (%)",
           "ROI (%)"]


# ---- INITIALIZE DATABASE -------
@st.cache_resource
def initialize_database():
    """Initialize database on first load."""
    return init_db()


# Initialize DB (runs once per session)
initialize_database()


# ---- MAIN -------
st.title("Football Prediction Web App")

# Sidebar configuration
st.sidebar.header("Configuration")
storage_info = f"Storage: **{cfg.STORAGE_BACKEND}**"
if cfg.use_azure():
    storage_info += " (Azure connected)"
st.sidebar.markdown(storage_info)

selected_leagues = st.multiselect("Select league: ", cfg.LEAGUES.keys())
df = load_data(selected_leagues)

# Check if we have data
if df.empty:
    st.warning("No prediction data available. Run the pipeline first: `python run_pipelines.py`")
    st.stop()

# ---- DISPLAY METRICS DASHBOARD -------
agg_df = aggregate_df(df)
overall_metrics = get_metrics(agg_df)
c = st.container()
metric_dashboard(c, "Stats:", overall_metrics[METRICS].loc[0,:])

# ---- DISPLAY METRICS TABLE -------
agg_df = aggregate_df(df, "Predicted result").reset_index().sort_values("PRED_RESULT_NUM", ascending=False)
metrics_table = get_metrics(agg_df)[["Predicted result"] + METRICS]
st.table(metrics_table)

# ---- DISPLAY ROLLING-28D METRICS -------
st.subheader("Stats over time:")
rlng = st.slider("Moving average rollup (days):", 1, 28, 14)
agg_df = aggregate_by_date(df, "F_DATE", rlng)
date_metrics = get_metrics(agg_df, fmt=False)
st.line_chart(date_metrics[METRICS[1:]])


# ---- RECOMMENDED TRADES SECTION -------
st.header("Recommended Trades")
st.markdown("""
Trades are recommended based on model predictions vs market odds.
**Edge** = Model confidence - Market implied probability.
""")

# Trade filters in sidebar
st.sidebar.subheader("Trade Filters")
min_odds = st.sidebar.slider("Minimum odds:", 1.1, 3.0, 1.2, 0.1)
max_odds = st.sidebar.slider("Maximum odds:", 2.0, 15.0, 10.0, 0.5)
min_edge = st.sidebar.slider("Minimum edge (%):", 0.0, 20.0, 5.0, 1.0) / 100
bankroll = st.sidebar.number_input("Bankroll:", min_value=10.0, max_value=10000.0, value=100.0, step=10.0)
top_n = st.sidebar.slider("Top trades to show:", 1, 25, 10)

# Date filter for upcoming matches
today = datetime.now().date()
date_range = st.selectbox(
    "Date range:",
    ["Today", "Next 3 days", "Next 7 days", "All upcoming"],
    index=2
)

# Create trade config
trade_config = TradeConfig(
    min_edge=min_edge,
    min_odds=min_odds,
    max_odds=max_odds,
    bankroll=bankroll,
    top_n=top_n
)

# Filter by date range
if date_range == "Today":
    date_filter = df["F_DATE"].dt.date == today
elif date_range == "Next 3 days":
    date_filter = (df["F_DATE"].dt.date >= today) & (df["F_DATE"].dt.date <= today + timedelta(days=3))
elif date_range == "Next 7 days":
    date_filter = (df["F_DATE"].dt.date >= today) & (df["F_DATE"].dt.date <= today + timedelta(days=7))
else:
    date_filter = df["F_DATE"].dt.date >= today

# Get upcoming fixtures only
upcoming_df = df[date_filter].copy()

# Get recommendations
trades = get_recommended_trades(upcoming_df, trade_config)

if not trades:
    st.info("No trades meet the current criteria. Try adjusting the filters or check back when new fixtures are available.")
else:
    # Display trade summary
    total_stake = sum(t.stake for t in trades)
    avg_edge = sum(t.edge for t in trades) / len(trades) * 100
    st.markdown(f"**{len(trades)} trades** | Total stake: **{total_stake:.2f}** | Avg edge: **{avg_edge:.1f}%**")

    # Display trades table
    trade_data = []
    for t in trades:
        side_emoji = {"H": "🏠", "D": "🤝", "A": "✈️"}.get(t.side, "")
        trade_data.append({
            "Date": t.date,
            "Match": f"{t.home_team} vs {t.away_team}",
            "League": t.division,
            "Pick": f"{side_emoji} {t.side}",
            "Odds": t.odds,
            "Model %": f"{t.model_confidence*100:.1f}",
            "Market %": f"{t.implied_prob*100:.1f}",
            "Edge %": f"{t.edge*100:.1f}",
            "Score": f"{t.score:.3f}",
            "Stake": f"{t.stake:.2f}"
        })

    trade_df = pd.DataFrame(trade_data)
    st.dataframe(trade_df, use_container_width=True)

    # Detailed view with expanders
    st.subheader("Trade Details")
    for t in trades:
        with st.expander(f"{t.date} | {t.home_team} vs {t.away_team} → {t.side} @ {t.odds}"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Edge", f"{t.edge*100:.2f}%")
            col2.metric("EV", f"{t.ev:.4f}")
            col3.metric("Stake", f"{t.stake:.2f}")

            st.markdown("**Rationale:**")
            for bullet in t.rationale.get("bullets", []):
                st.markdown(f"- {bullet}")

            if t.rationale.get("shap_drivers"):
                st.markdown("**Key Features (SHAP):**")
                shap_data = []
                for feat, val in t.rationale["shap_drivers"].items():
                    direction = "➕" if val > 0 else "➖"
                    shap_data.append({"Feature": feat, "Impact": direction, "SHAP": f"{val:.4f}"})
                st.table(pd.DataFrame(shap_data))

    # Save trades button
    st.divider()
    col1, col2 = st.columns([1, 3])
    if col1.button("💾 Save Trades to DB"):
        run_id = create_run(notes=f"UI session - {len(trades)} trades recommended")
        # Save predictions for the upcoming matches
        save_predictions(run_id, upcoming_df)
        # Save trades
        trade_dicts = [t.to_dict() for t in trades]
        count = save_trades(run_id, trade_dicts)
        st.success(f"Saved {count} trades to database (Run ID: {run_id})")

    # Show historical performance if available
    perf = get_trade_performance()
    if perf.get("settled_trades", 0) > 0:
        col2.markdown(
            f"**Historical:** {perf['wins']}/{perf['settled_trades']} wins "
            f"({perf['win_rate']*100:.1f}%) | ROI: {perf['roi']*100:.1f}%"
        )


# ---- RESULTS -------
st.divider()
c = st.container()
res_c = c.columns(3)
res_c[0].header("Results:")
n_games = res_c[-1].selectbox("Select how many games to show:", [25, 50, 100, "All"])
dates = (df.head(n_games) if n_games != "All" else df).F_DATE.unique()
results = df.loc[df.F_DATE.isin(dates),:]

# ---- DISPLAY DATE METRICS -------
for date, date_df in list(results.groupby("F_DATE"))[::-1]:
    pretty_date = date.strftime("%d %b")
    date_metrics = get_metrics(aggregate_df(date_df))[METRICS].loc[0,:]
    c = st.container()
    metric_dashboard(c, pretty_date, date_metrics)

    # ---- DISPLAY MATCHES -------
    for idx, row in date_df.iterrows():
        res = row['F_RESULT']
        report = ResultReport if res else FixtureReport
        title = report(row).render()
