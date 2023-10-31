#!/bin/bash
#SBATCH --job-name=convert_bgen_to_csv
#SBATCH -p vm-small
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mem=8G
#SBATCH -t 1:00:00
#SBATCH --mail-user=reginay3@utexas.edu
#SBATCH --mail-type=begin
#SBATCH --mail-type=end

#required installations: qctool and bgenix******

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

# #make sure you ran the below lines in the command line first -- can't run here!!
# #concurrently (using slurm array) extract the SNP IDs into different files for each chromosome
# # modify_sample_file_to_allow_qctool_use_bgen_files.sh
# # OK I GIVE ON TRYING TO GET SNP IDs FROM BGEN FILES -- WILL GET THEM FROM BFILES INSTEAD:
# for i in {1..22}; do
#     awk '{print $2}' /scratch/09528/haskin/wholecohort_bychr/ukb.filtered.imp.chr${i}.bim > SNP_IDs_each_chromosome/snp_ids_chr_${i}.txt
# done

# #make sure there aren't any duplicate RSIDs across different chromosomes: ********
# cat SNP_IDs_each_chromosome/snp_ids_chr_*.txt | sort | uniq -d > are_there_duplicate_RSIDs.txt

# #combine the SNP IDs into the same file
# cat SNP_IDs_each_chromosome/snp_ids_chr_*.txt > combined_snp_ids.txt

# #sample 20,000 SNPs randomly (replace with top 20,000 SNPs later)
# # and place it in the snps_to_use_as_NN_input.txt file
# python sample_20000_random_SNPs.py

# Everythign that requires qctool here doesdn't work*******lol
# create a .bgen file with the desired SNPs only
# qctool \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr1.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr2.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr3.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr4.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr5.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr6.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr7.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr8.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr9.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr10.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr11.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr12.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr13.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr14.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr15.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr16.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr17.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr18.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr19.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr20.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr21.bgen \
#     -s modified_sample_file.sample \
#     -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr22.bgen \
#     -s modified_sample_file.sample \
#     -incl-rsids snps_to_use_as_NN_input.txt \
#     -og info_for_desired_NN_input_SNPs_only.bgen \
#     -os modified_sample_file_joined.sample \

# qctool \
#     -g info_for_desired_NN_input_SNPs_only.bgen \
#     -s modified_sample_file.sample \
#     -ofiletype dosage \
#     -og genotypes.csv

#generate a file of sample IDs to keep -- we'll randomly select 400 sample IDs
# for now
#creates a file called random_sample_ids.txt
# python generate_sample_IDs_to_keep.py

#we must run these files now (IN ORDER)--but we can't do it here, so do it separately
# ./filter_bgen_files_for_correct_people_and_variants.sh
# ./convert_bgen_files_to_vcf.sh

# merge all of the vcf files
# replace the bgen file names with the names of your bgen files
# vcf-concat vcf_versions_of_files/chr_1.vcf vcf_versions_of_files/chr_2.vcf vcf_versions_of_files/chr_3.vcf vcf_versions_of_files/chr_4.vcf vcf_versions_of_files/chr_5.vcf vcf_versions_of_files/chr_6.vcf vcf_versions_of_files/chr_7.vcf vcf_versions_of_files/chr_8.vcf vcf_versions_of_files/chr_9.vcf vcf_versions_of_files/chr_10.vcf vcf_versions_of_files/chr_11.vcf vcf_versions_of_files/chr_12.vcf vcf_versions_of_files/chr_13.vcf vcf_versions_of_files/chr_14.vcf vcf_versions_of_files/chr_15.vcf vcf_versions_of_files/chr_16.vcf vcf_versions_of_files/chr_17.vcf vcf_versions_of_files/chr_18.vcf vcf_versions_of_files/chr_19.vcf vcf_versions_of_files/chr_20.vcf vcf_versions_of_files/chr_21.vcf vcf_versions_of_files/chr_22.vcf | gzip -c > vcf_versions_of_files/vcf_version_all_chromosomes.vcf.gz

#unzip that file
#gzip -d vcf_versions_of_files/vcf_version_all_chromosomes.vcf.gz

#check the head of the resulting vcf file in VSCode (doesn't show up correctly on command line)
# head -n 20 vcf_versions_of_files/vcf_version_all_chromosomes.vcf.gz vcf_versions_of_files/head_of_vcf_version_all_chromosomes.vcf

#get the individuals who don't have a missing phenotype -- might have to alter this if I'm creating a single performer to predict multiple phenotypes,
#where some phenotypes ahve missing values and some dont!
#can't run here
# retrieve_non_missing_phenotype_individuals.sh

# vcftools --vcf vcf_versions_of_files/vcf_version_all_chromosomes.vcf --keep keep_ids.txt --recode --recode-INFO-all --out vcf_versions_of_files/vcf_version_all_chromosomes_filtered_for_missing_phenotype.vcf
#idk if that flag should be 0v!!!^^^

#modified_sample_file_joined.sample should be the same as modified_sample_file.sample, right?i