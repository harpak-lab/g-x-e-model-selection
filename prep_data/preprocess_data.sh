#!/bin/bash

#uncomment stuff later 

#STOP EXECUTION WHEN THERE'S AN ERROR
set -e  # exit when any command fails

# will invoke the 'err_trap' function if any command has a non-zero exit status
trap 'err_trap $LINENO' ERR

# function to execute when an error occurs
err_trap() {
    local line=$1
    echo "Error on line $line"
    exit 1
}

#note: I haven't tested the code in its current form bc I'm not sure how to obtain some of the files
#needed for QC.sh -- I also moved a couple of things around, renamed things, etc. -- theoretically
#it should work though, if not try to debug or ask Regina reginay3@gmail.com******

source ../config.sh

#quality control for the UKBB files
./QC.sh

# extract SNP IDs from bfile:
awk '{print $2}' $QC_DIR/ukb_imp_all_v3_11.bim > combined_snp_ids.txt

#sample x SNPs randomly 
#and place it in the snps_to_use_as_NN_input.txt file
if [ "$RANDOMLY_SAMPLE_SNPS" == "true" ]; then
    python sample_random_SNPs.py 100
fi

#partition the sample population into GWAS and NN input
#creates a file called population_partitions/gwas_samples.txt and
#population_partitions/performer_input_samples.txt
python partition_sample_population.py

#perform GWAS for each phenotype
./do_gwas_for_each_phenotype.sh
./create_and_combine_filtered_files.sh

#get the index SNPS
./index_SNPs_each_phenotype/get_index_SNPs_for_a_phenotype.sh

python index_SNPs_each_phenotype/extract_index_SNPs.py

# generate a file of sample IDs to keep -- we'll randomly select this many sample IDs
# to input into the performer
# creates a file called random_sample_ids.txt
python generate_sample_IDs_to_keep.py $NUM_SAMPLES_TO_INPUT_TO_NN

ensure_directory_exists "bgen_files_filtered_by_people_and_variants"
ensure_directory_exists "vcf_versions_of_files"

for pheno in "${phenotypes[@]}"; do

    ensure_directory_exists "bgen_files_filtered_by_people_and_variants/${pheno}"
    ensure_directory_exists "vcf_versions_of_files/${pheno}"

    #delete all pre-existing filtered bgen files from other runs!
    base_dir="bgen_files_filtered_by_people_and_variants/${pheno}"

    #array of file patterns to check and remove
    file_patterns=("chr_*.bgen" "chr_*.bgen.bgi" "chr_*.sample" "concatenated_filtered_bgen_files.bgen" "chr_*.log")

    for pattern in "${file_patterns[@]}"; do
        for file in $base_dir/$pattern; do
            if [ -f "$file" ]; then
                rm "$file"
                echo "Removed $file."s
            else
                echo "File $file does not exist."
            fi
        done
    done

    #filter bgen files
    ./filter_bgen_files_for_correct_people_and_variants.sh "$pheno"

    #note: after this filter, there might be no SNPs from chr 21 or another
    #chromosome, which might cause an error!!! make sure there are no chromosomes
    #with an error that no variants are left; if there is, then make sure that
    #that chr_x.bgen file doesn't exist

    #concatenate the bgen files
    cat-bgen -clobber -g bgen_files_filtered_by_people_and_variants/${pheno}/chr_*.bgen -og bgen_files_filtered_by_people_and_variants/${pheno}/concatenated_filtered_bgen_files.bgen

    #create a sample file for concatenated_filtered_bgen_files.bgen
    directory="bgen_files_filtered_by_people_and_variants/${pheno}"
    pattern="chr_*.sample"

    #output file
    output_file="bgen_files_filtered_by_people_and_variants/${pheno}/sample_file.sample"

    #find the first .sample file
    for file in $directory/$pattern; do
        if [ -f "$file" ]; then
            #copy the contents of the first found file and break the loop
            cp "$file" "$output_file"
            echo "Copied contents of $file to $output_file."
            break
        fi
    done

    #convert the bgen file to vcf file
    BGEN_FILE="bgen_files_filtered_by_people_and_variants/${pheno}/concatenated_filtered_bgen_files.bgen"
    BGEN_SAMPLE="bgen_files_filtered_by_people_and_variants/${pheno}/sample_file.sample" 

    plink2 --memory ${mem} --bgen $BGEN_FILE ref-last --sample $BGEN_SAMPLE --export vcf vcf-dosage=DS --out vcf_versions_of_files/${pheno}/vcf_version_all_chromosomes

done

parallel "python create_lmdb_files_each_phenotype.py {} > output_of_parallel_create_lmdb_files_{}.txt 2> error_for_create_lmdb_files_{}.txt" :::: phenotype_names.txt