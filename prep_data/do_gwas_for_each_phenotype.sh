source ../config.sh
ensure_directory_exists "${GWAS_DIR}"

for pheno in "${phenotypes[@]}"; do
  ensure_directory_exists "${GWAS_DIR}/${pheno}"
  
  for CHR in {1..22}; do

    BGEN_FILE="${QC_DIR}/ukb.filtered.imp.chr${CHR}.bgen" 
    SAMPLE_FILE="${QC_DIR}/ukb.filtered.imp.chr${CHR}.sample"
    PHENO_FILE="${PHENO_DIR}/pheno_${pheno}.filledna.txt"

    # GWAS analysis
    plink2 \
      --memory ${mem} \
      --bgen ${BGEN_FILE} ref-last \
      --sample ${SAMPLE_FILE} \
      --keep population_partitions/gwas_samples.txt \
      --glm \
      --make-pgen \
      --covar-variance-standardize \
      --remove ${PHENO_FILE}/withdrawn_ids.txt \
      --pheno ${PHENO_FILE} \
      --covar ${COVARIATES_FILE} \
      --covar-name Sex,Age,PC1-PC20 \
      --out ${GWAS_DIR}/${pheno}/gwas_results_chr_${CHR}

  done
done