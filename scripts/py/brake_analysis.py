import pandas as pd
from scripts.py.vbox_parser import parse_file, parse_dataframe

def brake_length(df):

    # Replace values less than zero in the Brake column with zeros
    df['Brake'] = df['Brake'].clip(lower=0)

    # Column to mark the start of a braking instance
    df['Braking_Start'] = (df['Brake'] > 0) & (df['Brake'].shift(1) == 0)

    # Column to mark the end of a braking instance
    df['Braking_End'] = (df['Brake'] == 0) & (df['Brake'].shift(1) > 0)

    # Identify braking instances and assign a unique ID to each instance
    df['Braking_ID'] = df['Braking_Start'].cumsum()

    # Filter out non-braking periods
    braking_periods = df[df['Brake'] > 0]

    # Group by braking ID to calculate the duration of each instance
    braking_summary = braking_periods.groupby(['Braking_ID', "LapNumber"]).agg(
        start_time=('Time', 'first'),
        end_time=('Time', 'last'),
        duration=('Time', lambda x: x.max() - x.min()),
        peak_press = ("Brake", "max"),
    ).reset_index()

    # Remove instances with a duration of 1 (single entry)
    braking_summary = braking_summary[braking_summary['duration'] > 1]

    # Ignore single entry instances of brake application
    braking_summary['brake_index'] = braking_summary['peak_press'] / braking_summary['duration']

    # Reset the Braking_ID so that it starts from 1
    braking_summary.reset_index(drop=True, inplace=True)
    braking_summary['Braking_ID'] = braking_summary.index + 1

    # Display the results
    return braking_summary

if __name__ == "__main__":


    data = parse_dataframe("test, Lap 1.csv")

    brake_length(data)