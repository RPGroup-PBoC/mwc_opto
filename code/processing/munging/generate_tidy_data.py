"""
This script reads in the data provided by Abrar which serves as a cursory 
exploration of the time-dependent background fluoresescence. The data file 
was provided as a two-sheet excel file. This script converts it into a single, 
tidy csv.
"""
#%%
import numpy as np
import pandas as pd

N_sheets = 6
data = []
for i in range(N_sheets):
    ds = pd.read_excel('../../../data/preprocessed_data.xlsx',
                            sheet_name=i)

    # Add experiment identifiers
    ds['experiment_id'] = i + 1
    data.append(ds)

# Rename columns. 
data = pd.concat(data, sort=False)
data.rename(columns={'Relative time': 'time_min',
                      'Activation power desnity (nW^-2)': 'power_density_nW',
                      'Pre activation mCherry Intensity': 'preact_intensity',
                      'Saturation mCherry Intesnity': 'saturation_intensity',
                      'Total mCherry intensity': 'total_intensity'},
                      inplace=True)
# Save to disk
data.to_csv('../../../data/preprocessed_data_tidy.csv', index=False)



# %%
