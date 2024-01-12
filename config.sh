# config.sh
mem=64000
threads=16

IMPUTE_DIR=     # inputed, filtered bgen files are stored here
export PHENO_DIR=   # phenotype files are stored here
export QC_DIR=         # QC files are stored here

export GWAS_DIR="gwas_results"      # summary statistics files are stored here
export COVARIATES_FILE=     # file containing covariates used in GWAS
export RANDOMLY_SAMPLE_SNPS="false"
NUM_SAMPLES_TO_INPUT_TO_NN=200000

phenotypes=("bmi" "height" "HDL") # phenotypes to use
printf "%s\n" "${phenotypes[@]}" > phenotype_names.txt

ensure_directory_exists() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
    fi
}
