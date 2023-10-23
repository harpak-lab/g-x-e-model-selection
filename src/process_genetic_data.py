#code credit: based off of Måløy et al.'s code
# here: https://github.com/haakom/pay-attention-to-genomic-selection

import torch
import pandas as pd
import allel
import numpy as np
import lmdb
import pyxis as pxt
from torch.utils.data import DataLoader

num_SNPs_to_include = 20000

gwas_results = pd.read_csv('50_raw.gwas.imputed_v3.both_sexes.tsv', sep='\t')

sorted_results = gwas_results.sort_values(by='pval', ascending=True)

top_snps = sorted_results.head(num_SNPs_to_include) #change later and turn into variable****

#convert to DataFrame
genotype_data = allel.vcf_to_dataframe('ukb.filtered.imp.all_chromosomes.vcf', fields='*', alt_number=1)

top_snps[['chromosome', 'position', 'ref', 'alt']] = top_snps['variant'].str.split(':', expand=True)

# merge the two datasets on chromosome and position
filtered_genotype_data = pd.merge(top_snps, genotype_data, left_on=['chromosome', 'position'], right_on=['#CHROM', 'POS']) #are these headers ok*****

# top_snps_file_name = print("top_{}_snps.txt".format(num_SNPs_to_include))

# top_snps['ID'].to_csv(top_snps_file_name, sep='\t', index=False, header=False)

phenotype_data = pd.read_csv('/corral-repl/utexas/Harpak-Lab-GWAS/ageamplification/agegwas/plink_analysis/phenotypefiles/pheno_height.filledna.txt', sep='\t') #should be tab-delimited, right?****
context_data = pd.read_csv('/corral-repl/utexas/Harpak-Lab-GWAS/ageamplification/agegwas/plink_analysis/phenotypefiles/combined.covariates.quartile.1.txt', sep='\t')
# # assume 'SNP_ID' is the column with SNP identifiers in your genotype_data
# # and 'selected_snps.tsv' is the file with the 20,000 SNPs you want to keep.********

# # selected_snps = pd.read_csv(top_snps, sep='\t') #idk if this is right****
# filtered_genotype_data = genotype_data[genotype_data['SNP_ID'].isin(top_snps['SNP_ID'])]

# # randomly sample 400 individual IDs****change

print("POTENTIALLY FILTERED DATA CORRECTLY:")
print(filtered_genotype_data.head())

#LET'S PRETEND THE DATA WAS FILTERED CORRECTLY BY NOW LOL******

sampled_individuals = np.random.choice(filtered_genotype_data['IID'].unique(), 400, replace=False)

# # filter all data to only include the sampled individuals
sampled_genotype_data = filtered_genotype_data[filtered_genotype_data['IID'].isin(sampled_individuals)]
sampled_phenotype_data = phenotype_data[phenotype_data['IID'].isin(sampled_individuals)]
sampled_context_data = context_data[context_data['IID'].isin(sampled_individuals)]

# convert the 'DOB' column to age
year_data_collected = 2023 #double check*****
sampled_context_data['Age'] = year_data_collected - context_data['DOB'].astype(int)
sampled_context_data = sampled_context_data.drop(columns=['DOB'])

#prep data to be stored in a format that we can use TorchDataset on. if this all doesn't work
#then just create your own custom dataset class****
data = {
    'input_genome': sampled_genotype_data.values,
    'target': sampled_phenotype_data.values,
    'contexts': sampled_context_data.values
}

#Save as lmdb -- I pray this works -- look online for a diff solution if this one doesn't work****
env = lmdb.open('prepared_data.lmdb', map_size=1e9)  # Adjust map_size as needed****

with env.begin(write=True) as txn:
    for i in range(len(sampled_genotype_data)):
        # create a dictionary for each sample
        sample_data = {key: value[i] for key, value in data.items()}
        # serialize the data (convert to byte strings)
        serialized_data = pxt.serialize(sample_data)
        # store in the LMDB using the index as the key
        txn.put(str(i).encode(), serialized_data)

env.close()

#test to see if pxt works for this
dataset = pxt.TorchDataset('prepared_data.lmdb')

#test to see if DataLoader works for this
dataloader_test = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4)
for i, batch in enumerate(dataloader_test):
    # print the shape and content of the first batch
    if i == 0:
        for key, value in batch.items():
            print(f"{key} shape: {value.shape}")
            print(f"{key} content: {value}")
        break