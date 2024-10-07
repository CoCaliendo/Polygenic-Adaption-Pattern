# prupose of this script is to automize stats_testing.R even a bit more


#!/bin/bash

# Define the arrays for n_values and counts
n_values=(10 50 100 250 500)
counts=(1 2 3 4 5)
generations="0,10,20,40,60"
replicates="5,5,5,5,5"

# Loop over each n_value and count
for n in "${n_values[@]}"; do
  for count in "${counts[@]}"; do
    # Construct the input file name based on n_value and count
    input_file="allele-frequ-n${n}_count${count}.sync"

    # Define the output prefix
    output_prefix="output_n${n}_count${count}"

    # Run the R script with the specified arguments
    Rscript stats_testing.R "$input_file" "$output_prefix" "$generations" "$replicates" "$n"
  done
done

