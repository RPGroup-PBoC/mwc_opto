#%%
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import photo.bayes
import photo.viz 
GP_FORCE = False
GP_SAMPLE = False
colors = photo.viz.plotting_style()
data = pd.read_csv('../../data/experiment_3_traces_tidy.csv')
data = data[data['region']=='activated']


# Load the  inferrential model 
model = photo.bayes.StanModel('../stan/betancourt_gp.stan', force_compile=GP_FORCE)
preact = data[data['activation_time_s']==0]
act = data[data['activation_time_s']!=0]
data_dict = {'N':len(preact),
             'x':preact['experiment_time_s'].values,
             'y': preact['mean_mcherry_intensity'].values,
             'N_predict':len(act),
             'x_predict':act['experiment_time_s']}
#%%
if GP_SAMPLE:
    fit, samples = model.sample(data_dict)
    samples.to_csv('../../data/exp3_preact_gp_samples.csv', index=False)
    summary = model.summarize_parameters() 
    summary.to_csv('../../data/exp3_preact_gp_summary.csv', index=False)
else:
    print('Loaded summary statistics.')
    summary = pd.read_csv('../../data/exp3_preact_gp_summary.csv')
    # samples = pd.read_csv('../../data/exp3_preact_gp_samples.csv')


# %%
# if GP_SAMPLE != True:
#     fig, ax = plt.subplots(1, 1)
#     ax.plot(preact['experiment_time_s'], preact['mean_mcherry_intensity'], '.')
#     pred = summary[summary['parameter']=='y_predict']
#     ax.plot(act['experiment_time_s'], pred['median'], '-', color=colors['red'])

#     # Plot the deciles. 
#     cols = ['90th', '80th', '70th', '60th', '50th', '40th',
#             '30th', '20th', '10th', '1st']
#     alphas = np.linspace(0.1, 0.6, len(cols))
#     for i, c in enumerate(cols):
#         lower = pred[f'{c}_percentile_lower'].values
#         upper = pred[f'{c}_percentile_upper'].values
#         ax.fill_between(act['experiment_time_s'], lower, upper, color='black',
#                         alpha=alphas[i])
    

# %%
KIN_FORCE = False
KIN_SAMPLE = True

#%%
# Load the model for the GP subtraction kinetics inference.
kinetic_model = photo.bayes.StanModel('../stan/bg_subtraction_kinetic_inference.stan', 
                                      force_compile=KIN_FORCE)

# Get the indices at which the final activation measurement is taken. 

power_density = data.groupby(['point_idx'])['power_density_nW'].max()
exp_time_fc = data.groupby(['point_idx'])['experiment_time_s'].max().values
inds = [np.where(data['experiment_time_s'].values == k)[0][0] for k in exp_time_fc]

# Establish the data dictionary for the inference. 
data_dict = {
        'J': len(data['point_idx'].unique()),
        'N': len(data),
        'idx': data['point_idx'].values,
        'mcherry_int': data['mean_mcherry_intensity'].values,
        'experiment_time': data['experiment_time_s'].values,
        'activation_time': data['activation_time_s'].values,
        'power_density': power_density,
        'timepoint_idx': inds,
        'micro_conc': 700, # in nM
        'preact_sd': np.std(preact['mean_mcherry_intensity']),
        'preact_mean': np.mean(preact['mean_mcherry_intensity']),
        'alpha_mean': summary[summary['parameter']=='alpha']['mean'].values[0],
        'rho_mean': summary[summary['parameter']=='rho']['mean'].values[0],
}



if KIN_SAMPLE:
    fit, kin_samples = kinetic_model.sample(data_dict, iter=1000)
    kin_samples.to_csv('../../data/exp3_kinetic_samples.csv', index=False)
    kin_summary = kinetic_model.summarize_parameters() 
    kin_summary.to_csv('../../data/exp3_kinetic_summary.csv', index=False)
else:
    print('loading parameter samples and summaries')
    kin_summary = pd.read_csv('../../data/exp3_kinetic_summary.csv')
    kin_samples = pd.read_csv('../../data/exp3_kinetic_samples.csv') 
    
# %%
if KIN_SAMPLE == False:
    DIM = 6
    kon = kin_samples[f'kon[{DIM}]'].values
    sat = kin_samples[f'saturation[{DIM}]'].values
    sig = kin_samples[f'sigma'].values
    fig, ax = plt.subplots(2, 2)
    ax[0, 0].set_xscale('log')
    ax[1, 0].set_xscale('log')
    ax[0,0].plot(kon, sat, ',', color='k')
    ax[0,1].plot(sig, sat, ',', color='k')
    ax[1,0].plot(kon, sig, ',', color='k')
    
    ax[0,0].set_xlabel('kon')
    ax[1,0].set_xlabel('kon')
    ax[1, 1].set_xlabel('sig')
    ax[0, 1].set_xlabel('sig')
    ax[0,0].set_ylabel('sat')
    ax[1,0].set_ylabel('sig')

    fig, ax = plt.subplots(2, 2)
    theta_a = kin_samples['theta_a'].values
    theta_i = kin_samples['theta_i'].values
    ep_ai = kin_samples['ep_ai'].values
    ax[0, 0].plot(ep_ai, theta_a, 'k,')
    ax[1, 0].plot(ep_ai, theta_i, 'k,')
    ax[1, 1].plot(theta_a, theta_i, 'k,')
    ax[0, 0].set_xlabel('ep_ai')
    ax[1, 0].set_xlabel('ep_ai')
    ax[1, 1].set_xlabel('theta_a')
    ax[0, 0].set_ylabel('theta_a')
    ax[1, 0].set_ylabel('theta_i')
    ax[1, 1].set_ylabel('theta_i')

# %%
# Look exclusively at the saturation level and map to power density
sat = kin_summary[kin_summary['parameter']=='saturation']
fc = kin_summary[kin_summary['parameter']=='fold_change']
sat.sort_values(by='dimension', inplace=True)
fc.sort_values(by='dimension', inplace=True)
power_density = data.groupby(['point_idx'])['power_density_nW'].max().reset_index()
sat['power_density_nW'] = power_density['power_density_nW'].values
fc['power_density_nW'] = power_density['power_density_nW'].values
sat.drop(columns=['parameter', 'dimension', 'mass_fraction', 'hpd_min'], inplace=True)
fc.drop(columns=['parameter', 'dimension', 'mass_fraction', 'hpd_min'], inplace=True)

# Generate a dataframe for the deciles that is useable
sat_deciles = pd.DataFrame([])
for g, d in sat.groupby(['power_density_nW']):
    cols = np.unique([k.split('_')[0] for k in d.keys() if 'percentile' in k])
    for c in cols: 
        lower = d[f'{c}_percentile_lower'].values[0]
        upper = d[f'{c}_percentile_upper'].values[0]
        sat_deciles = sat_deciles.append({'power_density_nW':g,
                                          'percentile': int(c[:-2]),
                                          'lower_bound':lower,
                                          'upper_bound': upper},
                                          ignore_index=True)

fc_deciles = pd.DataFrame([])
for g, d in fc.groupby(['power_density_nW']):
    cols = np.unique([k.split('_')[0] for k in d.keys() if 'percentile' in k])
    for c in cols: 
        lower = d[f'{c}_percentile_lower'].values[0]
        upper = d[f'{c}_percentile_upper'].values[0]
        fc_deciles = fc_deciles.append({'power_density_nW':g,
                                          'percentile': int(c[:-2]),
                                          'lower_bound':lower,
                                          'upper_bound': upper},
                                          ignore_index=True)


sat_deciles['percentile']  = sat_deciles['percentile'].astype(int)
fc_deciles['percentile']  = fc_deciles['percentile'].astype(int)

# Save the deciles to disk. 
sat_deciles.to_csv('../../data/exp3_saturation_deciles.csv', index=False)
fc_deciles.to_csv('../../data/exp3_foldchange_deciles.csv', index=False)
#%%

if KIN_SAMPLE == False:
    # Plot the deciles with changing colors
    power_d = np.linspace(0, 5, 100)  
    theo = (1 + np.exp(-ep_ai.mean())) / (1 + np.exp(-ep_ai.mean()) * (1 + power_d / theta_i.mean()) / (1 + power_d / theta_a.mean()))
    percs = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 1]
    lws = {p:c for p, c in zip(percs, np.linspace(0.75, 5, len(percs)))}
    alphas = {p:c for p, c in zip(percs, np.linspace(0.5, 1, len(percs)))}
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    for g, d in sat_deciles.groupby(['power_density_nW', 'percentile']):
        ax[0].vlines(g[0], d['lower_bound'].values[0], d['upper_bound'].values[0], 
                color=colors['blue'], lw=lws[g[1]], alpha=alphas[g[1]])
    for g, d in fc_deciles.groupby(['power_density_nW', 'percentile']):
        ax[1].vlines(g[0], d['lower_bound'].values[0], d['upper_bound'].values[0], 
                color=colors['red'], lw=lws[g[1]], alpha=alphas[g[1]])

    ax[1].plot(power_d, theo, 'k-')
    # ax.plot(sat['power_density_nW'], sat['mean'].values, 'o', ms=4, 
        #    markerfacecolor='white', markeredgewidth=0.25, markeredgecolor='k')

    ax[0].set_xlabel('power density [nW / µm$^2$]')
    ax[1].set_xlabel('power density [nW / µm$^2$]')
    ax[0].set_ylabel('saturation intensity [a.u.]')
    ax[1].set_ylabel('fold-change')
    ax[0].set_title('experiment 3, inferred saturation intensities', fontsize=10)
    ax[1].set_title('experiment 3, inferred foldchange', fontsize=10)
    plt.savefig('../../figures/experiment3_inferred_saturation_foldchange_deciles.pdf', 
                bbox_inches='tight')

# %%

# %%