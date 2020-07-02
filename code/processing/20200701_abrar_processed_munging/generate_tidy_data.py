"""
This script reads in the data provided by Abrar which serves as a cursory 
exploration of the time-dependent background fluoresescence. The data file 
was provided as a two-sheet excel file. This script converts it into a single, 
tidy csv.
"""
#%%
import numpy as np
import pandas as pd
data_sheet1 = pd.read_excel('../../../data/20200701_abrar_processed_data_untidy.xlsx',
                            sheet_name=0)
data_sheet2 = pd.read_excel('../../../data/20200701_abrar_processed_data_untidy.xlsx',
                            sheet_name=1)

# Add experiment identifiers
data_sheet1['experiment_id'] = 1
data_sheet2['experiment_id'] = 2
data = pd.concat([data_sheet1, data_sheet2], sort=False)

# Rename columns. 
data.rename(columns={'Relative time': 'time_min',
                      'Activation power desnity (nW^-2)': 'power_density_nW',
                      'Pre activation mCherry Intensity': 'preact_intensity',
                      'Saturation mCherry Intesnity': 'saturation_intensity',
                      'Total mCherry intensity': 'total_intensity'},
                      inplace=True)
# Save to disk
data.to_csv('./output/20200701_abrar_processed_data_tidy.csv', index=False)

