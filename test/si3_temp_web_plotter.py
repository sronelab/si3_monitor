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
    file_path = os.path.join(os.path.dirname(__file__), "21_11_01_00_00_03.dat")

    data = pd.read_csv(
        file_path,
        header=0,
        skiprows=[1],
        delimiter=r'\s+',
    )

    # color scheme
    colors = {'Outer bottom 1': 'slategrey', 'Outer bottom 2': 'lightskyblue'}
    colors.update({'Inner bottom 1': 'red', 'Inner bottom 2': 'darkred'})
    colors.update({'Uout': 'tab:green'})


    # Main plot
    width = float(request.args.get("width", 400))
    height = float(request.args.get("height", 300))
    dpi = 200  # Adjust this value for your desired plot resolution
    fig = Figure(figsize=(width / dpi, height / dpi), dpi=dpi)    
    axes = fig.subplots(2, 2)
    # Inner bot
    axes[0, 0].clear()
    axes[0, 0].plot(data["time"], data["inn_bot_1"], '.', label='Inner bottom 1', color=colors['Inner bottom 1'])
    axes[0, 0].plot(data["time"], data["inn_bot_2"], '.', label='Inner bottom 2', color=colors['Inner bottom 2'])
    axes[0, 0].set(ylabel='Temperature (K)', xlabel='Time (Hours)', title="Inner bottom")
    axes[0, 0].grid()
    axes[0, 0].legend()

    # Outer bot
    axes[0, 1].clear()
    axes[0, 1].plot(data["time"], data['out_bot_1'], '.', label='Outer bottom 1', color=colors['Outer bottom 1'])
    axes[0, 1].plot(data["time"], data['out_bot_2'], '.', label='Outer bottom 2', color=colors['Outer bottom 2'])
    axes[0, 1].set(ylabel='Temperature (K)', xlabel='Time (Hours)', title="Outer bottom")
    axes[0, 1].grid()
    axes[0, 1].legend()

    # Control signal
    axes[1, 0].clear()
    axes[1, 0].plot(data["time"], data['Uout'], '.', label='Control voltage', color=colors['Uout'])
    axes[1, 0].set(ylabel='Control (arb.)', xlabel='Time (Hours)', title="Control voltage")
    axes[1, 0].grid()
    axes[1, 0].legend()

    # Notes 
    # axes[-1, -1].clear()
    # axes[-1, -1].annotate(
    #     "",
    #     (0, 0.5))
    # axes[-1, -1].axis("off")

    fig.suptitle("Si3 live temperature monitor. Last update: {}".format(str(datetime.datetime.now().replace(microsecond=0))))
    fig.tight_layout()

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = pybase64.b64encode(buf.getbuffer()).decode("ascii")
    return data

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80,)