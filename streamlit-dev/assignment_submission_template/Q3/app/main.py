"""Question 3, the broken chart and the fixed one.

    docker compose up -d
    open http://localhost:8514

Draw both versions on this page so you can screenshot them.
"""
import csv
import sys

import streamlit as st

sys.path.insert(0, "data")
from load_reactor import load_reactor          # noqa: E402


def load(name):
    with open(f"data/orders/{name}", newline="") as f:
        return list(csv.DictReader(f))


items = load("Item.csv")
orders = load("CustomerOrder.csv")
readings = load_reactor("data/reactor_sample_5k.csv")

st.title("Question 3: Break the Rules, Then Fix Them")


st.header("The broken chart")
st.write("TODO: name the three things that are wrong with it.")

# TODO: draw a chart that breaks three of the rules from Lecture 15.


st.header("The fixed chart")
st.write("TODO: say what you changed for each of the three faults.")

# TODO: the same data, drawn properly.
