"""An MCP server that reads three of the warehouse CSV files.

It offers three tools and nothing else:

    list_datasets()  what data is here
    columns(name)    what is in one dataset
    summarize(...)   group the rows and count or add something up

The server speaks MCP over HTTP on port 8000. The Streamlit app in app/ is
the client. Nothing in this file knows what Streamlit is, and nothing in it
draws a chart. It returns numbers. The app draws them.
"""
import csv
import json

from mcp.server.mcpserver import MCPServer

# The three files we expose, under the names the model will use.
FILES = {
    "customers": "data/orders/Customer.csv",
    "orders": "data/orders/CustomerOrder.csv",
    "items": "data/orders/Item.csv",
    "vendors": "data/orders/Vendor.csv",
    "shipmentinfo": "data/orders/Shipment_Info.csv",
    "pallet": "data/orders/Pallet.csv",
    "shipment": "data/orders/Shipment.csv",
    "orderitem": "data/orders/Order_Item.csv",
    "cases": "data/orders/Cases.csv",
}

mcp = MCPServer("warehouse")


def read_rows(dataset):
    with open(FILES[dataset], newline="") as f:
        return list(csv.DictReader(f))


@mcp.tool()
def list_datasets() -> str:
    """List the warehouse datasets available, with the number of rows in each.

    Call this first if you do not already know what data exists.
    """
    out = []
    for name in FILES:
        out.append({"dataset": name, "rows": len(read_rows(name))})
    return json.dumps(out)


@mcp.tool()
def columns(dataset: str) -> str:
    """List the column names of one dataset, with an example value for each.

    Call this before summarize so you use real column names.
    dataset must be one of: customers, orders, items.
    """
    if dataset not in FILES:
        return json.dumps({"error": f"no dataset called {dataset}",
                           "available": list(FILES)})

    rows = read_rows(dataset)
    out = []
    for name in rows[0]:
        out.append({"column": name, "example": rows[0][name]})
    return json.dumps(out)


@mcp.tool()
def summarize(dataset: str, group_by: str, how: str = "count",
              measure: str = "", chart: str = "bar") -> str:
    """Group the rows of a dataset by one column and count or add up another.

    dataset   one of: customers, orders, items
    group_by  the column to group by, for example Order_Carrier
    how       count, sum or mean. count ignores measure.
    measure   the numeric column to add up or average, when how is sum or mean
    chart     bar or line. Choose line only when group_by is a date or a time.

    Returns the grouped rows, largest first. The caller draws the chart.
    """
    if dataset not in FILES:
        return json.dumps({"error": f"no dataset called {dataset}",
                           "available": list(FILES)})

    rows = read_rows(dataset)

    if group_by not in rows[0]:
        return json.dumps({"error": f"{dataset} has no column {group_by}",
                           "available": list(rows[0])})

    if how != "count" and measure not in rows[0]:
        return json.dumps({"error": f"{dataset} has no column {measure}",
                           "available": list(rows[0])})

    # Collect the values that fall into each group.
    groups = {}
    for row in rows:
        key = row[group_by]
        if key not in groups:
            groups[key] = []
        if how == "count":
            groups[key].append(1)
        else:
            try:
                groups[key].append(float(row[measure]))
            except ValueError:
                return json.dumps({"error": f"{measure} is not a number, "
                                            f"so it cannot be used with {how}"})

    # Reduce each group to a single number.
    label = how if how != "count" else "count"
    result = []
    for key in groups:
        values = groups[key]
        if how == "mean":
            value = round(sum(values) / len(values), 2)
        else:
            value = sum(values)
        result.append({group_by: key, label: value})

    result.sort(key=lambda row: row[label], reverse=True)

    if chart not in ("bar", "line"):
        chart = "bar"

    return json.dumps({"chart": chart, "x": group_by, "y": label,
                       "rows": result})


if __name__ == "__main__":
    # 0.0.0.0 so the Streamlit container can reach it, not just this one.
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
