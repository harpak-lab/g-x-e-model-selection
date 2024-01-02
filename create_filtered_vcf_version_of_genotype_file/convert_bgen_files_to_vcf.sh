# for CHR in {1..22};
# do
#     BGEN_FILE="/stor/work/Harpak/regina_y/GWASxML_algo/performer_model/HEIGHT_create_filtered_vcf_versions_of_genotype_files/bgen_files_filtered_by_people_and_variants/chr_$CHR.bgen" 

#     #uncomment if you need to create index files
#     # bgenix -index -g $BGEN_FILE 

#     bgenix -g $BGEN_FILE -vcf > vcf_versions_of_files/chr_${CHR}.vcf
# done
 #this doesn't work so use plink instead:

for CHR in {1..22};
do
    BGEN_FILE="/stor/work/Harpak/regina_y/GWASxML_algo/performer_model/HEIGHT_create_filtered_vcf_versions_of_genotype_files/bgen_files_filtered_by_people_and_variants/chr_$CHR.bgen" 
    BGEN_SAMPLE="/stor/work/Harpak/regina_y/GWASxML_algo/performer_model/HEIGHT_create_filtered_vcf_versions_of_genotype_files/bgen_files_filtered_by_people_and_variants/chr_$CHR.sample" 
    
    plink2 --bgen $BGEN_FILE ref-last--sample $BGEN_SAMPLE --export vcf vcf-dosage=DS --out vcf_versions_of_files/chr_${CHR}
done