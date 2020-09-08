#%%
import numpy as np
import pandas as pd

# Define some constants.
EXP_ID = 3

# Load the tidy data converted from xslx by hand. 
trace = pd.read_csv(f'../../../data/experiment_{EXP_ID}_time_traces.csv') 
preact_exp = pd.read_csv(f'../../../data/experiment_{EXP_ID}_preact_intensities.csv')
preact = pd.read_csv('../../../data/preprocessed_data_tidy.csv')

# Restrict the preactivation data for experiment 3
preact = preact[preact['experiment_id']==EXP_ID] 

# Iterate through the experiment preactivation intensities I was given for each 
# point and map the power density. 
dfs = []
for g, d in preact.groupby(['time_min']):
    preact_exp.loc[preact_exp['time_min']==np.round(g, decimals=2), 
                  'power_density_nW'] = d['power_density_nW'].values[0]

preact_exp.rename(columns={'relative_time_s':'experiment_time_s'}, inplace=True)


# Now map the power densities to each time trace. 
for g, d in preact_exp.groupby(['point_idx', 'power_density_nW']):
    trace.loc[trace['point_idx']==g[0], 'power_density_nW'] = g[1]


# Merge the dataframes together updating time. 
dfs = []
for g, d in preact_exp.groupby(['point_idx']):
    # Get the "clock" time
    relative_time = d['experiment_time_s'].values[0]
    d = d[['point_idx', 'experiment_time_s', 'power_density_nW', 'mean_preact_intensity']]
    d['region'] = 'preactivation'
    d['activation_time_s'] = 0 
    d.rename(columns={'mean_preact_intensity':'mean_mcherry_intensity'}, inplace=True)

    # Get the corresponding trace for a single point 
    point = trace[trace['point_idx']==g].copy()
    point['experiment_time_s'] = relative_time + point['activation_time_s']
    dfs.append(point)
    dfs.append(d)
points = pd.concat(dfs, sort=False)

# Save the complete tidy data to disk. 
points.to_csv(f'../../../data/experiment_{EXP_ID}_traces_tidy.csv', index=False)

# %% preact_exp3.head() # %% 