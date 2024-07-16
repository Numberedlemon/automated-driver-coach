import pandas as pd
from scripts.py.vbox_parser import parse_file, parse_dataframe
from scripts.py.corner_detection import detect_corners

def calculate_metrics(df,lap):

    # calculate velocity metrics
    vel_metrics = calculate_velocity_metrics(df, lap)
    
    return vel_metrics

def calculate_velocity_metrics(df, lap):

    df = df[df["LapNumber"] == lap]

    # aggregation by group, calculation of group mean, min, and max.
    metrics = df.groupby('section').agg({'Velocity': ["min", "mean", "max"]}).reset_index()

    # make DataFrame.
    df_metrics = pd.DataFrame(metrics)

    print(metrics)

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

    data = parse_file("./uploads/data.csv")

    detect_corners(data)

    calculate_velocity_metrics(data)
    
    generate_acceleration_report(data)