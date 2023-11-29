for CHR in {1..22}
do
  BGEN_FILE="/stor/work/Harpak/regina_y/wholecohort_bychr_bgen/ukb.filtered.imp.chr${CHR}.bgen" 
  SAMPLE_FILE="/stor/work/Harpak/regina_y/wholecohort_bychr_bgen/ukb.filtered.imp.chr${CHR}.sample"

  plink2 \
    --bgen $BGEN_FILE ref-last \
    --sample $SAMPLE_FILE \
    --keep random_sample_ids.txt \
    --extract snps_to_use_as_NN_input.txt \
    --export bgen-1.3 \
    --out bgen_files_filtered_by_people_and_variants/chr_$CHR
done

#should this be ref-last??*********
#idk if the bgen-1.3 version is correct but ok*****