import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

DATA_PATH = r"C:\Users\Ye Lab\Google Drive\Data\21 cm Si Cavity\Dewar"
data_list = glob.glob(os.path.join(DATA_PATH, "*.dat"))
most_recent_file = max(data_list, key=os.path.getmtime)
data = pd.read_csv(
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
    return reference_date + days_since_reference

datasz = len(data["MJD"])-1
num_data_show = 1200
x = data["MJD"][datasz-num_data_show:datasz].to_numpy()
x = [mjd_to_date(x[ii]) for ii in range(len(x))]
y = data["level"][datasz-num_data_show:datasz].to_numpy()

fig, axes = plt.subplots()
axes.plot(x, y)
axes.set(xlabel="Time", ylabel="Camera level reading", title="Dewar Level. MIGHT NOT BE ACCURATE!")
axes.set_xticklabels(axes.get_xticklabels(), rotation=45)
fig.tight_layout()
plt.show()
