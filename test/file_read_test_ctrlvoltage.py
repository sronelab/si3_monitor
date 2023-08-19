import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

DATA_PATH = r"C:\Users\Ye Lab\Google Drive\Data\21 cm Si Cavity\Cryostat"
data_list = glob.glob(os.path.join(DATA_PATH, "*.dat"))
most_recent_file = max(data_list, key=os.path.getmtime)
data = pd.read_csv(
    most_recent_file,
    header=0,
    skiprows=[1],
    delimiter=r'\s+',
)
data = data.iloc[-10000:-1, :]

# print(data)
def mjd_to_date(mjd):
    # The reference date for MJD (November 17, 1858, 00:00 UTC)
    reference_date = datetime(1858, 11, 17, 0, 0, 0)

    # Convert MJD to a timedelta
    days_since_reference = timedelta(days=mjd)

    # Add the timedelta to the reference date
    return reference_date + days_since_reference

for ii in range(len(data)):
    data["MJD"].iloc[ii] = mjd_to_date(data["MJD"].iloc[ii])

fig, axes = plt.subplots(2, 2)
# color scheme
colors = {'Outer bottom 1': 'slategrey', 'Outer bottom 2': 'lightskyblue'}
colors.update({'Inner bottom 1': 'red', 'Inner bottom 2': 'darkred'})
colors.update({'Uout': 'tab:green'})

# Inner bot
offset_in_bot1 = data["inn_bot_1"].iloc[0]
offset_in_bot2 = data["inn_bot_2"].iloc[0]
axes[0, 0].clear()
axes[0, 0].plot(data["MJD"], data["inn_bot_1"] - offset_in_bot1, '.', label='Sensor1 - {} K'.format(np.round(offset_in_bot1, decimals=3)), color=colors['Inner bottom 1'])
axes[0, 0].plot(data["MJD"], data["inn_bot_2"] - offset_in_bot2, '.', label='Sensor2 - {} K'.format(np.round(offset_in_bot2, decimals=3)), color=colors['Inner bottom 2'])
axes[0, 0].set(ylabel='Temperature (K)', xlabel='Time (Hours)', title="Inner bottom ",)
axes[0, 0].set_xticklabels(axes[0, 0].get_xticklabels(), rotation=45)
axes[0, 0].grid()
axes[0, 0].legend()

# Outer bot
offset_out_bot1 = data["out_bot_1"].iloc[0]
offset_out_bot2 = data["out_bot_2"].iloc[0]
axes[0, 1].clear()
axes[0, 1].plot(data["MJD"], data['out_bot_1'], '.', label='Sensor1 - {} K'.format(np.round(offset_out_bot1, decimals=3)), color=colors['Outer bottom 1'])
axes[0, 1].plot(data["MJD"], data['out_bot_2'], '.', label='Sensor2 - {} K'.format(np.round(offset_in_bot2, decimals=3)), color=colors['Outer bottom 2'])
axes[0, 1].set(ylabel='Temperature (K)', xlabel='Time (Hours)', title="Outer bottom")
axes[0, 1].set_xticklabels(axes[0, 1].get_xticklabels(), rotation=45)
axes[0, 1].grid()
axes[0, 1].legend()

# Control signal
axes[1, 0].clear()
axes[1, 0].plot(data["MJD"], data['Uout'], '.', label='Control voltage', color=colors['Uout'])
axes[1, 0].set(ylabel='Control (arb.)', xlabel='Time (Hours)', title="Control voltage")
axes[1, 0].grid()
axes[1, 0].set_xticklabels(axes[1, 0].get_xticklabels(), rotation=45)
axes[1, 0].legend()
fig.tight_layout()
plt.show()
