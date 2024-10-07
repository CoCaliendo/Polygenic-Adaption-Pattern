# purpose of this script is to automatically take in the af files and generate the NBC algo

import pandas as pd
import numpy as np
from numpy import random
from scipy.stats import multivariate_normal

# Set the parameters for multi-distribution- SET AS NEEDED
# Define the parameters for the first distribution
Sigma1 = np.array([[0.25, 0.18], [0.18, 0.25]])
mu1 = np.array([0., 0.])

# Define the parameters for the second distribution
Sigma2 = np.array([[0.2, 0.199], [0.199, 0.2]])
mu2 = np.array([0.2, 0.7])

# Define the parameters for the third distribution
Sigma3 = np.array([[0.2, 0.199], [0.199, 0.2]])
mu3 = np.array([0.7, 0.2])

# Rotation angle in radians (8.5 degrees to the right)
theta3 = np.radians(-8.5)
theta2 = np.radians(8.5)

# Rotation matrices
rotation_matrix3 = np.array([[np.cos(theta3), -np.sin(theta3)], [np.sin(theta3), np.cos(theta3)]])
rotation_matrix2 = np.array([[np.cos(theta2), -np.sin(theta2)], [np.sin(theta2), np.cos(theta2)]])

# Rotate the mean vectors
mu2_rotated = np.dot(rotation_matrix2, mu2)
mu3_rotated = np.dot(rotation_matrix3, mu3)

# Rotate the covariance matrices
Sigma2_rotated = np.dot(np.dot(rotation_matrix2, Sigma2), rotation_matrix2.T)
Sigma3_rotated = np.dot(np.dot(rotation_matrix3, Sigma3), rotation_matrix3.T)

# Calculate the values of the rotated distributions
Z1 = multivariate_normal(mean=mu1, cov=Sigma1)
Z2 = multivariate_normal(mean=mu2_rotated, cov=Sigma2_rotated)
Z3 = multivariate_normal(mean=mu3_rotated, cov=Sigma3_rotated)
print("Parameters set")

# Define the lists of n_values, sets, and generations
n_values = [10, 50, 100, 250, 500]
sets = range(1, 6)
generations = [10, 20, 40, 60]


# Iterate over n_values, sets, and generations
for n_value in n_values:
    for set_num in sets:
        for gen in generations:
            # Read in af_gen0
            af_gen0 = pd.read_csv(f"/mnt/data01/ccaliend/simulation_pipeline_2024/af_sim_n{n_value}_count{set_num}_gen0_repl5_n{n_value}.txt", sep="\t", header=None, names=['pos', 'af0'])

            # Read in af_genX (where X is the generation)
            af_genX = pd.read_csv(f"/mnt/data01/ccaliend/simulation_pipeline_2024/af_sim_n{n_value}_count{set_num}_gen{gen}_repl5_n{n_value}.txt", sep="\t", header=None, names=['pos', 'af1'])

            af_gen0.drop(index=af_gen0.index[0], axis=0, inplace=True)
            af_genX.drop(index=af_genX.index[0], axis=0, inplace=True)

            # Merge the dataframes on the 'index' column
            merged_df = pd.merge(af_gen0, af_genX, on='pos')

            # Rename columns
            merged_df = merged_df.rename(columns={'af0': 'af0', 'af1': f'af{gen}'})

            # Start multi-distributed approach
            af_m4 = merged_df.copy()
            print(f"Data read in for n_value: {n_value}, set: {set_num}, gen: {gen}")
            print(af_m4.head(10))

            # Calculate probability density values for each data point under each distribution
            pdf_values1 = Z1.pdf(af_m4[['af0', f'af{gen}']])
            pdf_values2 = Z2.pdf(af_m4[['af0', f'af{gen}']])
            pdf_values3 = Z3.pdf(af_m4[['af0', f'af{gen}']])

            # Assign each data point to the distribution with the highest probability density
            af_m4['cluster'] = np.argmax(np.column_stack((pdf_values1, pdf_values2, pdf_values3)), axis=1) + 1

            # Separate data points into clusters
            cluster_3_df = af_m4[af_m4['cluster'] == 3]
            cluster_2_df = af_m4[af_m4['cluster'] == 2]

            # Save the output files with appropriate names
            cluster_2_df.to_csv(f'/mnt/data01/ccaliend/simulation_pipeline_2024/nbc_simulation_n{n_value}_count{set_num}_gen{gen}_cluster2.csv', header=True)
            cluster_3_df.to_csv(f'/mnt/data01/ccaliend/simulation_pipeline_2024/nbc_simulation_n{n_value}_count{set_num}_gen{gen}_cluster3.csv', header=True)

            print(f"Output saved for n_value: {n_value}, set: {set_num}, gen: {gen}")

