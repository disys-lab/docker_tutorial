# Assignment 4 template

Four folders, one per app. Each has its own `docker-compose.yml` and its own
`app/main.py`, and each runs on its own port so you can have them all open at
once.

| Folder         | What goes in it                      | Open                  |
|----------------|--------------------------------------|-----------------------|
| `Q1-customer/` | Question 1, customer dataset         | http://localhost:8511 |
| `Q1-reactor/`  | Question 1, reactor dataset          | http://localhost:8512 |
| `Q2/`          | Question 2, the three charts         | http://localhost:8513 |
| `Q3/`          | Question 3, broken chart and the fix | http://localhost:8514 |

## Running one

Go into the folder and start it:

```bash
cd Q1-customer
docker compose up -d
```

Then open the port from the table above. Stop it again with:

```bash
docker compose down
```

Repeat for each folder you are working on. Nothing is built, so the first start
only has to pull the course image.

## Editing

`app/` is mounted into the container. Edit `app/main.py` on your machine, save,
and the browser offers a rerun. You do not need to restart anything.

## The data

`data/` sits at the top of this template and is mounted read-only into every
app at `data/`, so your code reads it the same way in all four folders:

```python
with open("data/orders/Item.csv", newline="") as f:
    items = list(csv.DictReader(f))
```

For the reactor file use the supplied reader:

```python
import sys
sys.path.insert(0, "data")
from load_reactor import load_reactor

readings = load_reactor("data/reactor_sample_5k.csv")
```

Each reading comes back as a dictionary with the numbers already converted:

```python
{"Timestamp_min": 0, "Reactor_Temp_C": 85.0,
 "Pressure_atm": 3.2, "Reactor_Run_ID": "1"}
```

## Charts take a list of dictionaries

Build the rows first, then draw:

```python
chart_rows = []
for reading in readings:
    chart_rows.append({"Minute": reading["Timestamp_min"],
                       "Temperature": reading["Reactor_Temp_C"]})

st.line_chart(chart_rows, x="Minute", y="Temperature")
```

## What to submit

Submit the whole template folder with your code in it, plus the screenshots and
`README.md` the assignment asks for. Keep the folder names as they are.
