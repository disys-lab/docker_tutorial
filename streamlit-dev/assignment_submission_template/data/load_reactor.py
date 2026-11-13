"""Helper for Assignment 3, Part 3. Reads the reactor telemetry CSV."""
import csv


def load_reactor(path="data/reactor_sample_5k.csv"):
    """
    Read the reactor telemetry file and return a list of dicts, one per
    reading, with the numeric columns already converted:

        {"Timestamp_min": 0, "Reactor_Temp_C": 85.0,
         "Pressure_atm": 3.2, "Reactor_Run_ID": "1"}

    Reactor_Run_ID is left as a string because it is used in key names.
    """
    with open(path, newline="") as f:
        return [
            {
                "Timestamp_min":  int(row["Timestamp_min"]),
                "Reactor_Temp_C": float(row["Reactor_Temp_C"]),
                "Pressure_atm":   float(row["Pressure_atm"]),
                "Reactor_Run_ID": row["Reactor_Run_ID"],
            }
            for row in csv.DictReader(f)
        ]


if __name__ == "__main__":
    readings = load_reactor()
    print(len(readings), "readings")
    print(readings[0])
