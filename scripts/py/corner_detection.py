from scripts.py.vbox_parser import parse_dataframe
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt
import pandas as pd

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=5):

    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def detect_corners(df):

    vel = df["Velocity"]

    for i in range(0, len(vel) -1):

        v_i = vel[i]
        v_o = vel[i+1]

        df.loc[i, 'dv'] = v_o - v_i

    # Add a new column 'is_corner' initialized with zeros
    df['is_corner'] = 0

    # Define the threshold and the duration for which dv needs to be positive
    threshold = -1.2
    positive_duration = 10 # number of consecutive positive values required

    # Track the number of consecutive positive dv values
    positive_counter = 0

    # Flag indicating if the is_corner condition has been triggered
    is_corner_active = False

    for i in range(len(df)):
        if df.loc[i, 'dv'] < threshold:
            is_corner_active = True
            positive_counter = 0
        elif is_corner_active and df.loc[i, 'dv'] > 0:
            positive_counter += 1
        else:
            positive_counter = 0
        
        if is_corner_active:
            df.loc[i, 'is_corner'] = 1
        
        if positive_counter >= positive_duration:
            is_corner_active = False
            df.loc[i - positive_duration + 1:i + 1, 'is_corner'] = 0

    # Initialize the section counters
    corner_count = 1
    straight_count = 1

    # Initialize the section column
    df['section'] = ''

    # Assign unique labels to corners and straights
    for i in range(len(df)):
        if df.loc[i, 'is_corner'] == 1:
            df.loc[i, 'section'] = f'Corner {corner_count}'
            if i == len(df) - 1 or df.loc[i + 1, 'is_corner'] == 0:
                corner_count += 1
        else:
            df.loc[i, 'section'] = f'Straight {straight_count}'
            if i == len(df) - 1 or df.loc[i + 1, 'is_corner'] == 1:
                straight_count += 1

    print(df)
    
def detect_corners_by_accel(df):
    latacc = df["LateralAcceleration"] * 9.81
    v = (df["Velocity"]) ** 2

    curvature = latacc / v

    print("curvature: \n")
    print(curvature)

    # Calculate the sampling frequency (fs)
    time_diffs = df['Time'].diff().dropna()
    mean_time_diff = time_diffs.mean()
    fs = 1 / mean_time_diff

    # Set the cutoff frequency to 5 Hz
    cutoff = 0.6

    if curvature.isnull().any():
        print("NaNs found in curvature column before filtering")
    if np.isinf(curvature).any():
        print("Infinite values found in curvature column before filtering")

    # Apply the lowpass filter to the curvature column
    df['curvature_filtered'] = lowpass_filter(curvature, cutoff, fs)

    df['curvature'] = curvature

    print("post filtered:" ,df)

    curvature_threshold = 0.0016 # Example threshold for corner detection

    def segment_path(df, threshold):
        df['segment'] = np.where(abs(df['curvature_filtered']) > threshold, 'Corner', 'Straight')

        segment_labels = []
        corner_label = 1
        straight_label = 1

        current_segment = df.iloc[0]['segment']
        for i in range(len(df)):
            if df.iloc[i]['segment'] != current_segment:
                if df.iloc[i]['segment'] == 'Corner':
                    corner_label += 1
                else:
                    straight_label += 1
                current_segment = df.iloc[i]['segment']

            if current_segment == 'Corner':
                segment_labels.append(f"Corner {corner_label}")
            else:
                segment_labels.append(f"Straight {straight_label}")

        df['segment_label'] = segment_labels
        return df

    df = segment_path(df, curvature_threshold)

    # Print the resulting dataframe with labeled segments
    print(df[['Time', 'curvature', 'segment_label']])

    def plot_curvature_segments(df):
        unique_segments = df['segment_label'].unique()


        plt.figure(figsize=(15, 8))
        for segment in unique_segments:
            segment_data = df[df['segment_label'] == segment]
            plt.plot(segment_data['Longitude'], segment_data['Latitude'], label=segment)

        plt.xlabel('Time (s)')
        plt.ylabel('Curvature')
        plt.title('Curvature with Segments')
        plt.legend()
        plt.show()

    #plot_curvature_segments(df)
    return df


if __name__ == "__main__":

    print("This script is intended for use as a module imported into a script. It does not provide standalone functionality when run as main.\n\nPlease import corner_detection as a module.")

    data = parse_dataframe("test, Lap 3.csv")

    print(data)

    df = detect_corners_by_accel(data)
"""
    plt.figure()
    plt.plot(df["Time"], df["curvature_filtered"])

    plt.show()"""