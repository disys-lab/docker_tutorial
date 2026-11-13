"""Question 1, reactor dataset.

    docker compose up -d
    open http://localhost:8512
"""
import sys

import streamlit as st

sys.path.insert(0, "data")
from load_reactor import load_reactor          # noqa: E402

# Each reading is a dictionary:
#   {"Timestamp_min": 0, "Reactor_Temp_C": 85.0,
#    "Pressure_atm": 3.2, "Reactor_Run_ID": "1"}
readings = load_reactor("data/reactor_sample_5k.csv")

runs = []
for reading in readings:
    if reading["Reactor_Run_ID"] not in runs:
        runs.append(reading["Reactor_Run_ID"])
runs.sort(key=int)


# ---------------------------------------------------------------- your question
st.header("TODO: state your visualisation question here")
st.write("TODO: a sentence or two of context, if it helps.")


# ---------------------------------------------------------------- 1. sidebar
# Two widgets of different types. Both must change what the page shows.
st.sidebar.title("Filters")
# TODO: for example a selectbox of runs and a slider on temperature
# run = st.sidebar.selectbox("Run", runs)


# ---------------------------------------------------------------- filtering
shown = []
for reading in readings:
    shown.append(reading)        # TODO: add your conditions


# ---------------------------------------------------------------- 2. metrics
a, b, c = st.columns(3)
a.metric("Readings", len(shown))
b.metric("TODO", 0)
c.metric("TODO", 0)


# ---------------------------------------------------------------- 3. layout
tab_one, tab_two = st.tabs(["TODO", "TODO"])

# A chart takes a list of dictionaries. Build the rows first, then draw.
# chart_rows = []
# for reading in shown:
#     chart_rows.append({"Minute": reading["Timestamp_min"],
#                        "Temperature": reading["Reactor_Temp_C"]})
# tab_one.line_chart(chart_rows, x="Minute", y="Temperature")


# ---------------------------------------------------------------- 4. the table
with st.expander("Show the data behind this"):
    st.dataframe(shown, width="stretch", hide_index=True)
