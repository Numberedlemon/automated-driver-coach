import pandas as pd
from scripts.py.vbox_parser import parse_file, parse_dataframe
import matplotlib.pyplot as plt

def adjust_bin_edges(df, brake_threshold, num_bins):

    # Get the edges of the bins
    bin_edges = pd.qcut(df['Distance'], q=num_bins, retbins=True)[1]
    adjusted_bin_edges = []
    
    # Iterate over each bin
    for i in range(len(bin_edges) - 1):
        bin_start = bin_edges[i]
        bin_end = bin_edges[i + 1]
        
        # Check if bin adjustment condition is met
        start_idx = df[(df['Distance'] >= bin_start) & (df['Distance'] < bin_end)].index
        if not start_idx.empty and df.loc[start_idx[0], 'Brake'] > brake_threshold:
            # Find the new start index
            new_start_idx = start_idx[start_idx > start_idx[0]][df.loc[start_idx[start_idx > start_idx[0]], 'Brake'] <= brake_threshold]
            if not new_start_idx.empty:
                new_start_idx = new_start_idx[0]
                bin_start = df.loc[new_start_idx, 'Distance']
        
        adjusted_bin_edges.append(bin_start)
    
    adjusted_bin_edges.append(bin_edges[-1])
    return adjusted_bin_edges

def discretize_and_label(df, adjusted_bin_edges):

    # qcut the dataframe by the new bins.
    df['adjusted_bins'] = pd.cut(df['Distance'], bins=adjusted_bin_edges, include_lowest=True)
    df['sector'] = df['adjusted_bins'].cat.codes

    return df

def calculate_max_time(df):

    max_time_in_bins = df.groupby('sector')['Time'].max().reset_index()
    max_time_in_bins['sector'] = max_time_in_bins['sector'] + 1  # Bin labels start from 1
    return max_time_in_bins

def plot_max_time_bins(df):

    plt.figure(figsize=(10, 6))
    plt.scatter(df["Latitude"], df["Longitude"], c = df["sector"])
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.title('Sector Split Points')
    plt.xticks(rotation=45)
    plt.show()

def discretise_lap(df, num_bins, brake_threshold):
    # Adjust bin edges based on the Brake value
    adjusted_bin_edges = adjust_bin_edges(df, brake_threshold, num_bins)
    
    # Discretize the distance column and assign numerical bin labels
    df = discretize_and_label(df, adjusted_bin_edges)
    
    # Calculate the maximum time for each bin
    max_time_in_bins = calculate_max_time(df)

    print(max_time_in_bins)
    
    # Plot the results
    #plot_max_time_bins(df)

    return max_time_in_bins

def get_deltas(df, df2):

    merged_df = pd.merge(df, df2, on = "sector", suffixes = ("_df1", "_df2"))

    merged_df["time_difference"] = merged_df["Time_df2"] - merged_df["Time_df1"]

    results = merged_df[["sector", "time_difference"]]

    return results


if __name__ == "__main__":

    df = parse_dataframe("test, Lap 2.csv")
    df2 = parse_dataframe("test, Lap 3.csv")

    df1 = discretise_lap(df, num_bins=3, brake_threshold=10)
    df3 = discretise_lap(df2, num_bins = 3, brake_threshold= 10)


    merged_df = pd.merge(df1, df3, on='sector', suffixes=('_df1', '_df2'))

    merged_df['time_difference'] = merged_df['Time_df2'] - merged_df['Time_df1']

    result_df = merged_df[['sector', 'time_difference']]

    print(result_df)