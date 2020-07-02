#%%
import numpy as np
import pandas as pd
import light.bayes
import light.stats
force = False

# Load the data set. 
data = pd.read_csv('../processing/20200701_abrar_processed_munging/output/20200701_abrar_processed_data_tidy.csv')
exp1 = data[data['experiment_id']==1]

# Load the stan model.
model = light.bayes.StanModel('../stan/preact_gaussian_process.stan', force_compile=force)

# Define the time range over which to predict. 
N_predict = 50 
N_exp = len(exp1)
t_predict = np.linspace(0, 150, N_predict)

# Set up the data dictionary 
data_dict = {'N': N_exp, 'N_predict': N_predict, 
            'x': exp1['time_min'], 'x_predict':t_predict, 'y':exp1['preact_intensity']}
            
# Sample the model. 
fit, samples = model.sample(data_dict, iter=5000)
params = model.summarize_parameters()
params['experiment_id'] = 1
samples['experiment_id'] = 1
# Isolate the predicted values and make a new dataframe corresponding to x index
predicted_means = params[params['parameter']=='y_predict']
predicted_means.sort_values(by='dimension', inplace=True)
predicted_means = predicted_means[['hpd_min', 'hpd_max', 'mean']]
predicted_means['time'] = t_predict

# Save the sampling info to disk.
samples.to_csv('../../data/preact_gaussian_process_samples.csv', index=False)
params.to_csv('../../data/preact_gaussian_process_summary.csv', index=False)
predicted_means.to_csv('../../data/preact_gaussian_process_prediction.csv', index=False)
