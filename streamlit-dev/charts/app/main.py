"""The same data, drawn with every chart tool Streamlit supports.

    docker compose up -d
    open http://localhost:8506
"""
import csv

import altair as alt
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st

st.title("One Dataset, Six Chart Tools")
st.write("Every chart below shows the same thing: annual sales per item type.")

with open("data/orders/Item.csv", newline="") as f:
    items = list(csv.DictReader(f))

# Add up the sales for each kind of item.
sales = {}
for item in items:
    kind = item["Item_Description"]
    if kind in sales:
        sales[kind] = sales[kind] + int(item["Item_AnnualSales"])
    else:
        sales[kind] = int(item["Item_AnnualSales"])

rows = []
for kind in sales:
    rows.append({"Type": kind, "Sales": sales[kind]})

# Altair, Plotly and Matplotlib want a DataFrame rather than a list.
frame = pd.DataFrame(rows)

st.dataframe(rows, hide_index=True)


st.header("1. Streamlit's own chart")
st.write("Simplest but not very customizable")
st.bar_chart(rows, x="Type", y="Sales")


st.header("2. Altair")
st.write("Doesnt require any installation, not very different from Streamlit's own")
chart = alt.Chart(frame).mark_bar().encode(x="Type", y="Sales")
st.altair_chart(chart, width="stretch")


st.header("3. Plotly")
st.write("Interactive by default allows you to do a bunch of option.")
figure = px.bar(frame, x="Type", y="Sales", title="Annual sales by type")
st.plotly_chart(figure, width="stretch")


st.header("4. Matplotlib")
st.write("Static plot that we are all used to with Python.")
fig, ax = plt.subplots()
ax.bar(frame["Type"], frame["Sales"])
ax.set_xlabel("Type")
ax.set_ylabel("Sales")
st.pyplot(fig)


st.header("5. A map, with st.map")
st.write("Provide latitude and longitude and you can plot maps.")
places = pd.DataFrame({
    "lat": [36.1156, 35.4676, 36.1540],
    "lon": [-97.0584, -97.5164, -95.9928],
})
st.map(places)
