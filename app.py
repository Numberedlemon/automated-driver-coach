import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


from flask import Flask, session, redirect, request, render_template, jsonify
from flask_session import Session
import pandas as pd
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=(SettingWithCopyWarning))
from scripts.py.metrics import calculate_metrics
from scripts.py.corner_detection import detect_corners, detect_corners_by_accel
from scripts.py.vbox_parser import parse_dataframe, parse_file
from scripts.py.brake_analysis import brake_length
from scripts.py.mini_sectors import *
import re
import json
from io import StringIO

"""
To do: 

- Write alternative vbox parser to manipulate dataframes in vbox_parser.py - DONE 12:59 PM 27/6/2024
- Refactor metric calculation to separate out straights and corners im metrics.py - DONE 3:30 PM 27/6/2024
- Implement straights and corners metric visualisation in metrics.html - DONE 4:30 PM 27/6/2024
- Work out why jinja templates cause errors that don't make the web-page go funky. - ONGOING

: 9/7/2024 :

- Refactor code to accept every lap in the stint. DONE 25/7/2024
- Add dropdown functionality to select lap to view to velocity breakdown and gg-plot. 
- Add ability to compare two laps. DONE 26/7/2024
- Research breaking of lap into sectors and stitching together of best lap.
    - Sector splits DONE 25/7/2024

: 26/7/2024 :

- Under- and Over-steer algorithm implementation.
- More braking metrics (time to max brake?)
- Implement video detection in a way that makes sense.
- Cleaning of code and making sure visuals work in a way that looks right.

(LAST UPDATE 11:57 AM 26/7/2024)
"""

app = Flask(__name__, "/static")
app.config["SECRET_KEY"] = "testing"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        files = request.files.getlist('files')

        print(f"Received files: {[file.filename for file in files]}")

        if not files or files[0].filename == '':
            return 'No file selected'
        
        dfs = []
        lap_numbers = set()
        for file in files:
            if file:
                # Extract the lap number from the filename using regex
                match = re.search(r'Lap (\d+)', file.filename)
                if match:
                    lap_number = int(match.group(1))
                    lap_numbers.add(lap_number)
                else:
                    lap_number = None  # Default value if lap number is not found


                # Parse the file into a DataFrame
                df = parse_dataframe(file)
                
                # Add the lap number as a new column
                df['LapNumber'] = lap_number
                
                # Append the DataFrame to the list
                dfs.append(df)

                print(dfs)
        
        if dfs:
            # Concatenate all DataFrames in the list
            concatenated_df = pd.concat(dfs, ignore_index=True)
            
            # Store the concatenated DataFrame in the session as JSON
            session['data'] = concatenated_df.to_json()
            session['lap_numbers'] = sorted(lap_numbers)
            
        
        return redirect('/upload')
    
    return render_template('index.html')

# data upload screen
@app.route('/upload')
def upload_screen():
    return render_template('upload.html')

@app.route('/object-detection')
def object_detection():
    return render_template('detection.html')

@app.route("/mini-sectors", methods = ["POST", "GET"])
def mini_sectors():

    lap_numbers = session.get("lap_numbers")

    lapSelect = request.args.get('lapSelect', 3, type=int)
    lapReference = request.args.get('lapReference', 2, type=int)

    if request.method == 'POST':
        lapSelect = request.form.get('lapSelect', type=int)
        lapReference = request.form.get('lapReference', type=int)
        return redirect(f'/mini-sectors?lapSelect={lapSelect}&lapReference={lapReference}')

    df = pd.read_json(session.get("data"))

    df_Selected = df[df["LapNumber"] == lapSelect]
    df_Reference = df[df["LapNumber"] == lapReference]

    df1 = discretise_lap(df_Selected, num_bins = 4, brake_threshold = 10)
    df2 = discretise_lap(df_Reference, num_bins = 4, brake_threshold = 10)

    results = get_deltas(df2, df1)

    return render_template("mini_sectors.html", lap_numbers = lap_numbers, lapSelect = lapSelect, lapReference = lapReference, data = results.to_json())

@app.route('/brake_index')
def brakes():
    df = pd.read_json(session.get('data'))

    lap_numbers = session.get('lap_numbers')

    df = brake_length(df)

    return render_template('brakes.html', data = df.to_json(), lap_numbers = lap_numbers)

# o/s u/s page
@app.route('/os-us')
def os_us():
    df = session.get('data')

    lap_numbers = session.get('lap_numbers')


    lap = request.form.get("dropdown")

    if lap is not None:
        df = df[df["LapNumber"] == lap]

    return render_template('os-us.html', data = df, lap_numbers = lap_numbers)

#throttle brake trace diagram
@app.route('/traces')
def traces():
    df = session.get('data')

    lap_numbers = session.get('lap_numbers')

    lap = request.form.get('dropdown')

    if lap is not None:
        df = df[df["LapNumber"] == lap]

    return render_template('traces.html', data = df, lap_numbers = lap_numbers)

# gg-diagram screen
@app.route('/gg-diagram')
def show_gg():

    df = session.get('data')

    return render_template('gg_diagram.html', data = df)

# track map screen
@app.route('/track-map', methods = ["POST", "GET"])
def track_map():

    df = session.get('data')

    df = pd.read_json(df)

    lap = request.form.get('dropdown')

    lap_numbers = session.get('lap_numbers')
    
    if lap is not None:
        df = df[df["LapNumber"] == lap]
        print(df)

    return render_template('track-map.html', data = df.to_json(), lap_numbers= lap_numbers)

# metrics screen
@app.route('/metrics')
def metrics():

    lap_numbers = session.get('lap_numbers')
    lap = 2
    if 'data' not in session:
        return redirect('/upload')
    
    df = pd.read_json(session['data'])

    #print(f"Printing DF: {df}")

    metrics_agg = run_data_analysis(df, lap)

    print(f"Aggregated metrics: \n {metrics_agg}")

    metrics_agg = metrics_agg.to_json()

    #logging.debug(f'Analysis results: {results}')
    return render_template('metrics.html', data = metrics_agg, lap_numbers= lap_numbers, selected_lap=lap)

# metrics screen
@app.route('/update/<int:lap_number>', endpoint = "update")
def metrics(lap_number):

    lap = lap_number
    if 'data' not in session:
        return redirect('/upload')
    
    df = pd.read_json(session['data'])
    print(df)

    #print(f"Printing DF: {df}")

    metrics_agg = run_data_analysis(df, lap)

    metrics_agg = metrics_agg.to_json()

    #logging.debug(f'Analysis results: {results}')
    return metrics_agg

def run_data_analysis(df, lap):

    df = detect_corners_by_accel(df)

    metrics = calculate_metrics(df, lap)

    return metrics

if __name__ == '__main__':
    app.run(debug=True)