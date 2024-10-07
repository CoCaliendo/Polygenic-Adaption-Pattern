# purpose of this script is to automatically run ocsvm command for all simulated files

import pandas as pd
import numpy as np
from sklearn import preprocessing as pp
from sklearn.svm import OneClassSVM
import sys
import os

# Get the file prefixes from command-line arguments
af0_file = sys.argv[1]
af1_file = sys.argv[2]

# Extract relevant parts for naming outputs
base_name_af0 = os.path.basename(af0_file).replace(".txt", "")
base_name_af1 = os.path.basename(af1_file).replace(".txt", "")

# Read the data from the provided files
af_0 = pd.read_csv(af0_file, sep="\t", header=None, names=['pos', 'af0'])
af_1 = pd.read_csv(af1_file, sep="\t", header=None, names=['pos', 'af1'])

# Drop the first row from both datasets
af_0.drop(index=af_0.index[0], axis=0, inplace=True)
af_1.drop(index=af_1.index[0], axis=0, inplace=True)

# Merge the two datasets on the 'pos' column
merged = pd.merge(af_0, af_1, on=['pos'])

af_m4 = merged.copy()
print("Data read in")
print(af_m4.head(10))

# Standardize the data
sX = pp.StandardScaler(copy=True)
scale = sX.fit_transform(af_m4[['af0', 'af1']])
af_m4scale = pd.DataFrame(scale, columns=['af0', 'af1'])

print(af_m4scale.head(20))
print("Data prepared")

# Parameters for SVM
# Parameters might be changed, due to needings
svm = OneClassSVM(kernel='poly', nu=0.013, gamma=0.05, cache_size=1000)
print("Parameters set")

# Fit the model and predict
svm.fit(af_m4scale)
pred = svm.predict(af_m4scale)
print("Fitting done")

# Scores
scores = svm.score_samples(af_m4scale)

# Convert the scores array to a Pandas DataFrame
scores_df = pd.DataFrame({'Scores': scores})

# Find anomalies and non-anomalies
anom_index = np.where(pred == -1)
noanom_index = np.where(pred == 1)
values_anom = merged.iloc[anom_index]
values_noanom = merged.iloc[noanom_index]

# Save the results to CSV files
output_dir = "/mnt/data01/ccaliend/simulation_pipeline_2024/"
values_anom.to_csv(f'{output_dir}anomalies_{base_name_af0}_vs_{base_name_af1}.csv', header=True)
values_noanom.to_csv(f'{output_dir}noAnomalies_{base_name_af0}_vs_{base_name_af1}.csv', header=True)
scores_df.to_csv(f'{output_dir}scores_ocsvm_{base_name_af0}_vs_{base_name_af1}.csv', header=True)

