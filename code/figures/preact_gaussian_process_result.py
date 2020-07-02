#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import light.viz
colors = light.viz.plotting_style()

# Load the dataset. 
data = pd.read_csv('../processing/20200701_abrar_processed_munging/output/20200701_abrar_processed_data_tidy.csv')
exp1 = data[data['experiment_id']==1]

# Load the sampling info
predicted = pd.read_csv('../../data/preact_gaussian_process_prediction.csv')
#

# %%
# set up the plot. 
fig, ax = plt.subplots(1, 1, figsize=(6, 4))
ax.set_xlabel('time [min]')
ax.set_ylabel('preactivation intensity [a.u.]')

#plot the result of the gaussian process.
_ = ax.plot(predicted['time'], predicted['mean'], '-', lw=1, color=colors['red'],
            label='Gaussian process mean value')
_ = ax.fill_between(predicted['time'], predicted['hpd_min'], predicted['hpd_max'], 
            color=colors['red'], alpha=0.25, label='95% credible region')

_ = ax.plot(exp1['time_min'], exp1['preact_intensity'], 'o', color=colors['red'], ms=5,
            label='observation')
_ = ax.legend()


# %%
