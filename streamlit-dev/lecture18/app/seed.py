"""Load the warehouse CSVs into MySQL, and a few keys into Redis.

The stack runs this automatically when the streamlit container starts, so you
do not normally have to. Run it yourself to reload the data:

    docker compose exec streamlit python app/seed.py          # reload
    docker compose exec streamlit python app/seed.py --if-empty

With --if-empty it does nothing when the database already holds data, which is
how the container start-up calls it. Without the flag every table is dropped
and rebuilt.
"""
import csv
import os
import sys
import time

import pymysql
import redis

DATA = os.environ.get("DATA_DIR", "data/orders")

MYSQL = dict(host="mysql", port=3306, user="root",
             password="OSUGoPokes", database="iem4723_streamlit")

SCHEMA = {
    "customer": (
        """CREATE TABLE customer (
             Customer_Num       VARCHAR(10) PRIMARY KEY,
             Customer_FirstName VARCHAR(50),
             Customer_LastName  VARCHAR(50),
             Customer_Address   VARCHAR(100),
             Customer_City      VARCHAR(50),
             Customer_State     CHAR(2),
             Customer_ZIP       VARCHAR(10),
             Customer_Phone     VARCHAR(15),
             Customer_Email     VARCHAR(100))""",
        "Customer.csv",
        ["Customer_Num", "Customer_FirstName", "Customer_LastName", "Customer_Address",
         "Customer_City", "Customer_State", "Customer_ZIP", "Customer_Phone", "Customer_Email"],
    ),
    "item": (
        """CREATE TABLE item (
             Item_ID            VARCHAR(20) PRIMARY KEY,
             Item_Description   VARCHAR(50),
             Item_Price         DECIMAL(10,2),
             Item_Weight        DECIMAL(10,2),
             Item_AnnualSales   INT,
             Item_StockLocation VARCHAR(10))""",
        "Item.csv",
        ["Item_ID", "Item_Description", "Item_Price", "Item_Weight",
         "Item_AnnualSales", "Item_StockLocation"],
    ),
    "customerorder": (
        """CREATE TABLE customerorder (
             Order_Num            VARCHAR(10) PRIMARY KEY,
             Customer_Num         VARCHAR(10),
             Order_Date           DATE,
             Order_ReqShipDate    DATE,
             Order_ActualShipDate DATE,
             Order_Carrier        VARCHAR(50),
             FOREIGN KEY (Customer_Num) REFERENCES customer(Customer_Num))""",
        "CustomerOrder.csv",
        ["Order_Num", "Customer_Num", "Order_Date", "Order_ReqShipDate",
         "Order_ActualShipDate", "Order_Carrier"],
    ),
    "order_item": (
        """CREATE TABLE order_item (
             Order_Num VARCHAR(10),
             Item_ID   VARCHAR(20),
             Item_Qty  INT,
             PRIMARY KEY (Order_Num, Item_ID),
             FOREIGN KEY (Order_Num) REFERENCES customerorder(Order_Num),
             FOREIGN KEY (Item_ID)   REFERENCES item(Item_ID))""",
        "Order_Item.csv",
        ["Order_Num", "Item_ID", "Item_Qty"],
    ),
}

# dropped in reverse so the foreign keys never block a drop
DROP_ORDER = ["order_item", "customerorder", "item", "customer"]


def wait_for_mysql(timeout=90):
    """Block until MySQL accepts a connection, or give up after timeout seconds."""
    started = time.time()
    while True:
        try:
            pymysql.connect(**MYSQL).close()
            return
        except pymysql.err.OperationalError:
            if time.time() - started > timeout:
                raise
            time.sleep(1)


def already_seeded():
    conn = pymysql.connect(**MYSQL)
    cur = conn.cursor()
    cur.execute("SHOW TABLES LIKE 'customer'")
    if cur.fetchone() is None:
        conn.close()
        return False
    cur.execute("SELECT COUNT(*) FROM customer")
    rows = cur.fetchone()[0]
    conn.close()
    return rows > 0


def read_csv(name):
    with open(f"{DATA}/{name}", newline="") as f:
        return list(csv.DictReader(f))


def seed_mysql():
    """Rebuild the four tables and return a dict of table name to row count."""
    conn = pymysql.connect(**MYSQL)
    cur = conn.cursor()
    counts = {}

    for table in DROP_ORDER:
        cur.execute(f"DROP TABLE IF EXISTS {table}")

    for table, (ddl, csv_name, cols) in SCHEMA.items():
        cur.execute(ddl)
        rows = read_csv(csv_name)
        placeholders = ", ".join(["%s"] * len(cols))
        cur.executemany(
            f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})",
            [tuple(row[c] for c in cols) for row in rows],
        )
        counts[table] = len(rows)

    conn.commit()
    cur.close()
    conn.close()
    return counts


def seed_redis():
    """Rebuild the Redis keys and return how many there are."""
    r = redis.Redis(host="redis", port=6379, decode_responses=True)
    r.flushdb()

    for row in read_csv("Item.csv"):
        r.hset(f"item:{row['Item_ID']}", mapping=dict(row))
        r.sadd(f"items:description:{row['Item_Description']}", row["Item_ID"])
        r.zadd("items:by_sales", {row["Item_ID"]: float(row["Item_AnnualSales"])})

    return r.dbsize()


def load_everything():
    """Load both stores. Returns (table counts, redis key count)."""
    wait_for_mysql()
    return seed_mysql(), seed_redis()


if __name__ == "__main__":
    wait_for_mysql()

    if "--if-empty" in sys.argv and already_seeded():
        print("database already holds data, nothing to do")
        sys.exit(0)

    print("seeding MySQL")
    for table, n in seed_mysql().items():
        print(f"  {table:<14} {n:>4} rows")
    print("seeding Redis")
    print(f"  redis keys     {seed_redis():>4}")
    print("done")
