import torch
import pandas as pd
import allel
import numpy as np
import lmdb
import pyxis as pxt
from torch.utils.data import DataLoader
import lmdb
import pickle

#make sure you follow instructions in the 
# create_filtered_vcf_versions_of_genotype_files/follow_these_instructions_to_run_stuff.sh
#in order to filter your genotype files to include the SNPs you want, with the number of people
# you want to train on

#load in data
#should all be tab-delimited, right?***
phenotype_data = pd.read_csv('/corral-repl/utexas/Harpak-Lab-GWAS/ageamplification/agegwas/plink_analysis/phenotypefiles/pheno_height.filledna.txt', sep='\t')
context_data = pd.read_csv('/corral-repl/utexas/Harpak-Lab-GWAS/ageamplification/agegwas/plink_analysis/phenotypefiles/combined.covariates.quartile.1.txt', sep='\t')

#filter out all the individuals with invalid phenotype values
phenotype_data = phenotype_data[phenotype_data['height'] > 0]
context_data = context_data[context_data['IID'].isin(phenotype_data['IID'])]

#change the below line if you don't want randomly sampled individuals
#400 individuals were sampled here
sampled_individuals = pd.read_csv('../create_filtered_vcf_versions_of_genotype_files/random_sample_ids.txt', header=2, sep='\t')

#sample the phenotype and context data to only include the individuals we want
sampled_phenotype_data = phenotype_data[phenotype_data['IID'].isin(sampled_individuals['ID_2'])]
sampled_context_data = context_data[context_data['IID'].isin(sampled_individuals['ID_2'])]

# convert the 'DOB' column to age
year_data_collected = 2023 #double check*****
sampled_context_data['Age'] = year_data_collected - context_data['DOB'].astype(int)
sampled_context_data = sampled_context_data.drop(columns=['DOB'])

#convert the vcf to a form that the NN will accept
#this ignores the positions of all the SNPs though?? is this ok??****
vcf_file = '../create_filtered_vcf_versions_of_genotype_files/vcf_versions_of_files/vcf_version_all_chromosomes_filtered_for_missing_phenotype.vcf'

#parse and one-hot encode genotype data
def parse_and_encode_genotypes(vcf_file):
    genotypes = []
    with open(vcf_file, 'r') as file:
        
        #print the head of file
        print("head of vcf file")
        for _ in range(10): 
            print(file.readline().strip())
            
        file.seek(0)
            
        for line in file:
            if not line.startswith('#'): #parse the individuals' genotype data
                fields = line.strip().split('\t')
                genotype_data = fields[9:]  # genotype data starts from the 10th field
                encoded_genotypes = [one_hot_encode(g) for g in genotype_data]
                genotypes.append(encoded_genotypes)

    return torch.tensor(genotypes)

# one-hot encode a single genotype
def one_hot_encode(genotype):
    encoding_map = {
        '0/0': [1, 0, 0, 0],
        '0/1': [0, 1, 0, 0],
        '1/1': [0, 0, 1, 0],
        './.': [0, 0, 0, 1]
    }
    return encoding_map.get(genotype, [0]*4)  # default to all zeros for unknown genotypes

# turn the vcf file to usable genotype info
genotype_tensor = parse_and_encode_genotypes(vcf_file)
print("Genotype tensor shape:", genotype_tensor.shape)

#save the tensor
#might need to adjust this depending on the size of the tensor??
torch.save(genotype_tensor, 'genotype_tensor.pt')

#get the individual IDs in the VCF so we can reorder the phenotype and covariate data
#to match the order of the genotype data
with open(vcf_file, 'r') as file:
    for line in file:
        if line.startswith('#CHROM'):
            vcf_ids = line.strip().split('\t')[9:]
            break

# function to reorder dataframes based on VCF IDs
def reorder_df(df, vcf_ids):
    #combine FID and IID into a single column for matching
    df['FID_IID'] = df['FID'].astype(str) + '_' + df['IID'].astype(str)
    #reorder based on VCF IDs and drop the combined column
    df = df.set_index('FID_IID').reindex(vcf_ids).reset_index(drop=True)
    return df

#read and reorder phenotype data
sampled_phenotype_data = reorder_df(sampled_phenotype_data, vcf_ids)

#read and reorder covariates data
sampled_context_data = reorder_df(sampled_context_data, vcf_ids)

#save the reordered data
sampled_phenotype_data.to_csv('IID_reordered_filtered_phenotype_data_for_height.csv', index=False)
sampled_context_data.to_csv('IID_reordered_filtered_covariates_data_for_height.csv', index=False)

#perform a consistency check
#print out any IDs that are missing in either the phenotype or covariates data
print("IDs that are missing in either the phenotype or covariates data:")
missing_in_phenotype = set(vcf_ids) - set(sampled_phenotype_data['FID'].astype(str) + '_' + sampled_phenotype_data['IID'].astype(str))
missing_in_covariates = set(vcf_ids) - set(sampled_context_data['FID'].astype(str) + '_' + sampled_context_data['IID'].astype(str))

print("Missing in phenotype data:", missing_in_phenotype)
print("Missing in covariates data:", missing_in_covariates)

#create torch tensors from the phenotype and context dataframes
sampled_phenotype_data = sampled_phenotype_data.drop(columns=['FID', 'IID'])
sampled_context_data = sampled_context_data.drop(columns=['FID', 'IID'])

phenotype_tensor = torch.tensor(sampled_phenotype_data.values, dtype=torch.float32)
context_tensor = torch.tensor(sampled_context_data.values, dtype=torch.float32)

#prep data to be stored in a format that we can use TorchDataset on. if this all doesn't work
#then just create your own custom dataset class****
data = {
    'input_genome': genotype_tensor,
    'target': phenotype_tensor,
    'contexts': context_tensor
}

print("shape of data dict:")
print("data['input_genome'].shape:", data['input_genome'].shape)
print("data[target].shape:", data['target'].shape)
print("data[contexts].shape:", data['contexts'].shape)

#save as lmdb -- look online for a diff solution if this one doesn't work****
lmdb_path = 'genome_phenotype_context_data.lmdb'

#create an LMDB environment
env = lmdb.open(lmdb_path, map_size=1e9)  #adjust the map_size according to your data size??

with env.begin(write=True) as txn:
    #iterate over the items in the dictionary and put them in the database
    for key, value in data.items():
        #keys in LMDB should be bytes, values are serialized
        txn.put(key.encode(), pickle.dumps(value))

#close the environment
env.close()
