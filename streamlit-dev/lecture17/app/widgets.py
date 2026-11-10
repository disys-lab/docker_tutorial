"""Lecture 17: widgets, layout, session state and forms.

Run it from inside streamlit-dev/lecture17:

    docker compose up -d

Then open http://localhost:8504
"""
import csv

import streamlit as st

st.title("Lecture 17: Widgets, Layout and State")


@st.cache_data
def load_items():
    with open("data/orders/Item.csv", newline="") as f:
        return list(csv.DictReader(f))


items = load_items()

st.header("1. Widgets are variables")

# The list of item types, each one only once.
descriptions = []
for item in items:
    if item["Item_Description"] not in descriptions:
        descriptions.append(item["Item_Description"])
descriptions.sort()

st.sidebar.subheader("Filters")
chosen = st.sidebar.multiselect("Description", descriptions, default=descriptions)
min_sales = st.sidebar.slider("Minimum annual sales", 0, 7000, 0, step=100)
sort_desc = st.sidebar.checkbox("Sort by sales, highest first", value=True)

st.write("chosen is a list:", chosen)
st.write("min_sales is a number:", min_sales)
st.write("sort_desc is True or False:", sort_desc)

# Keep the items that match both filters.
filtered = []
for item in items:
    if item["Item_Description"] in chosen:
        if int(item["Item_AnnualSales"]) >= min_sales:
            filtered.append(item)


def sales_of(item):
    return int(item["Item_AnnualSales"])


if sort_desc:
    filtered.sort(key=sales_of, reverse=True)

st.metric("Items matching the filter", len(filtered))
st.dataframe(filtered, width="stretch")

st.header("2. Layout")

chart_rows = []
for item in filtered:
    chart_rows.append({
        "Item": item["Item_ID"],
        "Sales": int(item["Item_AnnualSales"]),
    })

tab_chart, tab_data, tab_notes = st.tabs(["Chart", "Raw data", "Notes"])
tab_chart.bar_chart(chart_rows, x="Item", y="Sales")
tab_data.dataframe(filtered, width="stretch")
tab_notes.markdown(
    "Tabs hold alternative views of the same thing. Columns hold things "
    "that belong side by side. The sidebar holds the controls."
)

st.header("3. Session state")

st.markdown("A plain variable cannot survive a rerun. Session state can.")

broken_count = 0

if "count" not in st.session_state:
    st.session_state.count = 0


def add_five():
    st.session_state.count = st.session_state.count + 5


left, middle, right = st.columns(3)

if left.button("Plain variable +1"):
    broken_count = broken_count + 1
left.write("Plain variable:")
left.write(broken_count)

if middle.button("Session state +1"):
    st.session_state.count = st.session_state.count + 1
middle.write("Session state:")
middle.write(st.session_state.count)

right.button("Session state +5", on_click=add_five)
if right.button("Reset"):
    st.session_state.count = 0

st.caption("Click the left button repeatedly. It never gets past 1.")

st.header("4. Widget keys")

st.text_input("Type something", key="typed")
st.write("Read back from session state:", st.session_state["typed"])

st.header("5. Forms")

st.markdown(
    "Inside a form nothing reruns until you press submit, so an expensive "
    "query fires once rather than once per widget."
)

item_ids = []
for item in items:
    item_ids.append(item["Item_ID"])
item_ids.sort()

with st.form("item_lookup"):
    wanted = st.selectbox("Item", item_ids)
    show_all_columns = st.checkbox("Show every column")
    submitted = st.form_submit_button("Look it up")

if submitted:
    for item in items:
        if item["Item_ID"] == wanted:
            if show_all_columns:
                st.write(item)
            else:
                st.write({
                    "Item_ID": item["Item_ID"],
                    "Item_Description": item["Item_Description"],
                    "Item_Price": item["Item_Price"],
                })
