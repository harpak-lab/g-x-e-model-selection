#!/bin/bash
#SBATCH --job-name=extract_all_SNP_IDs
#SBATCH -p vm-small
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mem=8G
#SBATCH -t 1:00:00
#SBATCH --mail-user=reginay3@utexas.edu
#SBATCH --mail-type=begin
#SBATCH --mail-type=end
#SBATCH --array=1-22
#SBATCH --cpus-per-task=4

#file doesn't work*****

CHR=$SLURM_ARRAY_TASK_ID

qctool\
    -g /scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr${CHR}.bgen\
    -s modified_sample_file.sample \
    -osnp SNP_IDs_each_chromosome/snp_ids_chr_${CHR}.txt
