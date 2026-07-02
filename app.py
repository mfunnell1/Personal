import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Cricket Shot Analysis", layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("ball_by_ball.csv")

    df = df.sort_values(
        ["Match", "Innings", "Over", "Ball"]
    )

    seam = [
        "RFM",
        "RM",
        "RF",
        "LFM",
        "LM",
        "LF"
    ]

    spin = [
        "ROB",
        "LOB",
        "RLB",
        "LLB"
    ]

    df["Bowling Group"] = "Unknown"

    df.loc[
        df["Bowler Type"].isin(seam),
        "Bowling Group"
    ] = "Seam"

    df.loc[
        df["Bowler Type"].isin(spin),
        "Bowling Group"
    ] = "Spin"

    return df

df = load_data()

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("Filters")

batter = st.sidebar.selectbox(
    "Batter",
    sorted(df["Batter"].dropna().unique())
)

bowler_type = st.sidebar.selectbox(
    "Bowler Type",
    ["All", "Seam", "Spin"]
)

dots_required = st.sidebar.selectbox(
    "Consecutive Dots",
    [2,3]
)

# -----------------------------
# CREATE PREVIOUS DOTS
# -----------------------------

def create_previous_dot_flag(group):

    runs = group["Runs"]

    if dots_required == 2:
        group["AfterDots"] = (
            runs.shift(1).eq(0)
            &
            runs.shift(2).eq(0)
        )

    elif dots_required == 3:
        group["AfterDots"] = (
            runs.shift(1).eq(0)
            &
            runs.shift(2).eq(0)
            &
            runs.shift(3).eq(0)
        )

    return group


df = (
    df
    .groupby(
        ["Match","Innings","Over","Batter"],
        group_keys=False
    )
    .apply(create_previous_dot_flag)
)

# -----------------------------
# FILTER
# -----------------------------

filtered = df[df["Batter"] == batter]

if bowler_type != "All":
    filtered = filtered[
        filtered["Bowler Type"] == bowler_type
    ]

filtered = filtered[
    filtered["AfterDots"] == True
]

# -----------------------------
# RESULTS
# -----------------------------

st.title("Shot Selection After Consecutive Dot Balls")

st.subheader(batter)

if len(filtered)==0:

    st.warning("No examples found.")

else:

    shot_summary = (
        filtered["Shot"]
        .value_counts()
        .reset_index()
    )

    shot_summary.columns = [
        "Shot",
        "Count"
    ]

    shot_summary["Percent"] = (
        shot_summary["Count"]
        /
        shot_summary["Count"].sum()
        *100
    ).round(1)

    st.dataframe(
        shot_summary,
        use_container_width=True
    )

    fig = px.bar(
        shot_summary,
        x="Shot",
        y="Percent",
        text="Percent"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.metric(
        "Total Opportunities",
        len(filtered)
    )
