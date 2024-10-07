# purpose of this script is to provide the correct files to the ocsvm python script and open screens for each run
#!/bin/bash

# Path to your Python script
PYTHON_SCRIPT="/mnt/data01/ccaliend/simulation_pipeline_2024/ocsvm_mainScript.py"

# Path to the directory containing your input files
INPUT_DIR="/mnt/data01/ccaliend/simulation_pipeline_2024/"

# Specify the n_value you're targeting (e.g., n10)
N_VALUE="n10"

# Loop over each count (1-5) and compare gen0 with gen10, gen20, gen40, and gen60
for COUNT in 1 2 3 4 5; do
    af0_file="${INPUT_DIR}af_sim_${N_VALUE}_count${COUNT}_gen0_repl5_${N_VALUE}.txt"

    for GEN in 10 20 40 60; do
        af1_file="${INPUT_DIR}af_sim_${N_VALUE}_count${COUNT}_gen${GEN}_repl5_${N_VALUE}.txt"

        if [[ -f "$af0_file" && -f "$af1_file" ]]; then
            # Extract base filename for screen session naming
            BASENAME="${N_VALUE}_count${COUNT}_gen${GEN}"

            # Start a new screen session for each comparison
            screen -dmS "$BASENAME" bash -c "python3 $PYTHON_SCRIPT $af0_file $af1_file; exec bash"

            echo "Started screen session for $BASENAME"
        else
            echo "Missing file(s) for count ${COUNT} and generation ${GEN}, skipping..."
        fi
    done
done

echo "All screen sessions started."

