# purpose of this script is to get comparative metrices like AUC/ROC, Accuary and FPR

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import roc_auc_score, accuracy_score, confusion_matrix

# Function to calculate FPR, AUC, and Accuracy based on true and predicted labels
def calculate_metrics(true_labels, predicted_labels):
    if len(set(true_labels)) < 2:
        fpr = 0.0
        auc = 0.0
        accuracy = accuracy_score(true_labels, predicted_labels)
    else:
        tn, fp, fn, tp = confusion_matrix(true_labels, predicted_labels).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        auc = roc_auc_score(true_labels, predicted_labels)
        accuracy = accuracy_score(true_labels, predicted_labels)

    return fpr, auc, accuracy

# Define sample sizes and the number of replicates
sample_sizes = ['10', '50', '100', '250', '500']
replicates = ['1', '2', '3', '4', '5']

# Placeholder for storing all metrics
all_metrics = []

# Loop through each sample size and each replicate
for n in sample_sizes:
    for count in replicates:
        af_file = f"af_sim_n{n}_count{count}_gen0_repl5_n{n}.txt"
        scores_file = f"scores_ocsvm_af_sim_n{n}_count{count}_gen0_repl5_n{n}_vs_af_sim_n{n}_count{count}_gen10_repl5_n{n}.csv"
        nbc_3_file = f"nbc_simulation_n{n}_count{count}_gen10_cluster3.csv"
        nbc_2_file = f"nbc_simulation_n{n}_count{count}_gen10_cluster2.csv"
        fet_file = f"output_n{n}_count{count}_gen0_vs_gen10_repl5_n{n}_pvalues_bh.txt"
        selected_loci_file = f"selected_loci_forMimicree_n{n}_count{count}.txt"

        # Read in the allele frequencies and selected loci
        af_df = pd.read_csv(af_file, sep='\t', names=['index', 'x'], low_memory=False)
        af_df.drop(index=af_df.index[0], axis=0, inplace=True)

        selected_loci_df = pd.read_csv(selected_loci_file, sep='\t', names=['index', 'pos', 'iw', 'zahl2', 'zahl3'])
        selected_loci_df['index'] = selected_loci_df['index'] + '.' + selected_loci_df['pos'].astype(str)
        selected_loci_df.drop('pos', axis=1, inplace=True)

        #Scores
        scores_df = pd.read_csv(scores_file, sep=',')
        scores_df = scores_df.rename(columns={'Unnamed: 0': 'index', 'Scores':'score'})
        scores_df = pd.merge(af_df, scores_df[['score']], left_index=True, right_index=True, how='left')
        print(scores_df)
        af_df['index'] = af_df['index'].astype(str)
        scores_df['index'] = scores_df['index'].astype(str)

        scores_df_final1 = scores_df.copy()
        print(scores_df_final1)

        # Normalize scores
        scaler = MinMaxScaler()
        scores_df_final1['normalized_score'] = scaler.fit_transform(scores_df_final1['score'].values.reshape(-1, 1)).flatten()
        scores_df_final = scores_df_final1[scores_df_final1['normalized_score'] > 0.60]
        #scores_df_final['score'] = pd.to_numeric(scores_df_final1['score'], errors='coerce')
        print(scores_df_final.columns)

        # NBC
        nbc_df_3 = pd.read_csv(nbc_3_file, sep=',')
        nbc_df_2 = pd.read_csv(nbc_2_file, sep=',')
        nbc_df_3 = nbc_df_3.rename(columns={'pos': 'index'})
        nbc_df_2 = nbc_df_2.rename(columns={'pos': 'index'})
        nbc_df = pd.concat([nbc_df_3, nbc_df_2])

        #FET
        fet_df = pd.read_csv(fet_file, sep='\t', names=['index', 'bh'], low_memory=False)
        fet_df.drop(index=fet_df.index[0], axis=0, inplace=True)
        fet_df['bh'] = pd.to_numeric(fet_df['bh'])
        fet_df_final = fet_df[fet_df['bh'] > 30]

        # OCSVM-FET overlap
        scores_df_final['index'] = scores_df_final['index'].astype(str)
        fet_df_final['index'] = fet_df_final['index'].astype(str)
        scoresFet_df_final = pd.merge(scores_df_final, fet_df_final, on='index')

        # NBC-FET overlap
        nbc_df['index'] = nbc_df['index'].astype(str)
        nbcFet_df_final = pd.merge(nbc_df, fet_df_final, on='index')


        # Ensure 'index' column in fet_df_final is of the same type as in scores_df_final
        fet_df_final['index'] = fet_df_final['index'].astype(str)
        scoresFet_df_final['index'] = scoresFet_df_final['index'].astype(str)
        nbcFet_df_final['index'] = nbcFet_df_final['index'].astype(str)

        af_df['true_label'] = 0
        af_df.loc[af_df['index'].isin(selected_loci_df['index']), 'true_label'] = 1

        af_df['fet_label'] = 0
        af_df.loc[af_df['index'].isin(fet_df_final['index']), 'fet_label'] = 1

        af_df['scores_label'] = 0
        af_df.loc[af_df['index'].isin(scores_df_final['index']), 'scores_label'] = 1

        af_df['scoresFet_label'] = 0
        af_df.loc[af_df['index'].isin(scoresFet_df_final['index']), 'scoresFet_label'] = 1

        af_df['nbc_label'] = 0
        af_df.loc[af_df['index'].isin(nbc_df['index']), 'nbc_label'] = 1

        af_df['nbcFet_label'] = 0
        af_df.loc[af_df['index'].isin(nbcFet_df_final['index']), 'nbcFet_label'] = 1

        fet_fpr, fet_auc, fet_accuracy = calculate_metrics(af_df['true_label'], af_df['fet_label'])
        scores_fpr, scores_auc, scores_accuracy = calculate_metrics(af_df['true_label'], af_df['scores_label'])
        scoresFet_fpr, scoresFet_auc, scoresFet_accuracy = calculate_metrics(af_df['true_label'], af_df['scoresFet_label'])
        nbc_fpr, nbc_auc, nbc_accuracy = calculate_metrics(af_df['true_label'], af_df['nbc_label'])
        nbcFet_fpr, nbcFet_auc, nbcFet_accuracy = calculate_metrics(af_df['true_label'], af_df['nbcFet_label'])

        metrics = {
            'n': n,
            'count': count,
            'fet_fpr': fet_fpr, 'fet_auc': fet_auc, 'fet_accuracy': fet_accuracy,
            'scores_fpr': scores_fpr, 'scores_auc': scores_auc, 'scores_accuracy': scores_accuracy,
            'scoresFet_fpr': scoresFet_fpr, 'scoresFet_auc': scoresFet_auc, 'scoresFet_accuracy': scoresFet_accuracy,
            'nbc_fpr': nbc_fpr, 'nbc_auc': nbc_auc, 'nbc_accuracy': nbc_accuracy,
            'nbcFet_fpr': nbcFet_fpr, 'nbcFet_auc': nbcFet_auc, 'nbcFet_accuracy': nbcFet_accuracy
        }

        all_metrics.append(metrics)

results_df = pd.DataFrame(all_metrics)

print(results_df)

results_df.to_csv('metrices_overview_gen10.csv', sep='\t')

