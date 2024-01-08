#!/bin/bash
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

#check if user has provided an argument
if [ $# -eq 0 ]; then
    echo "No directory path where the UK Biobank (UKBB) imputed genotype files are located provided. Usage: $0 dirname"
    exit 1
fi

dirname=$1

#filter the UKBB files
./QC.sh "$dirname"

#include a step here where you are converting the bgen files to bfiles OR extracting the SNP IDs from the bgen files
#directly********

#make sure you ran the below lines in the command line first -- can't run here!!
#concurrently (using slurm array) extract the SNP IDs into different files for each chromosome
# modify_sample_file_to_allow_qctool_use_bgen_files.sh
# OK I GIVE ON TRYING TO GET SNP IDs FROM BGEN FILES -- WILL GET THEM FROM BFILES INSTEAD:
for i in {1..22}; do
    awk '{print $2}' /scratch/09528/haskin/wholecohort_bychr/ukb.filtered.imp.chr${i}.bim > SNP_IDs_each_chromosome/snp_ids_chr_${i}.txt
done

#make sure there aren't any duplicate RSIDs across different chromosomes: ********
cat SNP_IDs_each_chromosome/snp_ids_chr_*.txt | sort | uniq -d > are_there_duplicate_RSIDs.txt

#combine the SNP IDs into the same file
cat SNP_IDs_each_chromosome/snp_ids_chr_*.txt > combined_snp_ids.txt

#sample x SNPs randomly (replace with top 200,000 SNPs later)
# and place it in the snps_to_use_as_NN_input.txt file
python sample_random_SNPs.py 3000

# generate a file of sample IDs to keep -- we'll randomly select this many sample IDs
# for now
# creates a file called random_sample_ids.txt
python generate_sample_IDs_to_keep.py 300

#delete all pre-existing filtered bgen files from other runs!
base_dir="bgen_files_filtered_by_people_and_variants"

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
./filter_bgen_files_for_correct_people_and_variants.sh

#note: after this filter, there might be no SNPs from chr 21 or another
#chromosome, which might cause an error!!! make sure there are no chromosomes
#with an error that no variants are left; if there is, then make sure that
#that chr_x.bgen file doesn't exist!!!!!???

#concatenate the bgen files
cat-bgen -clobber -g bgen_files_filtered_by_people_and_variants/chr_*.bgen -og bgen_files_filtered_by_people_and_variants/concatenated_filtered_bgen_files.bgen

#create a sample file for concatenated_filtered_bgen_files.bgen
directory="bgen_files_filtered_by_people_and_variants"
pattern="chr_*.sample"

#output file
output_file="bgen_files_filtered_by_people_and_variants/sample_file.sample"

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
BGEN_FILE="bgen_files_filtered_by_people_and_variants/concatenated_filtered_bgen_files.bgen"
BGEN_SAMPLE="bgen_files_filtered_by_people_and_variants/sample_file.sample" 

plink2 --bgen $BGEN_FILE ref-last --sample $BGEN_SAMPLE --export vcf vcf-dosage=DS --out vcf_versions_of_files/vcf_version_all_chromosomes

cd ../src

python create_lmdb_files_each_phenotype.py