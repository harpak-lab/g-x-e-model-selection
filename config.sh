# config.sh
mem=64000
threads=16

IMPUTE_DIR=     # inputed, filtered bgen files are stored here
export PHENO_DIR=        # phenotype files are stored here
export QC_DIR=         # QC files are stored here

export GWAS_DIR=       # summary statistics files are stored here
export GWAS_SAMPLE_FILE="/scratch/09528/haskin/GWASxML_algo/population_partitions/gwas_samples_filtered.txt" # file containing samples used in GWAS
export COVARIATES_FILE="/scratch/09217/ssmith21/sad_variance/2.covariates/wc.covariates.txt" # file containing covariates used in GWAS
export RANDOMLY_SAMPLE_SNPS="false"

phenotypes=("bmi" "height" "HDL") # phenotypes to use
printf "%s\n" "${phenotypes[@]}" > phenotype_names.txt