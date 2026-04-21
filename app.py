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
      div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #111827, #0f172a);
        border: 1px solid #263043;
        padding: 10px 12px;
        border-radius: 12px;
      }
      .section-subtitle {
        color: #9ca3af;
        margin-bottom: 0.75rem;
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

# Team logo URLs (ESPN CDN) for visual branding.
team_logos = {
    "UConn": "https://a.espncdn.com/i/teamlogos/ncaa/500/41.png",
    "Houston": "https://a.espncdn.com/i/teamlogos/ncaa/500/248.png",
    "Purdue": "https://a.espncdn.com/i/teamlogos/ncaa/500/2509.png",
    "Tennessee": "https://a.espncdn.com/i/teamlogos/ncaa/500/2633.png",
    "Arizona": "https://a.espncdn.com/i/teamlogos/ncaa/500/12.png",
    "North Carolina": "https://a.espncdn.com/i/teamlogos/ncaa/500/153.png",
    "Iowa State": "https://a.espncdn.com/i/teamlogos/ncaa/500/66.png",
    "Alabama": "https://a.espncdn.com/i/teamlogos/ncaa/500/333.png",
    "Duke": "https://a.espncdn.com/i/teamlogos/ncaa/500/150.png",
    "Kansas": "https://a.espncdn.com/i/teamlogos/ncaa/500/2305.png",
    "Creighton": "https://a.espncdn.com/i/teamlogos/ncaa/500/156.png",
    "Marquette": "https://a.espncdn.com/i/teamlogos/ncaa/500/269.png",
}

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
df["Logo_URL"] = df["Team"].map(team_logos).fillna("")
df["Team_Label"] = df["Team"]

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

selected_team = st.sidebar.selectbox(
    "Highlight team",
    filtered_df["Team"].tolist(),
    index=0,
)

team_row = filtered_df[filtered_df["Team"] == selected_team].iloc[0]
avg_off = filtered_df["Off_Eff"].mean()
avg_def = filtered_df["Def_Eff"].mean()
avg_net = filtered_df["NET_Rating"].mean()
avg_sos = filtered_df["SOS"].mean()

st.markdown("### Interactive Team Snapshot")
snapshot_cols = st.columns([0.55, 1, 1, 1, 1, 1])
with snapshot_cols[0]:
    if team_row["Logo_URL"]:
        st.image(team_row["Logo_URL"], width=64)
snapshot_cols[1].metric("Team", team_row["Team"])
snapshot_cols[2].metric("Record", f"{int(team_row['Wins'])}-{int(team_row['Losses'])}")
snapshot_cols[3].metric("Off Eff", f"{team_row['Off_Eff']:.2f}", f"{team_row['Off_Eff'] - avg_off:+.2f} vs avg")
snapshot_cols[4].metric("Def Eff", f"{team_row['Def_Eff']:.2f}", f"{avg_def - team_row['Def_Eff']:+.2f} better than avg")
snapshot_cols[5].metric("NET / SOS", f"{team_row['NET_Rating']:.2f} / {team_row['SOS']:.1f}", f"{team_row['NET_Rating'] - avg_net:+.2f} NET")

st.markdown(
    f"<div class='section-subtitle'>{selected_team} rank: #{int(team_row['Rank'])} in current filtered view.</div>",
    unsafe_allow_html=True,
)

overview_tab, team_tab = st.tabs(["Overview", "Team Explorer"])

with overview_tab:
    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.subheader("Offensive vs Defensive Efficiency")
        scatter_fig = px.scatter(
            filtered_df,
            x="Off_Eff",
            y="Def_Eff",
            text="Team_Label",
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
            y="Team_Label",
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
            "Logo_URL",
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
            "Logo_URL": st.column_config.ImageColumn("Logo", help="Team logo"),
            "Win_Pct": st.column_config.NumberColumn("Win %", format="%.3f"),
            "Off_Eff": st.column_config.NumberColumn("Off Eff", format="%.3f"),
            "Def_Eff": st.column_config.NumberColumn("Def Eff", format="%.3f"),
            "NET_Rating": st.column_config.NumberColumn("NET", format="%.3f"),
            "SOS": st.column_config.NumberColumn("SOS", format="%.2f"),
        },
    )

with team_tab:
    st.subheader(f"{selected_team} Team Explorer")
    compare_df = filtered_df.copy()
    compare_df["Selected Team"] = compare_df["Team"].apply(
        lambda team: selected_team if team == selected_team else "Other Teams"
    )
    compare_fig = px.scatter(
        compare_df,
        x="SOS",
        y="NET_Rating",
        color="Selected Team",
        color_discrete_map={selected_team: "#38bdf8", "Other Teams": "#64748b"},
        size="Wins",
        text="Team_Label",
        hover_data={
            "Team": True,
            "Conference": True,
            "Wins": True,
            "Losses": True,
            "SOS": ":.2f",
            "NET_Rating": ":.2f",
        },
        title="NET Rating vs Strength of Schedule",
    )
    compare_fig.update_traces(textposition="top center")
    compare_fig.update_layout(template="plotly_dark", height=500, margin=dict(l=20, r=20, t=45, b=20))
    st.plotly_chart(compare_fig, use_container_width=True)

    rank_change_df = filtered_df.sort_values("Off_Eff", ascending=False).reset_index(drop=True)
    rank_change_df["Off_Rank"] = rank_change_df.index + 1
    rank_change_df = rank_change_df.sort_values("Def_Eff", ascending=True).reset_index(drop=True)
    rank_change_df["Def_Rank"] = rank_change_df.index + 1
    rank_row = rank_change_df[rank_change_df["Team"] == selected_team].iloc[0]

    rank_cols = st.columns(4)
    rank_cols[0].metric("NET Rank", f"#{int(team_row['Rank'])}")
    rank_cols[1].metric("Offense Rank", f"#{int(rank_row['Off_Rank'])}")
    rank_cols[2].metric("Defense Rank", f"#{int(rank_row['Def_Rank'])}")
    rank_cols[3].metric("SOS Rank", f"#{int(filtered_df['SOS'].rank(ascending=False, method='min')[filtered_df['Team'] == selected_team].iloc[0])}")

st.caption(
    "Metric definitions: Off Eff = points scored per 100 possessions; "
    "Def Eff = points allowed per 100 possessions; NET = Off Eff - Def Eff; "
    "SOS = opponent win percentage x 100."
)
