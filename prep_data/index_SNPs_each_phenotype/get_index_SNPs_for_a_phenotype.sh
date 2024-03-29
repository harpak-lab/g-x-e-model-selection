#!/bin/bash
#CHANGE THE CLUMPING GWAS LOCATION TO BE THE ONE WITH THE OMITTED ALLELES*****
#also added the --keep flag

source ../../config.sh

for pheno in "${phenotypes[@]}"; do
    ensure_directory_exists "intermediate_files_${pheno}"
    
    for CHR in {1..22}; do
        plink1.9 \
            --memory ${mem} \
            --bfile $QC_DIR/ukb.filtered.imp.chr${CHR} \
            --keep population_partitions/gwas_samples.txt \
            --clump-p1 10e-8 \
            --clump-r2 0.1 \
            --clump-kb 250 \
            --clump ${GWAS_DIR}/${pheno}/filtered_gwas_results_chr_${CHR}.${pheno}.glm.linear \
            --clump-snp-field ID \
            --clump-field P \
            --out intermediate_files_${pheno}/SNPs_${CHR}_clumped \
            --pheno $PHENO_DIR/pheno_${pheno}.filledna.txt

        awk 'NR!=1{print $3}' intermediate_files_${pheno}/SNPs_${CHR}_clumped.clumped >  intermediate_files_${pheno}/SNPs_clumped_${CHR}.valid.snp
    done
done