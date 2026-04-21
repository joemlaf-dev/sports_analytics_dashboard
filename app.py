import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="College Basketball Analytics Dashboard",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp {
        background-color: #0e1117;
        color: #f5f5f5;
      }
      [data-testid="stSidebar"] {
        background-color: #151a22;
      }
      h1, h2, h3, h4 {
        color: #f9fafb !important;
      }
      .metric-card {
        border: 1px solid #2b3340;
        border-radius: 10px;
        padding: 8px 14px;
        background-color: #111827;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏀 College Basketball Analytics Dashboard")
st.caption("Built-in sample data with efficiency metrics, NET ratings, and interactive filters.")

# Built-in sample data (no external CSV required).
sample_data = [
    ("UConn", "Big East", 31, 4, 3120, 2485, 2710, 0.654),
    ("Houston", "Big 12", 30, 5, 2880, 2358, 2665, 0.671),
    ("Purdue", "Big Ten", 28, 7, 3015, 2594, 2732, 0.638),
    ("Tennessee", "SEC", 27, 8, 2792, 2410, 2648, 0.662),
    ("Arizona", "Big 12", 27, 8, 2981, 2583, 2702, 0.621),
    ("North Carolina", "ACC", 29, 7, 2924, 2504, 2681, 0.605),
    ("Iowa State", "Big 12", 26, 9, 2691, 2317, 2604, 0.649),
    ("Alabama", "SEC", 25, 10, 3042, 2748, 2759, 0.593),
    ("Duke", "ACC", 27, 9, 2862, 2488, 2660, 0.614),
    ("Kansas", "Big 12", 23, 11, 2776, 2555, 2627, 0.646),
    ("Creighton", "Big East", 24, 10, 2839, 2521, 2651, 0.612),
    ("Marquette", "Big East", 24, 10, 2810, 2493, 2640, 0.601),
]

df = pd.DataFrame(
    sample_data,
    columns=[
        "Team",
        "Conference",
        "Wins",
        "Losses",
        "Points_For",
        "Points_Against",
        "Possessions",
        "Opp_Win_Pct",
    ],
)

# Metrics:
# Offensive efficiency = points scored per 100 possessions.
# Defensive efficiency = points allowed per 100 possessions.
# NET rating = offensive efficiency - defensive efficiency.
# Strength of schedule = opponent win percentage (scaled to 100).
df["Games"] = df["Wins"] + df["Losses"]
df["Win_Pct"] = df["Wins"] / df["Games"]
df["Off_Eff"] = (df["Points_For"] / df["Possessions"]) * 100
df["Def_Eff"] = (df["Points_Against"] / df["Possessions"]) * 100
df["NET_Rating"] = df["Off_Eff"] - df["Def_Eff"]
df["SOS"] = df["Opp_Win_Pct"] * 100

df = df.sort_values("NET_Rating", ascending=False).reset_index(drop=True)
df["Rank"] = df.index + 1

st.sidebar.header("Filters")
min_wins = st.sidebar.slider(
    "Minimum wins",
    min_value=int(df["Wins"].min()),
    max_value=int(df["Wins"].max()),
    value=int(df["Wins"].min()),
)

conference_options = ["All"] + sorted(df["Conference"].unique().tolist())
conference = st.sidebar.selectbox("Conference", conference_options, index=0)

filtered_df = df[df["Wins"] >= min_wins].copy()
if conference != "All":
    filtered_df = filtered_df[filtered_df["Conference"] == conference]

if filtered_df.empty:
    st.warning("No teams match these filters. Try lowering minimum wins or changing conference.")
    st.stop()

filtered_df = filtered_df.sort_values("NET_Rating", ascending=False).reset_index(drop=True)
filtered_df["Rank"] = filtered_df.index + 1

metric_cols = st.columns(4)
metric_cols[0].metric("Teams shown", f"{len(filtered_df)}")
metric_cols[1].metric("Avg Off Eff", f"{filtered_df['Off_Eff'].mean():.2f}")
metric_cols[2].metric("Avg Def Eff", f"{filtered_df['Def_Eff'].mean():.2f}")
metric_cols[3].metric("Avg NET", f"{filtered_df['NET_Rating'].mean():.2f}")

st.markdown("---")

left_col, right_col = st.columns([1.2, 1])

with left_col:
    st.subheader("Offensive vs Defensive Efficiency")
    scatter_fig = px.scatter(
        filtered_df,
        x="Off_Eff",
        y="Def_Eff",
        text="Team",
        color="NET_Rating",
        color_continuous_scale="RdYlGn",
        size="Wins",
        hover_data={
            "Team": True,
            "Conference": True,
            "Wins": True,
            "Losses": True,
            "Off_Eff": ":.2f",
            "Def_Eff": ":.2f",
            "NET_Rating": ":.2f",
            "SOS": ":.2f",
        },
    )
    scatter_fig.update_traces(textposition="top center")
    scatter_fig.update_layout(
        template="plotly_dark",
        xaxis_title="Offensive Efficiency (Points per 100 possessions)",
        yaxis_title="Defensive Efficiency (Points allowed per 100 possessions)",
        coloraxis_colorbar_title="NET",
        height=520,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    # Lower defensive efficiency is better; reverse axis for intuitive reading.
    scatter_fig.update_yaxes(autorange="reversed")
    st.plotly_chart(scatter_fig, use_container_width=True)

with right_col:
    st.subheader("NET Ratings")
    net_fig = px.bar(
        filtered_df.sort_values("NET_Rating", ascending=True),
        x="NET_Rating",
        y="Team",
        orientation="h",
        color="Conference",
        text="NET_Rating",
    )
    net_fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    net_fig.update_layout(
        template="plotly_dark",
        xaxis_title="NET Rating",
        yaxis_title="",
        height=520,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(net_fig, use_container_width=True)

st.markdown("---")
st.subheader("Sortable Team Rankings")

table_df = filtered_df[
    [
        "Rank",
        "Team",
        "Conference",
        "Wins",
        "Losses",
        "Win_Pct",
        "Off_Eff",
        "Def_Eff",
        "NET_Rating",
        "SOS",
    ]
].copy()

for col in ["Win_Pct", "Off_Eff", "Def_Eff", "NET_Rating", "SOS"]:
    table_df[col] = table_df[col].round(3)

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Win_Pct": st.column_config.NumberColumn("Win %", format="%.3f"),
        "Off_Eff": st.column_config.NumberColumn("Off Eff", format="%.3f"),
        "Def_Eff": st.column_config.NumberColumn("Def Eff", format="%.3f"),
        "NET_Rating": st.column_config.NumberColumn("NET", format="%.3f"),
        "SOS": st.column_config.NumberColumn("SOS", format="%.2f"),
    },
)

st.caption(
    "Metric definitions: Off Eff = points scored per 100 possessions; "
    "Def Eff = points allowed per 100 possessions; NET = Off Eff - Def Eff; "
    "SOS = opponent win percentage x 100."
)
