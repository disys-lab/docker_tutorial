"""Question 1, customer dataset.

    docker compose up -d
    open http://localhost:8511
"""
import csv

import streamlit as st


def load(name):
    with open(f"data/orders/{name}", newline="") as f:
        return list(csv.DictReader(f))


customers = load("Customer.csv")
orders = load("CustomerOrder.csv")
items = load("Item.csv")
order_items = load("Order_Item.csv")


st.header("TODO: state your visualisation question here")
st.write("TODO: a sentence or two of context, if it helps.")


# 1. The sidebar. Two widgets of different types, and both must change what
#    the page shows.
st.sidebar.title("Filters")
# TODO: for example a multiselect of carriers and a slider
# chosen = st.sidebar.multiselect(...)


# Keep the rows that match the sidebar. A plain loop is fine.
shown = []
for order in orders:
    shown.append(order)          # TODO: add your conditions


# 2. At least three metrics, and they must change when the sidebar changes.
a, b, c = st.columns(3)
a.metric("TODO", len(shown))
b.metric("TODO", 0)
c.metric("TODO", 0)


# 3. Lay the charts out in columns or tabs.
tab_one, tab_two = st.tabs(["TODO", "TODO"])

# A chart takes a list of dictionaries. Build the rows first, then draw.
# chart_rows = []
# for ... :
#     chart_rows.append({"X": ..., "Y": ...})
# tab_one.bar_chart(chart_rows, x="X", y="Y")


# 4. The rows behind one chart, hidden until the user asks.
with st.expander("Show the data behind this"):
    st.dataframe(shown, width="stretch", hide_index=True)
