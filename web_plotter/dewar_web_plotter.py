# Author: Kyungtae Kim
# Mail : kim.kyngt@gmail.com
# Date: 2023-04

import base64
import pybase64
from io import BytesIO
from flask import Flask, render_template_string, request
from matplotlib.figure import Figure
import numpy as np
import datetime
import json
import os
import glob
import pandas as pd
from datetime import datetime, timedelta
import time
# Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return render_template_string('''
        <html>
            <head>
                <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
                <script>
                    $(document).ready(function() {
                        function updatePlot() {
                            var width = $(window).width();
                            var height = $(window).height();
                            $.ajax({
                                url: "/plot?width=" + width + "&height=" + height,
                                success: function(data) {
                                    $('#plot').attr('src', 'data:image/png;base64,' + data);
                                },
                                complete: function() {
                                    setTimeout(updatePlot, 10000); // Adjust the delay between updates (in milliseconds)
                                }
                            });
                        }
                        updatePlot();
                        $(window).resize(function() {
                            clearTimeout(window.updateTimeout);
                            window.updateTimeout = setTimeout(updatePlot, 10000);
                        });
                    });
                </script>
            </head>
            <body style="margin:0; padding:0;">
                <img id="plot" src="" style="width:100%; height:100%; display:block;" />
            </body>
        </html>
    ''')

@app.route("/plot")

def plot():
    # Dewar data
    most_recent_file = max(glob.glob(os.path.join(r"C:\Users\Ye Lab\Google Drive\Data\21 cm Si Cavity\Dewar", "*.dat")), key=os.path.getmtime)
    data_dewar = pd.read_csv(
        most_recent_file,
        header=0,
        skiprows=[1],
        delimiter=r'\s+',
    )

    # PID controller data
    most_recent_file = max(glob.glob(os.path.join(r"C:\Users\Ye Lab\Google Drive\Data\21 cm Si Cavity\Cryostat", "*.dat")), key=os.path.getmtime)
    data_pid = pd.read_csv(
        most_recent_file,
        header=0,
        skiprows=[1],
        delimiter=r'\s+',
    )


    def mjd_to_date(mjd):
        # The reference date for MJD (November 17, 1858, 00:00 UTC)
        reference_date = datetime(1858, 11, 17, 0, 0, 0)

        # Convert MJD to a timedelta
        days_since_reference = timedelta(days=mjd)

        # Add the timedelta to the reference date
        return reference_date + days_since_reference - timedelta(hours=6) # converting to local time zone (manually!)

    # Processing Dewar level data
    datasz = len(data_dewar["MJD"])-1
    num_data_show = 3000 # Number of data points to show.
    x = data_dewar["MJD"][datasz-num_data_show:datasz].to_numpy()
    x = [mjd_to_date(x[ii])  for ii in range(len(x))]
    y = data_dewar["level"][datasz-num_data_show:datasz].to_numpy()


    # Processing PID data
    data_pid = data_pid.iloc[-num_data_show:-1, :]
    for ii in range(len(data_pid)):
        data_pid["MJD"].iloc[ii] = mjd_to_date(data_pid["MJD"].iloc[ii]) 

    # Main plot
    time.sleep(5) # pause a little bit
    width = float(request.args.get("width", 800))
    height = float(request.args.get("height", 600))
    dpi = 150  # Adjust this value for your desired plot resolution
    fig = Figure(figsize=(width / dpi, height / dpi), dpi=dpi)
    axes = fig.subplots(2, 2)

    # color scheme
    colors = {'Outer bottom 1': 'slategrey', 'Outer bottom 2': 'lightskyblue'}
    colors.update({'Inner bottom 1': 'red', 'Inner bottom 2': 'darkred'})
    colors.update({'Uout': 'tab:green'})

    # Inner bot
    offset_in_bot1 = data_pid["inn_bot_1"].iloc[0]
    offset_in_bot2 = data_pid["inn_bot_2"].iloc[0]
    axes[1, 1].clear()
    axes[1, 1].plot(data_pid["MJD"], data_pid["inn_bot_1"] - offset_in_bot1, '.', label='Sensor1 - {} K'.format(np.round(offset_in_bot1, decimals=3)), color=colors['Inner bottom 1'])
    axes[1, 1].plot(data_pid["MJD"], data_pid["inn_bot_2"] - offset_in_bot2, '.', label='Sensor2 - {} K'.format(np.round(offset_in_bot2, decimals=3)), color=colors['Inner bottom 2'])
    axes[1, 1].set(ylabel='Temperature (K)', xlabel='Time (Hours)', title="Inner bottom ",)
    axes[1, 1].set_xticklabels(axes[1, 1].get_xticklabels(), rotation=45)
    axes[1, 1].grid()
    axes[1, 1].legend()

    # Outer bot
    offset_out_bot1 = data_pid["out_bot_1"].iloc[0]
    offset_out_bot2 = data_pid["out_bot_2"].iloc[0]
    axes[0, 1].clear()
    axes[0, 1].plot(data_pid["MJD"], data_pid['out_bot_1'] - offset_out_bot1, '.', label='Sensor1 - {} K'.format(np.round(offset_out_bot1, decimals=3)), color=colors['Outer bottom 1'])
    axes[0, 1].plot(data_pid["MJD"], data_pid['out_bot_2'] - offset_out_bot2, '.', label='Sensor2 - {} K'.format(np.round(offset_out_bot2, decimals=3)), color=colors['Outer bottom 2'])
    axes[0, 1].set(ylabel='Temperature (K)', xlabel='Time (Hours)', title="Outer bottom")
    axes[0, 1].set_xticklabels(axes[0, 1].get_xticklabels(), rotation=45)
    axes[0, 1].grid()
    axes[0, 1].legend()

    # Control signal
    axes[1, 0].clear()
    axes[1, 0].plot(data_pid["MJD"], data_pid['Uout'], '.', label='Control voltage', color=colors['Uout'])
    axes[1, 0].set(ylabel='Control (arb.)', xlabel='Time (Hours)', title="Outer bot control voltage. \n Hit limit -> Change BK pw/sup voltage", ylim=[-1, 11])
    axes[1, 0].axhline(10, label="limit", color="red", lw=2)
    axes[1, 0].axhline(0, label=None, color="red", lw=2)
    axes[1, 0].grid()
    axes[1, 0].set_xticklabels(axes[1, 0].get_xticklabels(), rotation=45)
    axes[1, 0].legend()

    # Dewar level
     ## Detect the a big gradient for checking the calibration of the mjm 
    dydt = np.diff(y)
    indx_peak = np.argwhere(dydt > 30)
    axes[0, 0].plot(x, y, '.', ls="", label="data")
    # axes[0, 0].axvline(x[indx_peak], lw=2, color="red")
    axes[0, 0].set(xlabel="Time", ylabel="Camera level reading", title="Dewar Level = {} on {}. \n Single step jump = BAD CALIBRATION! CHECK CAMERA! ".format(y[-1], x[-1].strftime("%H:%M:%S")), )
    axes[0, 0].set_xticklabels(axes[0, 0].get_xticklabels(), rotation=45)
    axes[0, 0].legend()
    axes[0, 0].grid()
    fig.suptitle("si3.colorado.edu. Last update: {}".format(str(datetime.now().replace(microsecond=0))))
    fig.tight_layout()

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = pybase64.b64encode(buf.getbuffer()).decode("ascii")
    return data

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80,)