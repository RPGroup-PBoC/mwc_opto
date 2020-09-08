#%% 
import numpy as np
import pandas as pd 
import photo.stats 
import photo.bayes 
force = True
sample = True
traces = pd.read_csv('../../data/experiment_3_traces_subtracted.csv')

# Assign point identities to each power
traces['power_idx'] = traces.groupby(['power_density_nW']).ngroup() + 1 

model = photo.bayes.StanModel('../stan/hierarchical_binding_kinetics.stan', 
                force_compile=force)


# Define the datadict and sample
power_vec = [g[0] for g, d in traces.groupby(['power_idx', 'point_idx'])]
data_dict = {'J': len(traces['power_idx'].unique()),
             'M': len(traces['point_idx'].unique()),
             'N': len(traces),
             'power_idx': power_vec,
             'point_idx': traces['point_idx'],
             'micro_conc': 0.7,
             'mcherry_sub': traces['mch_median_sub'],
             'relative_time': traces['activation_time_s']}

if sample:
    fit, samples = model.sample(data_dict, iter=5000, control=dict(adapt_delta=0.999))
    params = model.summarize_parameters()
    samples.to_csv('../../data/experiment_3_hierarchical_kinetics_samples.csv', index=False) 
    for g, d in traces.groupby(['point_idx']):
        params.loc[params['dimension']==g, 'power_density_nW'] =  d['power_density_nW'].values[0]
        params.loc[params['dimension']==g, 'experiment_time_s'] =  d['experiment_time_s'].values[0]
    params.to_csv('../../data/experiment_3_hierarchical_kinetics_summary.csv', index=False)
    
else:
    samples = pd.read_csv('../../data/experiment_3_hierarchical_kinetics_samples.csv')
    params = pd.read_csv('../../data/experiment_3_hierarchical_kinetics_summary.csv')

#%
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



# %%
