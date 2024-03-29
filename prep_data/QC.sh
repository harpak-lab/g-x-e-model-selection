#!/bin/bash
#code credit: a near direct copy of Zhu et al.'s code
# here: https://github.com/harpak-lab/amplification_gxsex/blob/main/scripts/QC.sh

# QC for all chromosomes 

# paths
source config.sh
impute_path=$IMPUTE_DIR # ukbb imputed genotype files 
qc_path=$QC_DIR
mfi_ids_path=$QC_DIR    # obtain MFI ids from UKBB https://biobank.ndph.ox.ac.uk/ukb/refer.cgi?id=1967
pheno_path=$PHENO_DIR

for i in {1..22}
do 
	# make bgen
	plink2 --memory $mem --threads $threads --bgen $impute_path/ukb_imp_chr${i}_v3.bgen ref-last --sample $impute_path/ukb61666_imp_chr${i}_v3_s487280.sample \
    --make-bgen --out $qc_path/ukb_imp_chr${i}_v3_1
    #changed from ref-first to ref-last^^****
	
    ### GENOTYPE QC ###
	# # Info score >0.8
	plink2 --memory $mem --threads $threads --bgen $qc_path/ukb_imp_chr${i}_v3_1 --extract $mfi_ids_path/ukb_mfi_chr${i}_v3_IDs.txt \
    --make-bgen --out $qc_path/ukb_imp_chr${i}_v3_2
	 
    # 	# call rate > 0.95 (missingness)
    # plink2 --memory 64000 --threads 16 --bgen ukb_imp_chr${i}_v3_2 --missing 
	plink2 --memory $mem --threads $threads --bgen $qc_path/ukb_imp_chr${i}_v3_2 --geno 0.05 --mind 0.05 --make-bgen --out $qc_path/ukb_imp_chr${i}_v3_3
    # 	Rscript --no-save hist_miss.R $i
    
    # 	# Alternate frequency (MAF) > 0.001 && <0.999
    # plink2 --memory 64000 --threads 16 --bgen ukb_imp_chr${i}_v3_3 --freq --out MAF_check
	plink2 --memory $mem --threads $threads --bgen $qc_path/ukb_imp_chr${i}_v3_3 --maf 0.001 --max-maf 0.999 --make-bgen --out $qc_path/ukb_imp_chr${i}_v3_4
    # 	Rscript --no-save MAF_check.R
    
    # 	# HWE > 1e-10
    #plink2 --memory 64000 --threads 16 --bgen ukb_imp_chr${i}_v3_4 --hardy 
	plink2 --memory $mem --threads $threads --bgen $qc_path/ukb_imp_chr${i}_v3_4 --hwe 1e-10 --make-bgen --out $qc_path/ukb_imp_chr${i}_v3_5
    #awk '{ if ($10 <0.000000001) print $0 }' plink2.hardy>plink2zoomhwe.hardy
    #Rscript --no-save hwe.R $i

	# remove duplicates and keep only snps
	plink2 --memory $mem --threads $threads --bgen $qc_path/ukb_imp_chr${i}_v3_5 --snps-only --rm-dup exclude-all --make-bgen --out $qc_path/ukb_imp_chr${i}_v3_6

    # remove indels and multiallelic snps
    awk -F '\t' 'index($3, ":") !=0 {print $3}' $qc_path/ukb_imp_chr${i}_v3_6.pvar  > $qc_path/indels_chr${i}.txt
    plink2 --bgen $qc_path/ukb_imp_chr${i}_v3_6 --exclude $qc_path/indels_chr${i}.txt --make-bgen --out $qc_path/ukb_imp_chr${i}_v3_7

    ### SAMPLE QC ###
    
    # remove diff sex and sex chromosome aneuploidy samples
    plink2 --bgen $qc_path/ukb_imp_chr${i}_v3_7 --remove $pheno_path/diffsex_ids.txt $pheno_path/sex_aneuploidy_ids.txt --make-bgen --out $qc_path/ukb_imp_chr${i}_v3_8

    # keep white british
    plink2 --bgen $qc_path/ukb_imp_chr${i}_v3_8 --keep $pheno_path/WBids.txt --make-bgen --out $qc_path/ukb_imp_chr${i}_v3_9

    # keep unrelated individuals
    plink2 --bgen $qc_path/ukb_imp_chr${i}_v3_9 --keep $pheno_path/in_pca_ids.txt --make-bgen --out $qc_path/ukb_imp_chr${i}_v3_10

    # remove withdrawn samples
    plink2 --bgen $qc_path/ukb_imp_chr${i}_v3_10 --remove $pheno_path/withdrawn_ids.txt --make-bgen --out $qc_path/ukb.filtered.imp.chr${i}.bgen

    # convert to bfiles (added)
    plink --bgen $qc_path/ukb.filtered.imp.chr${i}.bgen --sample $qc_path/ukb.filtered.imp.chr22.sample --make-bed --out $qc_path/ukb.filtered.imp.chr${i}
done

# create list of sample IIDs 
tail -n +2 $qc_path/ukb.filtered.imp.chr22.sample | cut -f1 > $pheno_path/QC_ids.txt

# merge all into one
plink2 --memory $mem --threads $threads --pmerge-list $qc_path/merge_list.txt bgen --make-bed --out $qc_path/ukb_imp_all_v3_11