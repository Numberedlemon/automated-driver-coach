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

if __name__ == "__main__":

    print("This script is intended for use as a module imported into a script. It does not provide standalone functionality when run as main.\n\nPlease import corner_detection as a module.")
