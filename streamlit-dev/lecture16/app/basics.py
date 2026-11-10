"""Lecture 16: the things Streamlit puts on a page.

Run it from inside streamlit-dev/lecture16:

    docker compose up -d

Then open http://localhost:8503
"""
import csv

import streamlit as st

st.title("Lecture 16: Putting Things on the Page")
st.caption("Every element below is one line of Python.")

st.header("Text and structure")
st.subheader("A subheading")
st.markdown("Markdown works, so you get **bold**, *italic* and `code` for free.")
st.code("SELECT * FROM customerorder;", language="sql")

st.header("Magic, and st.write")
st.write("st.write takes several arguments at once:", 42, [1, 2, 3])

# A bare variable on its own line also displays. That is "magic".
# Uncomment the next two lines to see it.
# message = "this appeared without st.write"
# message

st.header("Reading the data")


@st.cache_data
def load_items():
    with open("data/orders/Item.csv", newline="") as f:
        return list(csv.DictReader(f))


items = load_items()

st.write("Loaded", len(items), "items. Interact with the page and notice that "
         "the file is not read again.")
st.write("One row looks like this:", items[0])

st.header("Showing a table")

left, right = st.columns(2)
left.caption("st.dataframe — interactive")
left.dataframe(items, width="stretch")
right.caption("st.table — static, first five rows")
right.table(items[:5])

st.header("A single number")

total_sales = 0
total_price = 0.0
for item in items:
    total_sales = total_sales + int(item["Item_AnnualSales"])
    total_price = total_price + float(item["Item_Price"])

mean_price = total_price / len(items)

a, b, c = st.columns(3)
a.metric("Items", len(items))
b.metric("Mean price", "$" + str(round(mean_price, 2)))
c.metric("Total annual sales", total_sales)

st.header("The built-in charts")

# Add up the sales for each kind of item.
sales_by_type = {}
for item in items:
    kind = item["Item_Description"]
    sales = int(item["Item_AnnualSales"])
    if kind in sales_by_type:
        sales_by_type[kind] = sales_by_type[kind] + sales
    else:
        sales_by_type[kind] = sales

by_type_rows = []
for kind in sales_by_type:
    by_type_rows.append({"Type": kind, "Sales": sales_by_type[kind]})

st.caption("st.bar_chart")
st.bar_chart(by_type_rows, x="Type", y="Sales")

# A chart needs numbers, and the CSV gives us text, so convert first.
price_rows = []
for item in items:
    price_rows.append({
        "Price": float(item["Item_Price"]),
        "Sales": int(item["Item_AnnualSales"]),
    })

st.caption("st.scatter_chart — price against annual sales")
st.scatter_chart(price_rows, x="Price", y="Sales")

with st.expander("Show the numbers behind the bar chart"):
    st.dataframe(by_type_rows, width="stretch")
