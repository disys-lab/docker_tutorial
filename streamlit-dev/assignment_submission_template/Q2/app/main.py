"""Question 2, the three charts.

    docker compose up -d
    open http://localhost:8513

Both datasets are loaded below. Pick whichever suits each chart, and say on
the page which one you used.
"""
import csv
import sys

import streamlit as st

sys.path.insert(0, "data")
from load_reactor import load_reactor          # noqa: E402


def load(name):
    with open(f"data/orders/{name}", newline="") as f:
        return list(csv.DictReader(f))


customers = load("Customer.csv")
orders = load("CustomerOrder.csv")
items = load("Item.csv")
order_items = load("Order_Item.csv")
readings = load_reactor("data/reactor_sample_5k.csv")

st.title("Question 2: Three Charts")


# ---------------------------------------------------------------- over time
st.header("1. Over time")
st.write("TODO: the question this chart answers, in one sentence.")
st.caption("TODO: which dataset this uses.")

# chart_rows = []
# for ... :
#     chart_rows.append({"X": ..., "Y": ...})
# st.line_chart(chart_rows, x="X", y="Y")


# ---------------------------------------------------------------- categories
st.header("2. Comparing categories")
st.write("TODO: the question this chart answers, in one sentence.")
st.caption("TODO: which dataset this uses.")

# Counting by category is a dictionary and a loop:
# counts = {}
# for row in ... :
#     name = row["..."]
#     if name in counts:
#         counts[name] = counts[name] + 1
#     else:
#         counts[name] = 1


# ---------------------------------------------------------------- your choice
st.header("3. Your own chart")
st.write("TODO: the question this chart answers, in one sentence.")
st.caption("TODO: which dataset this uses.")
