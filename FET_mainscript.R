# purpose of this skript is using poolSeq to calculate fisher's exakt test on the simulated data sets

#Purpose of this script is to argparse and automate the AF calling via poolSeq and perform chi-square tests

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

# Process each generation and all replicates
for (repl in unique(Pool_Sim@repl)) {
  for (gen in generations) {

    if (gen == 0) next  # Skip gen0 as it is used for comparison

    print(paste("Processing generation:", gen, "replicate:", repl)) # Debug statement

    # Generate allele frequency data for gen0 and the current generation
    af_gen0 <- af(sync=Pool_Sim, gen=0, repl=repl)
    af_genX <- af(sync=Pool_Sim, gen=gen, repl=repl)

    # Generate coverage data for gen0 and the current generation
    coverage_gen0 <- t(coverage(Pool_Sim, repl=repl, gen=0))
    coverage_genX <- t(coverage(Pool_Sim, repl=repl, gen=gen))

    # Calculate allele counts
    A0 <- as.vector(t(af_gen0 * coverage_gen0))
    a0 <- coverage_gen0 - A0
    AX <- as.vector(t(af_genX * coverage_genX))
    aX <- coverage_genX - AX
    # Perform the chi-square test
    p.values <- chi.sq.test(A0=A0, a0=a0, At=AX, at=aX, min.cov=1, min.cnt=1, max.cov=1, log=FALSE)

    # Adjust p-values using Benjamini-Hochberg method
    p.values_bh <- p.adjust(p.values, method="fdr")

    # Convert to -log10(p) for easier interpretation
    p.values_logbh <- -log10(p.values_bh)

    # Construct output file name
    output_file <- paste0(output_prefix, "_gen0_vs_gen", gen, "_repl", repl, "_n", n_value, "_pvalues_bh.txt")

    # Write data to file
    write.table(p.values_logbh, file=output_file, sep="\t", quote=FALSE, col.names=NA)

    print(paste("Chi-square test completed and results saved for generation:", gen, "replicate:", repl))
  }
}

