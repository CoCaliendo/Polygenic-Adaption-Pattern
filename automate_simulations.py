# purpose of this script is to automate simulation analysis with Mimicree2

import argparse
import subprocess

# Define paths to the required scripts and files
path_to_pick_snps = "/mnt/data01/ccaliend/chiro_tide/results_catarina_gatk4/pick-SNPs-QTL.py"
path_to_recombination_map = "/mnt/data01/ccaliend/chiro_tide/results_catarina_gatk4/simple-recombination-map.py"
path_to_mimicree_jar = "/mnt/data01/ccaliend/chiro_tide/results_catarina_gatk4/mim2-v206.jar"

def run_pick_snps(mimhap, n, f, effect_file, output_file):
    cmd = f"python {path_to_pick_snps} --mimhap {mimhap} --n {n} --f {f} --effect-file {effect_file} > {output_file}"
    subprocess.run(cmd, shell=True)

def run_recombination_map(mimhap, output_file):
    cmd = f"python {path_to_recombination_map} --mimhap {mimhap} --rr 4 > {output_file}"
    subprocess.run(cmd, shell=True)

def run_awk(input_file, output_file):
    cmd = f"awk 'BEGIN {{ srand() }} {{ print $1, rand() * (4 - 0.1) + 0.1 }}' {input_file} > {output_file} && sed -i '1s/ .*//' {output_file}"
    subprocess.run(cmd, shell=True)

def run_mimicree(haplotypes, recombination_rate, effect_size, heritability, snapshots, replicate_runs, output_sync, selection_regime, threads):
    cmd = f"java -jar {path_to_mimicree_jar} qt --haplotypes-g0 {haplotypes} --recombination-rate {recombination_rate} --effect-size {effect_size} --heritability {heritability} --snapshots {snapshots} --replicate-runs {replicate_runs} --output-sync {output_sync} --selection-regime {selection_regime} --threads {threads}"
    subprocess.run(cmd, shell=True)

def process_sync_with_r(sync_file, output_prefix, generations, replicates, n_value):
    gen_str = ",".join(map(str, generations))
    repl_str = ",".join(map(str, replicates))
    cmd = f"Rscript test8.R {sync_file} {output_prefix} {gen_str} {repl_str} {n_value}"
    subprocess.run(cmd, shell=True)

def main():
    parser = argparse.ArgumentParser(description="Automate mimicree analysis")
    parser.add_argument("--mimhap", required=True, help="Input mimhap file")
    parser.add_argument("--n_values", type=int, nargs='+', required=True, help="List of n values for different scenarios")
    parser.add_argument("--f", type=float, required=True, help="Frequency value for SNP selection")
    parser.add_argument("--effect_file", required=True, help="Effect size file")
    parser.add_argument("--heritability", type=float, required=True, help="Heritability value")
    parser.add_argument("--snapshots", required=True, help="Snapshots for mimicree")
    parser.add_argument("--replicate_runs", type=int, required=True, help="Number of replicate runs")
    parser.add_argument("--selection_regime", required=True, help="Selection regime file")
    parser.add_argument("--threads", type=int, required=True, help="Number of threads")
    parser.add_argument("--generations", type=int, nargs='+', required=True, help="List of generations for R script")
    parser.add_argument("--replicates", type=int, nargs='+', required=True, help="List of replicates for each generation for R script")
    parser.add_argument("--num_repeats", type=int, required=True, help="Number of times to repeat each scenario")

    args = parser.parse_args()

    for n in args.n_values:
        for i in range(args.num_repeats):
            # Create unique file names for each repeat
            snp_output = f"selected_loci_forMimicree_n{n}_count{i+1}.txt"
            recomb_output = f"rr_genotype_output_forMimicree_n{n}_count{i+1}.txt"
            awk_output = f"recomb_forMimicree_n{n}_count{i+1}.txt"
            mimicree_output = f"allele-frequ-n{n}_count{i+1}.sync.gz"
            output_prefix = f"af_sim_n{n}_count{i+1}"

            # Run the necessary commands
            run_pick_snps(args.mimhap, n, args.f, args.effect_file, snp_output)
            run_recombination_map(args.mimhap, recomb_output)
            run_awk(recomb_output, awk_output)
            run_mimicree(args.mimhap, awk_output, snp_output, args.heritability, args.snapshots, args.replicate_runs, mimicree_output, args.selection_regime, args.threads)

            # Decompress the sync file
            subprocess.run(f"gunzip {mimicree_output}", shell=True)

            # Process the sync file with R
            sync_file_unzipped = mimicree_output.replace(".gz", "")
            process_sync_with_r(sync_file_unzipped, output_prefix, args.generations, args.replicates, n)

if __name__ == "__main__":
    main()

