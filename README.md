# Genomic Selection Detection: Method Comparison

This repository contains a pipeline for comparing different approaches to detect selection in simulated genomic data. The pipeline simulates data using Mimicree2 and analyzes it with machine learning and statistical methods.

## Methods Compared

The pipeline compares five different approaches:

1. **OCSVM**: One-Class Support Vector Machine
2. **NBC**: Naive Bayesian Classifier 
3. **FET**: Fisher's Exact Test
4. **OCSVM-FET**: Combined OCSVM and FET approach
5. **NBC-FET**: Combined NBC and FET approach

## Workflow

1. **Data Simulation**: Generate simulated genomic data with known selection patterns
2. **Data Processing**: Process data for each analytical method
3. **Analysis**: Apply each method to detect selection
4. **Performance Assessment**: Calculate metrics (AUC/ROC, Accuracy, FPR) to evaluate method performance
5. **Visualization**: Plot results for comparison

## Usage

### Data Simulation

Simulate data using Mimicree2:

python3 automate_simulations.py --mimhap haplofile.mimhap --n_values  --f  --effect_file effect-size-file --heritability  --snapshots  --replicate_runs  --selection_regime truncating_05.txt --threads  --generations  --replicates  --num_repeats

### Run OCSVM analysis:
bash run_parallel_ocsvm.sh

### Run NBC analysis:
python3 NBC_mainscript.py

### Run FET analysis:
Rscript FET_mainscript.R input.sync output_prefix "0,10,20,40,60" "1,2,3,4,5" 10


Alternatively, automate the FET analysis:
bash automize_FET.sh

### Calculate performance metrics:
python3 getting_AUC_ACC_FPR_fromOCSVM.py

### Visualization
For result visualization, run the Jupyter notebook:
jupyter notebook plot_script.ipynb


## Requirements

Python 3.6+
R 4.0+
Jupyter Notebook

Required Python packages:
  scikit-learn
  numpy
  pandas
  matplotlib
  seaborn


Required R packages:
  data.table
  ggplot2

## Citation

If you use these scripts or methods in your research, please cite:

doi: https://doi.org/10.1101/2024.11.28.625827 


## Contact

For questions or issues, please open an issue on this repository or contact the repository owner.
