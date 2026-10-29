"""Load the warehouse CSVs into MySQL, and a few keys into Redis.

Run this once after the stack comes up:

    docker compose exec streamlit python app/seed.py

It is safe to run again; every table is dropped and rebuilt.
"""
import csv
import os

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


def read_csv(name):
    with open(f"{DATA}/{name}", newline="") as f:
        return list(csv.DictReader(f))


def seed_mysql():
    conn = pymysql.connect(**MYSQL)
    cur = conn.cursor()

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
        print(f"  {table:<14} {len(rows):>4} rows")

    conn.commit()
    cur.close()
    conn.close()


def seed_redis():
    r = redis.Redis(host="redis", port=6379, decode_responses=True)
    r.flushdb()

    for row in read_csv("Item.csv"):
        r.hset(f"item:{row['Item_ID']}", mapping=dict(row))
        r.sadd(f"items:description:{row['Item_Description']}", row["Item_ID"])
        r.zadd("items:by_sales", {row["Item_ID"]: float(row["Item_AnnualSales"])})

    print(f"  redis keys     {r.dbsize():>4}")


if __name__ == "__main__":
    print("seeding MySQL")
    seed_mysql()
    print("seeding Redis")
    seed_redis()
    print("done")
