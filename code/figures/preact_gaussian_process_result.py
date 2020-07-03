#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import light.viz
colors = light.viz.plotting_style()
palette = colors.values()

# Load the dataset. 
data = pd.read_csv('../../data/preprocessed_data_tidy.csv')


# Load the sampling info
predicted = pd.read_csv('../../data/preact_gaussian_process_prediction.csv')
#

# %%
# set up the plot. 
fig, ax = plt.subplots(1, 1, figsize=(6, 4))
ax.set_xlabel('time [min]')
ax.set_ylabel('preactivation intensity [a.u.]')

#plot the result of the gaussian process.
_colors = [colors['red'], colors['blue'], colors['green'], colors['purple'], 'k', 
           colors['dark_brown'], ]
exp_ids = data['experiment_id'].unique()
for i, no in enumerate(exp_ids):
    _data = data[data['experiment_id']==no]
    _predicted = predicted[predicted['experiment_id']==no]
    _ = ax.plot(_predicted['time'], _predicted['mean'], '-', lw=1, color=_colors[i],
            label='Gaussian process mean value')
    _ = ax.fill_between(_predicted['time'], _predicted['hpd_min'], _predicted['hpd_max'], 
            color=_colors[i], alpha=0.25, label='95% credible region')
    _ = ax.plot(_data['time_min'], _data['preact_intensity'], 'o', color=_colors[i], ms=5,
            label='observation')
# _ = ax.legend()

# %%
