# Data for Assignment 3

## `reactor_sample_5k.csv`

Batch reactor telemetry, 4,901 readings drawn from 27 reactor runs. Four columns; the other sensor channels have been removed.

| Column | Meaning |
|---|---|
| `Timestamp_min` | Elapsed time in minutes. Unique across the whole file and increasing, with the runs laid end to end. |
| `Reactor_Temp_C` | Reactor temperature, degrees Celsius |
| `Pressure_atm` | Reactor pressure, atmospheres |
| `Reactor_Run_ID` | Which run the reading belongs to, 1 through 27 |

Read it with `load_reactor()` from `load_reactor.py` in this folder.

`Timestamp_min` runs 0 to 5000 with no gaps and no repeats, so it works directly
as a sorted set score. Run 1 covers minutes 0 to 149, run 2 covers 150 to 299,
and so on. Runs vary in length from 100 to 290 readings.

**Source.** *Batch Reactor Anomaly Data (Sample)* by AI Mind Teams, published on
Kaggle at <https://www.kaggle.com/datasets/aimindteams/batch-reactor-anomaly-data-sample>.

**Licence.** Creative Commons Attribution-NonCommercial 4.0 International
(CC BY-NC 4.0), <https://creativecommons.org/licenses/by-nc/4.0/>. Redistributed
here unmodified for classroom use with attribution.

## `orders/`

`Customer.csv` and `CustomerOrder.csv` are the two files the assignment actually
uses. `Item.csv` and `Order_Item.csv` are included for reference only, in case you
want to extend the comparison further.

All four are the same files used in the Lecture 7 through 9 tutorials, without the
personalised key suffix that Assignment 2 required, so that the SQL and Redis
answers in this assignment can be compared directly.
