from datetime import datetime

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
from time import sleep
from datetime import datetime, timedelta
import pandas as pd
import os
import glob
import sys

sys.path.append(os.getcwd())
import db_cred


def mjd_to_date(mjd):
    # The reference date for MJD (November 17, 1858, 00:00 UTC)
    reference_date = datetime(1858, 11, 17, 0, 0, 0)

    # Convert MJD to a timedelta
    days_since_reference = timedelta(days=mjd)

    # Add the timedelta to the reference date
    return reference_date + days_since_reference - timedelta(hours=6) # converting to local time zone (manually!)


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

# keys to save
key_dewar = ["MJD", "level"]
key_pid = [
    "MJD", 'out_bot_1', 'inn_bot_1', 'out_bot_2', 'inn_bot_2', 'out_top', 'RT', 'Uout'
]

# # test codes
# for key in key_dewar:
#     print(data_dewar[key].to_numpy()[-1])
# for key in key_pid:
#     print(data_pid[key].to_numpy()[-1])

# Send data to the database
with InfluxDBClient(url=db_cred.url, token=db_cred.token, org=db_cred.org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # send dewar data
    for key in key_dewar:
        data_dewar[key].to_numpy()[-1]
        data = f"dewar,tag={key} value={data_dewar[key].to_numpy()[-1]}"
        write_api.write(db_cred.bucket, db_cred.org, data)

    # send pid data
    for key in key_pid:
        data_pid[key].to_numpy()[-1]
        data = f"pid,tag={key} value={data_pid[key].to_numpy()[-1]}"
        write_api.write(db_cred.bucket, db_cred.org, data)

    client.close()
    
print(os.path.dirname(sys.executable))