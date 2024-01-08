for pheno in "${phenotypes[@]}"; do
  for CHR in {1..22}; do
    head -n 1 ${GWAS_DIR}/${pheno}/gwas_results_chr_${CHR}.${pheno}.glm.linear > header${CHR}.txt

    awk '($7 == "ADD")' ${GWAS_DIR}/${pheno}/gwas_results_chr_${CHR}.${pheno}.glm.linear > temp_file_${CHR}

    cat header${CHR}.txt temp_file_${CHR} > ${GWAS_DIR}/${pheno}/filtered_gwas_results_chr_${CHR}.${pheno}.glm.linear

    rm header${CHR}.txt temp_file_${CHR}

  done

#combine filtered files
cat ${GWAS_DIR}/${pheno}/filtered_gwas_results_chr_{1..22}.${pheno}.glm.linear > ${GWAS_DIR}/${pheno}/filtered_gwas_all_chromosomes.${pheno}.glm.linear

done