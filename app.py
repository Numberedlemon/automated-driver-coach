from flask import Flask, session, redirect, request, render_template
from flask_session import Session
import pandas as pd
from scripts.py.metrics import calculate_metrics
from scripts.py.corner_detection import detect_corners
from scripts.py.vbox_parser import parse_dataframe, parse_file


"""
To do: 

- Write alternative vbox parser to manipulate dataframes in vbox_parser.py - DONE 12:59 PM 27/6/2024
- Refactor metric calculation to separate out straights and corners im metrics.py - DONE 3:30 PM 27/6/2024
- Implement straights and corners metric visualisation in metrics.html - DONE 4:30 PM 27/6/2024
- Work out why jinja templates cause errors that don't make the web-page go funky. - ONGOING

: 9/7/2024 :

- Refactor code to accept every lap in the stint
- Add dropdown functionality to select lap to view to velocity breakdown and gg-plot.
- Add ability to compare two laps.
- Research breaking of lap into sectors and stitching together of best lap.

(LAST UPDATE 11:28 AM 9/7/2024)
"""

app = Flask(__name__, "/static")
app.config["SECRET_KEY"] = "testing"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# basic route for uploading file.
@app.route('/', methods = ['GET','POST'])
def upload():
    if request.method == "POST":
        file = request.files['file']
        if file:
            df = parse_file(file)
            session['data'] = df.to_json()
            return redirect('/upload')
    return render_template('index.html')

# data upload screen
@app.route('/upload')
def upload_screen():
    return render_template('upload.html')

# gg-diagram screen
@app.route('/gg-diagram')
def show_gg():

    df = session.get('data')

    return render_template('gg_diagram.html', data = df)

# track map screen
@app.route('/track-map')
def track_map():

    df = session.get('data')

    return render_template('track-map.html', data = df)

# metrics screen
@app.route('/metrics')
def metrics():

    df = session.get('data')

    df = pd.read_json(df)

    metrics_agg = run_data_analysis(df)

    metrics_agg = metrics_agg.to_json()

    #logging.debug(f'Analysis results: {results}')
    return render_template('metrics.html', data = metrics_agg)

def run_data_analysis(df):

    data = parse_dataframe(df)
    
    detect_corners(data)

    metrics = calculate_metrics(data)

    return metrics



if __name__ == '__main__':
    app.run(debug=True)