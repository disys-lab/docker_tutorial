"""Lecture 16: the things Streamlit puts on a page.

Run it with you have to be inside streamlit-dev:

    docker compose up -d --force-recreate

Then open http://localhost:8502
"""
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------- text
st.title("Lecture 16: Putting Things on the Page")
st.caption("Every element below is one line of Python.")

st.header("Text and structure")
st.subheader("A subheading")
st.markdown("Markdown works, so you get **bold**, *italic* and `code` for free.")
st.code("SELECT * FROM customerorder;", language="sql")

# ---------------------------------------------------------------- magic
st.header("Magic, and st.write")

st.write("st.write takes several arguments at once:", 42, [1, 2, 3])

# A bare variable on its own line also displays. That is "magic".
# Uncomment the next two lines to see it.
# message = "this appeared without st.write"
# message

# ---------------------------------------------------------------- caching
st.header("Caching")


@st.cache_data
def load_items():
    """Read the CSV once, not on every rerun."""
    return pd.read_csv("data/orders/Item.csv")


items = load_items()
st.write(f"Loaded {len(items)} items. Interact with anything on this page and "
         "note that the file is not read again.")

# ---------------------------------------------------------------- tables
st.header("Showing a table")

left, right = st.columns(2)
with left:
    st.caption("st.dataframe — interactive")
    st.dataframe(items, width="stretch")
with right:
    st.caption("st.table — static")
    st.table(items.head(5))

# ---------------------------------------------------------------- metrics
st.header("A single number")

a, b, c = st.columns(3)
a.metric("Items", len(items))
b.metric("Mean price", f"${items['Item_Price'].mean():.2f}")
c.metric("Total annual sales", f"{items['Item_AnnualSales'].sum():,}")

# ---------------------------------------------------------------- charts
st.header("The built-in charts")

by_desc = (items.groupby("Item_Description")["Item_AnnualSales"]
                .sum()
                .reset_index()
                .sort_values("Item_AnnualSales", ascending=False))

st.caption("st.bar_chart")
st.bar_chart(by_desc, x="Item_Description", y="Item_AnnualSales")

st.caption("st.scatter_chart — price against annual sales")
st.scatter_chart(items, x="Item_Price", y="Item_AnnualSales")

with st.expander("Show the dataframe behind these charts"):
    st.dataframe(by_desc, width="stretch")
