"""Lecture 17: widgets, layout, session state and forms.

Run it with you have to be inside streamlit-dev:

    docker compose up -d --force-recreate

Then open http://localhost:8502
"""
import pandas as pd
import streamlit as st

st.title("Lecture 17: Widgets, Layout and State")


@st.cache_data
def load_items():
    return pd.read_csv("data/orders/Item.csv")


items = load_items()

# ---------------------------------------------------------------- widgets
st.header("1. Widgets are variables")

descriptions = sorted(items["Item_Description"].unique())

with st.sidebar:
    st.subheader("Filters")
    chosen = st.multiselect("Description", descriptions, default=descriptions)
    min_sales = st.slider("Minimum annual sales", 0, 7000, 0, step=100)
    sort_desc = st.checkbox("Sort by sales, highest first", value=True)

filtered = items[items["Item_Description"].isin(chosen) &
                 (items["Item_AnnualSales"] >= min_sales)]
if sort_desc:
    filtered = filtered.sort_values("Item_AnnualSales", ascending=False)

st.write(f"`chosen` is a {type(chosen).__name__}, "
         f"`min_sales` is an {type(min_sales).__name__}, "
         f"`sort_desc` is a {type(sort_desc).__name__}.")

st.metric("Items matching the filter", len(filtered))
st.dataframe(filtered, width="stretch")

# ---------------------------------------------------------------- layout
st.header("2. Layout")

tab_chart, tab_data, tab_notes = st.tabs(["Chart", "Raw data", "Notes"])

with tab_chart:
    st.bar_chart(filtered, x="Item_ID", y="Item_AnnualSales")

with tab_data:
    st.dataframe(filtered, width="stretch")

with tab_notes:
    st.markdown(
        "Tabs hold alternative views of the same thing. Columns hold things "
        "that belong side by side. The sidebar holds the controls."
    )

# ---------------------------------------------------------------- state
st.header("3. Session state")

st.markdown("A plain variable cannot survive a rerun. Session state can.")

broken_count = 0            # reset on every rerun, so this never passes 1

if "count" not in st.session_state:
    st.session_state.count = 0


def increment_by(n):
    st.session_state.count += n


left, middle, right = st.columns(3)
with left:
    if st.button("Plain variable +1"):
        broken_count += 1
    st.write("Plain variable:", broken_count)
with middle:
    st.button("Session state +1", on_click=increment_by, args=(1,))
    st.write("Session state:", st.session_state.count)
with right:
    st.button("Session state +5", on_click=increment_by, args=(5,))
    if st.button("Reset"):
        st.session_state.count = 0

st.caption("Click the left button repeatedly. It never gets past 1.")

# ---------------------------------------------------------------- keys
st.header("4. Widget keys")

st.text_input("Type something", key="typed")
st.write("Read back from session state:", st.session_state.get("typed", ""))

# ---------------------------------------------------------------- forms
st.header("5. Forms")

st.markdown(
    "Inside a form nothing reruns until you press submit, so an expensive "
    "query fires once rather than once per widget."
)

with st.form("item_lookup"):
    item_id = st.selectbox("Item", sorted(items["Item_ID"]))
    show_all_columns = st.checkbox("Show every column")
    submitted = st.form_submit_button("Look it up")

if submitted:
    row = items[items["Item_ID"] == item_id]
    st.dataframe(row if show_all_columns
                 else row[["Item_ID", "Item_Description", "Item_Price"]],
                 width="stretch")
