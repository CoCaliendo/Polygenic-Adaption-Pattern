# Purpose of this script is to argparse and automate the AF calling via poolSeq

args <- commandArgs(trailingOnly=TRUE)

# Print the arguments to debug
print("Arguments passed to the script:")
print(args)

sync_file <- args[1]
output_prefix <- args[2]
generations <- as.integer(strsplit(args[3], ",")[[1]])
replicate_count <- as.integer(strsplit(args[4], ",")[[1]]) # Even if this is not used directly
n_value <- args[5]

# Print parsed generations and number of replicates to debug
print("Parsed generations:")
print(generations)
print("Parsed replicate counts:")
print(replicate_count)

# Set the library to use in R
.libPaths("~/R/x86_64-pc-linux-gnu-library/4.3")

# Set the compiler flags to avoid treating warnings as errors
Sys.setenv("CXXFLAGS"="-Wno-format-security")

# Load necessary libraries
library(Rcpp)
library(poolSeq)

# Read sync file with the specified generations and replicates
Pool_Sim <- read.sync(file=sync_file, gen=generations, repl=replicate_count, keepOnlyBiallelic=TRUE)

# Process each generation and all replicates (assuming replicate labels are fixed as '5')
for (gen in generations) {
  for (repl in unique(Pool_Sim@repl)) { # Iterate over all unique replicates present in sync
    print(paste("Processing generation:", gen, "replicate:", repl)) # Debug statement

    # Generate allele frequency data
    af_rot_gen <- af(sync=Pool_Sim, gen=gen, repl=repl)

    # Construct output file name
    output_file <- paste0(output_prefix, "_gen", gen, "_repl", repl, "_n", n_value, ".txt")

    # Write data to file
    write.table(af_rot_gen, file=output_file, sep="\t")
  }
}

