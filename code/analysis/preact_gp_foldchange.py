#%%
import numpy as np
import pandas as pd
import light.bayes
import light.stats
import tqdm
force = False

# Load the data set. 
data = pd.read_csv('../../data/preprocessed_data_tidy.csv', comment='#')

# Load the stan model.
model = light.bayes.StanModel('../stan/preact_gp_foldchange.stan', force_compile=force)

# Define the time range over which to predict. 
N_predict = 150 
_samples = []
_params = []
_means = []
for g, d in tqdm.tqdm(data.groupby(['experiment_id'])):
    t_predict = np.linspace(0, d['time_min'].max() + 10,  N_predict)
    N_exp = len(d)

    # Set up the data dictionary 
    data_dict = {'N': N_exp, 'N_predict': N_predict, 
                'x': d['time_min'], 'x_predict':t_predict, 
                'y':d['preact_intensity'],
                'total_intensity': d['total_intensity']}

    # Sample the model. 
    fit, samples = model.sample(data_dict, iter=3000, control=dict(adapt_delta=0.95))
    params = model.summarize_parameters()
    params['experiment_id'] = g
    samples['experiment_id'] = g
    # Isolate the predicted values and make a new dataframe corresponding to x index
    predicted_means = params[params['parameter']=='y_predict']
    predicted_means.sort_values(by='dimension', inplace=True)
    predicted_means = predicted_means[['hpd_min', 'hpd_max', 'mean']]
    predicted_means['time'] = t_predict
    predicted_means['experiment_id'] = g
    estimated_foldchange = params[params['parameter']=='fc']
    estimated_foldchange.sort_values(by='dimension', inplace=True)
    estimated_foldchange= predicted_means[['hpd_min', 'hpd_max', 'mean']]
    estimated_foldchange['param'] = 'fc'
    estimated_foldchange['time'] = d['time_min'].values
    predicted_means = pd.concat([predicted_means, estimated_foldchange])


    # Store the experiment ID linked samples
    _samples.append(samples)
    _params.append(params)
    _means.append(predicted_means)

# Save the sampling info to disk.
samples = pd.concat(_samples, sort=False)
params = pd.concat(_params, sort=False)
predicted_means = pd.concat(_means, sort=False)
samples.to_csv('../../data/preact_gaussian_process_fc_samples.csv', index=False)
params.to_csv('../../data/preact_gaussian_process_fc_summary.csv', index=False)
predicted_means.to_csv('../../data/preact_gaussian_process_fc_prediction.csv', index=False)
