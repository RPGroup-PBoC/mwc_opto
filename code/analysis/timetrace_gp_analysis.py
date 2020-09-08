#%%
import numpy as np
import pandas as pd
import photo.viz
import photo.bayes
import photo.stats
import matplotlib.pyplot as plt
import tqdm
# force = True
# sample = True
colors = photo.viz.plotting_style()

#%%
# Load the data set. 
data = pd.read_csv('../../data/experiment_3_traces_tidy.csv', comment='#')

# Ignore the dark regions for now. 
traces = data[data['region']=='activated']
preact = data[data['region']=='preactivation']

# Load the stan model.
model = photo.bayes.StanModel('../stan/betancourt_gp.stan', force_compile=force)

#%%
# Assemble the data dictionary. 
data_dict = {'N': len(preact),
             'N_predict': len(traces),
             'x': preact['experiment_time_s'].values/60,
             'x_predict': traces['experiment_time_s'].values/60,
             'y': preact['mean_mcherry_intensity'].values}

# Sample. 
if sample:
    fit, samples = model.sample(data_dict)
    params = model.summarize_parameters()
    params.to_csv('../../data/experiment_3_gp_preact_params.csv', index=False)

else:
    params = pd.read_csv('../../data/experiment_3_gp_preact_params.csv')
#%% 
fig, ax = plt.subplots(1, 1)
pred = params[params['parameter']=='y_predict']
ax.plot(preact['experiment_time_s'], preact['mean_mcherry_intensity'], 'k.')
ax.plot(traces['experiment_time_s'], pred['median'], 'k-')
ax.fill_between(traces['experiment_time_s'].values, pred['hpd_min'].values, pred['hpd_max'].values, color='k', alpha=0.25)

# %%
#Map the predicted times to the points
traces['mch_median_sub'] = traces['mean_mcherry_intensity'].values - pred['median'].values
traces.to_csv('../../data/experiment_3_traces_subtracted.csv', index=False)
power_density = data['power_density_nW'].unique()[0]

fig, ax = plt.subplots(1, 2, figsize=(7, 3))
ax[0].set_xlabel('time')
ax[0].set_ylabel('intensity [a.u.]')

_traces = traces[traces['power_density_nW']==power_density]
for g, d in _traces.groupby(['point_idx']):
    ax[0].plot(d['activation_time_s'], d['mean_mcherry_intensity'], 'o',
            markeredgewidth=0.5, markeredgecolor='k', label=np.int(d['experiment_time_s'].min()/60),
                alpha=0.5)
    ax[1].plot(d['activation_time_s'], d['mch_median_sub'].values, 'o', alpha=0.5,
        markeredgewidth=0.5, markeredgecolor='k', label='__nolegend__')
leg = ax[0].legend(title='elapsed time [min]', fontsize=6)
leg.get_title().set_fontsize(8)
ax[0].set_title('raw measurements', fontsize=8)
ax[1].set_title('GP background subtraction', fontsize=8)            

# plt.savefig(f'../../figures/experiment_3_GP_bg_subtraction_{np.round(power_density,
# decimals=2)}_nW.pdf') = True
#%% for each power density, see how the saturation level changes with time. 
for g, d in traces.groupby(['power_density_nW'])

#%%
sample = False
force = False
# Compile the model for inference of k on and the saturaton.

kinetic_model = photo.bayes.StanModel('../stan/binding_kinetics_inference.stan',
                                      force_compile=force)

# assemble the data dictionary. 
data_dict = {
    'J':traces['point_idx'].max(),
    'N': len(traces),
    'idx': traces['point_idx'].values.astype(int),
    'micro_conc': 0.700, 
    'mcherry_sub': traces['mch_median_sub'].values,
    'relative_time': traces['activation_time_s']}

if sample == True:
    fit, samples = kinetic_model.sample(data_dict)
    params = kinetic_model.summarize_parameters()
    params.to_csv('../../data/experiment_3_kinetic_parameters_summary.csv', 
                  index=False)
    samples.to_csv('../../data/experiment_3_kinetic_parameters_samples.csv', 
                  index=False)
else:
    params = pd.read_csv('../../data/experiment_3_kinetic_parameters_summary.csv')
    samples = pd.read_csv('../../data/experiment_3_kinetic_parameters_samples.csv')

# define a time range and, for each fit, compute the credible region. 
dfs = []
for g, d in tqdm.tqdm(traces.groupby(['point_idx'])):
    obs = samples[f'observed_onrate[{g}]'].values
    sat = samples[f'saturation[{g}]'].values
    time_range = np.linspace(0, d['activation_time_s'].max() + 3, 300)
    fit_cred = np.zeros((2, len(time_range)))
    for i, t in enumerate(time_range):
       val = sat * (1 - np.exp(-t * obs))
       fit_cred[:, i] = photo.stats.compute_hpd(val, 0.95)
    _df = pd.DataFrame([]) 
    _df['hpd_min'] = fit_cred[0, :]
    _df['hpd_max'] = fit_cred[1, :]
    _df['activation_time_s'] = time_range
    _df['power_density_nW'] = d['power_density_nW'].values[0]
    _df['elapsed_time'] = d['experiment_time_s'].values[0]
    _df['point_idx'] = g
    dfs.append(_df)

fit_df = pd.concat(dfs, sort=False)
fit_df.to_csv('../../data/experiment_3_hpd_fit.csv', index=False)
# %%


fig, ax = plt.subplots(1, 2, figsize=(7, 3))
ax[0].set_xlabel('time')
ax[0].set_ylabel('intensity [a.u.]')
power_density = traces['power_density_nW'].unique()[0]
_traces = traces[traces['power_density_nW']==power_density]
for g, d in _traces.groupby(['point_idx']):
    _fit = fit_df[fit_df['point_idx']==g]
    ax[0].plot(d['activation_time_s'], d['mean_mcherry_intensity'], 'o',
            markeredgewidth=0.5, markeredgecolor='k', label=np.int(d['experiment_time_s'].min()/60),
                alpha=0.5)
    ax[1].plot(d['activation_time_s'], d['mch_median_sub'].values, 'o', alpha=0.5,
        markeredgewidth=0.5, markeredgecolor='k', label='__nolegend__')
    ax[1].fill_between(_fit['activation_time_s'], _fit['hpd_min'], _fit['hpd_max'], alpha=0.4)
leg = ax[0].legend(title='elapsed time [min]', fontsize=6)
leg.get_title().set_fontsize(8)
ax[0].set_title('raw measurements', fontsize=8)
ax[1].set_title('GP background subtraction', fontsize=8)      

# %%
