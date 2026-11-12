"""The warehouse dashboard: Streamlit in front of MySQL and Redis.

Run it from inside streamlit-dev/lecture18:

    docker compose up -d

Then open http://localhost:8505 and press the load button.
"""
import pymysql
import redis
import streamlit as st

from seed import already_seeded, load_everything

st.set_page_config(page_title="Warehouse Dashboard", layout="wide")


def get_mysql():
    return pymysql.connect(host="mysql", port=3306, user="root",
                           password="OSUGoPokes", database="iem4723_streamlit",
                           connect_timeout=5, read_timeout=10)


def get_redis():
    return redis.Redis(host="redis", port=6379, decode_responses=True)


def get_orders():
    """Read every order, newest query every time the page runs."""
    conn = get_mysql()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT co.Order_Num, co.Order_Date, co.Order_Carrier,
               c.Customer_Num, c.Customer_LastName, c.Customer_State
        FROM customerorder co
          JOIN customer c ON co.Customer_Num = c.Customer_Num
        ORDER BY co.Order_Date
    """)

    orders = []
    for row in cursor.fetchall():
        orders.append({
            "Order_Num": row[0],
            "Order_Date": str(row[1]),
            "Carrier": row[2],
            "Customer_Num": row[3],
            "Last_Name": row[4],
            "State": row[5],
        })

    cursor.close()
    conn.close()
    return orders


# ---------------------------------------------------------------- loading
# A button is True only on the run where it was clicked, so the work goes
# inside the if. The script then runs again from the top.
def load_button(label, key):
    if not st.button(label, key=key, type="primary"):
        return False
    with st.spinner("Loading the warehouse data..."):
        tables, keys = load_everything()
    st.session_state.last_load = (tables, keys)
    return True


try:
    seeded = already_seeded()
except Exception as exc:                                  # noqa: BLE001
    st.title("Warehouse Dashboard")
    st.error("Cannot reach MySQL. Is the stack up?")
    st.exception(exc)
    st.stop()

if not seeded:
    st.title("Warehouse Dashboard")
    st.warning("The database is empty. Load the data to get started.")
    if load_button("Load the warehouse data", "load_first"):
        st.rerun()
    st.stop()

if "last_load" in st.session_state:
    tables, keys = st.session_state.pop("last_load")
    st.success(f"Loaded {sum(tables.values())} rows and {keys} Redis keys.")

# ---------------------------------------------------------------- sidebar
orders = get_orders()

carriers = []
states = []
for order in orders:
    if order["Carrier"] not in carriers:
        carriers.append(order["Carrier"])
    if order["State"] not in states:
        states.append(order["State"])
carriers.sort()
states.sort()

st.sidebar.title("Filters")
chosen_carriers = st.sidebar.multiselect("Carrier", carriers, default=carriers)
chosen_states = st.sidebar.multiselect("Customer state", states, default=states)

st.sidebar.divider()
st.sidebar.caption("Reloading drops every table and rebuilds it from the CSVs.")
confirmed = st.sidebar.checkbox("Yes, reload the data")
with st.sidebar:
    if confirmed and load_button("Reload the data", "reload"):
        st.rerun()

# ---------------------------------------------------------------- the page
st.title("Warehouse Dashboard")
st.caption("MySQL for the orders, Redis for the item rankings. "
           "Every figure is read fresh on each interaction.")

shown = []
for order in orders:
    if order["Carrier"] in chosen_carriers and order["State"] in chosen_states:
        shown.append(order)

customers = []
for order in shown:
    if order["Customer_Num"] not in customers:
        customers.append(order["Customer_Num"])

a, b, c = st.columns(3)
a.metric("Orders", len(shown))
b.metric("Customers", len(customers))
c.metric("Carriers", len(chosen_carriers))

if not shown:
    st.info("No orders match these filters.")
    st.stop()

tab_orders, tab_items = st.tabs(["Orders", "Top items"])

# orders per carrier, counted with a plain loop
per_carrier = {}
for order in shown:
    name = order["Carrier"]
    if name in per_carrier:
        per_carrier[name] = per_carrier[name] + 1
    else:
        per_carrier[name] = 1

chart_rows = []
for name in per_carrier:
    chart_rows.append({"Carrier": name, "Orders": per_carrier[name]})

tab_orders.subheader("Orders by carrier")
tab_orders.bar_chart(chart_rows, x="Carrier", y="Orders")
with tab_orders.expander("Show the orders"):
    st.dataframe(shown, width="stretch", hide_index=True)

tab_items.subheader("Top sellers, from the Redis sorted set")
how_many = tab_items.slider("How many", 3, 15, 5)

r = get_redis()
top_rows = []
for item_id, score in r.zrevrange("items:by_sales", 0, how_many - 1, withscores=True):
    fields = r.hgetall(f"item:{item_id}")
    top_rows.append({
        "Item_ID": item_id,
        "Description": fields.get("Item_Description", ""),
        "Annual sales": int(score),
    })

tab_items.dataframe(top_rows, width="stretch", hide_index=True)
tab_items.bar_chart(top_rows, x="Item_ID", y="Annual sales")
