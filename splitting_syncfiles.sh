#!/bin/bash

# Define input file
input_file="allele-frequ-n10_count1.sync"  # Replace with your actual sync file name

# Define the number of generations and replicates
generations=(0 10 20 40 60)  # List of generations
replicates=(1 2 3 4 5)       # Number of replicates per generation
n_value="n10"                # n value used in naming

# Loop through generations and replicates
for gen in "${generations[@]}"; do
    for rep in "${replicates[@]}"; do
        # Calculate the field number (3 fixed columns + (replicate - 1 + gen*5))
        # This assumes your fields start from gen0/rep1, gen0/rep2, ..., gen10/rep1, etc.
        start_field=$((3 + (rep - 1) + gen / 10 * 5))
        end_field=$((start_field))

        # Construct output file name
        output_file="gen${gen}_rep${rep}_${n_value}.sync"

        # Use awk to extract the desired columns
        awk -v start="$start_field" -v end="$end_field" '{print $1"\t"$2"\t"$3"\t"$start}' "$input_file" > "$output_file"
    done
done

echo "Files have been split successfully."

