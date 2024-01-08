#!/bin/bash

source ../config.sh

pheno=$1

for CHR in {1..22}
do
  BGEN_FILE="${QC_DIR}/ukb.filtered.imp.chr${CHR}.bgen" 
  SAMPLE_FILE="${IMPUTE_DIR}/ukb61666_imp_chr${CHR}_v3_s487280.sample"
  
  if [ "${RANDOMLY_SAMPLE_SNPS}" == "true" ]; then
    SNPS_TO_USE_FILE="snps_to_use_as_NN_input.txt"
  else
    SNPS_TO_USE_FILE="index_SNPs_each_phenotype/intermediate_files_${pheno}/index_snps.txt"
  fi

  plink2 \
    --memory ${mem} \
    --bgen "${BGEN_FILE}" ref-last \
    --sample "${SAMPLE_FILE}" \
    --keep random_sample_ids.txt \
    --extract "${SNPS_TO_USE_FILE}" \
    --export bgen-1.3 \
    --out bgen_files_filtered_by_people_and_variants/${pheno}/chr_$CHR

done

#idk if the bgen-1.3 version is correct but ok*****