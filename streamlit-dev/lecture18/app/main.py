"""The warehouse dashboard: Streamlit in front of MySQL and Redis.

This is the app the stack runs by default. It assumes `app/seed.py` has been
run once to load the database.

    docker compose up -d --force-recreate
    docker compose exec streamlit python app/seed.py

Then open http://localhost:8502
"""
import pandas as pd
import pymysql
import redis
import streamlit as st

st.set_page_config(page_title="Warehouse Dashboard", layout="wide")


# ------------------------------------------------------------------ connections
# A connection is a RESOURCE: opened once, shared by every session.
@st.cache_resource
def get_mysql():
    return pymysql.connect(host="mysql", port=3306, user="root",
                           password="OSUGoPokes", database="iem4723_streamlit")


@st.cache_resource
def get_redis():
    return redis.Redis(host="redis", port=6379, decode_responses=True)


# A query result is DATA: copied per caller, and allowed to go stale for 5 min.
@st.cache_data(ttl=300)
def query(sql, params=None):
    cur = get_mysql().cursor()
    cur.execute(sql, params or ())
    cols = [d[0] for d in cur.description]
    return pd.DataFrame(cur.fetchall(), columns=cols)


# ------------------------------------------------------------------ sidebar
st.sidebar.title("Filters")

try:
    carriers = query("SELECT DISTINCT Order_Carrier FROM customerorder "
                     "ORDER BY Order_Carrier")["Order_Carrier"].tolist()
except Exception as exc:                      # noqa: BLE001
    st.error(
        "Could not read from MySQL. Has the database been seeded?\n\n"
        "    docker compose exec streamlit python app/seed.py"
    )
    st.exception(exc)
    st.stop()

chosen_carriers = st.sidebar.multiselect("Carrier", carriers, default=carriers)
states = query("SELECT DISTINCT Customer_State FROM customer "
               "ORDER BY Customer_State")["Customer_State"].tolist()
chosen_states = st.sidebar.multiselect("Customer state", states, default=states)

st.sidebar.divider()
if st.sidebar.button("Clear the cache"):
    st.cache_data.clear()
    st.rerun()

# ------------------------------------------------------------------ header
st.title("Warehouse Dashboard")
st.caption("MySQL for the orders, Redis for the item rankings, Streamlit for the page.")

if not chosen_carriers or not chosen_states:
    st.warning("Pick at least one carrier and one state.")
    st.stop()

ORDERS_SQL = """
SELECT co.Order_Num, co.Order_Date, co.Order_Carrier,
       c.Customer_Num, c.Customer_LastName, c.Customer_State
FROM customerorder co
  JOIN customer c ON co.Customer_Num = c.Customer_Num
WHERE co.Order_Carrier IN ({carriers})
  AND c.Customer_State IN ({states})
ORDER BY co.Order_Date
"""
sql = ORDERS_SQL.format(
    carriers=", ".join(["%s"] * len(chosen_carriers)),
    states=", ".join(["%s"] * len(chosen_states)),
)
orders = query(sql, tuple(chosen_carriers) + tuple(chosen_states))

# ------------------------------------------------------------------ metrics
a, b, c = st.columns(3)
a.metric("Orders", len(orders))
b.metric("Customers", orders["Customer_Num"].nunique() if len(orders) else 0)
c.metric("Carriers", orders["Order_Carrier"].nunique() if len(orders) else 0)

if orders.empty:
    st.info("No orders match these filters.")
    st.stop()

# ------------------------------------------------------------------ tabs
tab_orders, tab_items, tab_sql = st.tabs(["Orders", "Items", "Behind the page"])

with tab_orders:
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Orders by carrier")
        by_carrier = (orders.groupby("Order_Carrier")
                            .size()
                            .reset_index(name="Orders"))
        st.bar_chart(by_carrier, x="Order_Carrier", y="Orders")
    with right:
        st.subheader("By state")
        by_state = orders.groupby("Customer_State").size().reset_index(name="Orders")
        st.dataframe(by_state, width="stretch", hide_index=True)

    st.subheader("The orders themselves")
    st.dataframe(orders, width="stretch", hide_index=True)

with tab_items:
    st.subheader("Top sellers, straight out of Redis")
    st.caption("A sorted set keeps this ranking; nothing is sorted at read time.")

    how_many = st.slider("How many", 3, 15, 5)
    r = get_redis()
    top = r.zrevrange("items:by_sales", 0, how_many - 1, withscores=True)

    if not top:
        st.warning("Redis has no item data. Run app/seed.py.")
    else:
        rows = []
        for item_id, score in top:
            fields = r.hgetall(f"item:{item_id}")
            rows.append({"Item_ID": item_id,
                         "Description": fields.get("Item_Description", ""),
                         "Annual sales": int(score)})
        ranking = pd.DataFrame(rows)
        st.dataframe(ranking, width="stretch", hide_index=True)
        st.bar_chart(ranking, x="Item_ID", y="Annual sales")

with tab_sql:
    st.subheader("The query behind the Orders tab")
    st.code(sql.strip(), language="sql")
    st.caption(
        "The connection is cached with @st.cache_resource and shared. "
        "The result is cached with @st.cache_data(ttl=300), so it may be up to "
        "five minutes stale. That is the trade from Lecture 11."
    )
