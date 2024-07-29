import pandas as pd
from scripts.py.vbox_parser import parse_file, parse_dataframe
from scripts.py.corner_detection import *


def calculate_metrics(df,lap):

    # calculate velocity metrics
    vel_metrics = calculate_velocity_metrics(df, lap)
    
    return vel_metrics

def calculate_velocity_metrics(df, lap):

    #print(timeit.timeit(f'df[df["LapNumber"] == lap]', number = 100, globals={'df': df, 'lap': lap}))

    df = df[df["LapNumber"] == lap]
    print(df)

    # aggregation by group, calculation of group mean, min, and max.
    metrics = df.groupby('segment_label').agg({'Velocity': ["min", "mean", "max"]}).reset_index()

    # make DataFrame.
    df_metrics = pd.DataFrame(metrics)

    #print(metrics)

    # dump DataFrame to json file.

    #print(jsonify(df_metrics))

    return metrics

def generate_acceleration_report(df):
    
    speeds = [50, 100, 150, 200, 250]
    
    # pattern for regex filtering of df.
    pat = r'\bStraight \d+\b'
    
    # filtering of df to exclude corners and consider only straights.
    df = df[df['section'].str.contains(pat)]
    
    # aggregation by group and calculation of group min and max.
    metrics = df.groupby('section').agg({'Time': ['min', 'max']}).reset_index()
    
    df_metrics = pd.DataFrame(metrics)
    
    df_metrics.to_json("./metrics/acceleration_report.json", orient = "records")
    
    print(metrics)

if __name__ == "__main__":

    data = parse_dataframe("test, Lap 3.csv")

    detect_corners_by_accel(data)

    m = calculate_velocity_metrics(data, 1)
    
    #generate_acceleration_report(data)

    print(m)