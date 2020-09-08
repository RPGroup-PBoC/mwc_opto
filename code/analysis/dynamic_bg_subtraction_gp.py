#%%
import numpy as np
import pandas as pd
import photo.viz
import photo.bayes
import photo.stats
import matplotlib.pyplot as plt
import tqdm
force = True
colors = photo.viz.plotting_style()

#%%
# Load the data set. 
data = pd.read_csv('../../data/experiment_3_traces_tidy.csv', comment='#')

# Ignore the dark regions for now. 
traces = data[data['region']=='activated']
preact = data[data['region']=='preactivation']

# Load the stan model.
model = photo.bayes.StanModel('../stan/preact_gp_trace_intensities.stan', force_compile=force)

# Assemble the data dictionary. 
data_dict = {'J': len(data['point_idx'].unique()),
             'N_trace': len(traces),
             'N_preact': len(preact),
             'point_idx': traces['point_idx'].values,
             'mch_trace': traces['mean_mcherry_intensity'].values,
             'relative_time_trace': traces['activation_time_s'].values,
             'experiment_time_trace': traces['experiment_time_s'].values,
             'mch_preact': preact['mean_mcherry_intensity'].values,
             'experiment_time_preact': preact['experiment_time_s'].values}

print('beginning sampling...')
fit, samples = model.sample(data_dict)
print('finished!')

# %%
params = model.summarize_parameters(parnames=['rho', 'alpha', 'gp_sigma', 'mch_subtracted',
                                              'mch_predicted'])
params.to_csv('../../data/experiment_3_gp_bg_subtraction_params.csv', index=False)
#%% Map params to time
subs = params[params['parameter']=='mch_subtracted']
subs.sort_values('dimension', inplace=True)
subs['activation_time_s'] = traces['activation_time_s'].values
subs['point_idx'] = traces['point_idx'].values

# %%
power_density = data['power_density_nW'].unique()[10]

fig, ax = plt.subplots(1, 2, figsize=(7, 3))
ax[0].set_xlabel('time')
ax[0].set_ylabel('intensity [a.u.]')

_traces = traces[traces['power_density_nW']==power_density]
for g, d in _traces.groupby(['point_idx']):
    ax[0].plot(d['activation_time_s'], d['mean_mcherry_intensity'], 'o',
            markeredgewidth=0.5, markeredgecolor='k', label=np.int(d['experiment_time_s'].min()/60),
                alpha=0.5)

    _subs = subs[subs['point_idx'] == g] 
    ax[1].plot(_subs['activation_time_s'], _subs['median'], 'o', alpha=0.5,
        markeredgewidth=0.5, markeredgecolor='k', label='__nolegend__')
leg = ax[0].legend(title='elapsed time [min]', fontsize=6)
leg.get_title().set_fontsize(8)
ax[0].set_title('raw measurements', fontsize=8)
ax[1].set_title('GP background subtraction', fontsize=8)            
plt.savefig(f'../../figures/experiment_3_GP_bg_subtraction_{np.round(power_density, decimals=2)}_nW.pdf')
# %%
fig, ax = plt.subplots(1,1)
ax.plot(preact['experiment_time_s'], preact['mean_mcherry_intensity'], 'o', 
        label='data')
pred = params[params['parameter']=='mch_predicted']
ax.plot(preact['experiment_time_s'], pred['median'], color=colors['blue'])
ax.fill_between(preact['experiment_time_s'], pred['hpd_min'], pred['hpd_max'],
                color=colors['light_blue'], alpha=0.5)
plt.savefig(f'../../figures/experiment_3_GP.pdf')


# %%
power_density

# %%
