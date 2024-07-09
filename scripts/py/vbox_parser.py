import pandas as pd
import re

def convert_dms(dm):

    """
    Converts a list of latitude or longitude values from degrees, minutes, decimal minutes (DMM) format to decimal degrees.

    Takes a list of strings representing geographic coordinates in DMM format and converts 
    each value to decimal degrees (DD). The DMM format should be in the form "DDD°MM.MMMMM N/S/E/W".

    Parameters:
    dm (list of str): A list of strings where each string represents a coordinate in DMM format.

    Returns:
    list of float: A list of converted coordinates in decimal degrees.

    Raises:
    ValueError: If any of the input strings do not match the expected DMM format.

    Notes:
    - The input list `dm` should contain strings formatted as "DDD°MM.MMMMM N/S/E/W", where:
        - DDD is degrees
        - MM.MMMMM is minutes and decimal minutes
        - N/S/E/W indicates the direction (North, South, East, West)
    - North and East coordinates are positive, while South and West coordinates are negative.

    Example:
    >>> dmm_list = ["51°30.0000 N", "000°07.0000 W"]
    >>> convert_dms(dmm_list)
    [51.5, -0.11666666666666667]
    """

    decimal_degrees_list = []

    for i in dm:
        match = re.match(r"(\d+)°(\d+)\.(\d+) ([NSEW])", i)
        if not match:
            raise ValueError("Invalid DMM format")
        
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        decimal_minutes = float("0." + match.group(3))
        direction = match.group(4)
        
        # Convert minutes and decimal minutes to decimal degrees
        decimal_degrees = degrees + (minutes + decimal_minutes) / 60
        
        # Adjust the sign based on the direction
        if direction == 'S' or direction == 'W':
            decimal_degrees = -decimal_degrees

        decimal_degrees_list.append(decimal_degrees)
    
    return decimal_degrees_list

def parse_file(filepath):

    print(f"Parsing VBOX csv export file at '{filepath}', please wait.\n")

    data = pd.read_csv(filepath, sep = ",")

    lat = data["Latitude"]
    long = data["Longitude"]
    alt = data["Height"]
    time = data["ElapsedTimeSeconds"]
    velocity = data["Velocity"]
    latacc = data["LateralAcceleration"]
    longacc = data["LongitudinalAcceleration"]

    startTime = time[0]

    time = time - startTime

    lat_deg = convert_dms(lat)
    lon_deg = convert_dms(long)

    data_df = pd.DataFrame({
        "Time": time,
        "Latitude": lat_deg,
        "Longitude":lon_deg,
        "Height": alt,
        "Velocity": velocity,
        "LateralAcceleration": latacc,
        "LongitudinalAcceleration": longacc
    })

    print("VBOX data parsed. Showing head of data.\nPlease inspect data to ensure form is as expected.\n")
    print(data_df)

    return data_df

def parse_dataframe(df):

    print(f"Parsing VBOX-derived dataframe, please wait.\n")

    data = df

    lat = data["Latitude"]
    long = data["Longitude"]
    alt = data["Height"]
    time = data["Time"]
    velocity = data["Velocity"]
    latacc = data["LateralAcceleration"]
    longacc = data["LongitudinalAcceleration"]

    startTime = time[0]

    time = time - startTime

    data_df = pd.DataFrame({
        "Time": time,
        "Latitude": lat,
        "Longitude":long,
        "Height": alt,
        "Velocity": velocity,
        "LateralAcceleration": latacc,
        "LongitudinalAcceleration": longacc
    })

    print("VBOX data parsed. Showing head of data.\nPlease inspect data to ensure form is as expected.\n")
    print(data_df)

    return data_df


if __name__ == "__main__":

    #data = parse("matthew.csv")

    #print(data)

    print("This script is intended to be imported as a module, and not as a standalone file.\nPlease import the module.")