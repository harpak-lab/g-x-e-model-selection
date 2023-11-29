import torch
import pandas as pd
import numpy as np
import lmdb
import pyxis.pyxis as pxp
from torch.utils.data import DataLoader
import lmdb
import pickle
import joblib
from sklearn.preprocessing import MinMaxScaler

#debugging
import os
print("current working")
print(os.getcwd())

#make sure you follow instructions in the 
# HEIGHT_create_filtered_vcf_versions_of_genotype_files/follow_these_instructions_to_run_stuff.sh
#in order to filter your genotype files to include the SNPs you want, with the number of people
# you want to train on

#load in data
#should all be tab-delimited, right?***
phenotype_data = pd.read_csv('/stor/work/Harpak/regina_y/pheno_files/pheno_height.filledna.txt', sep='\t')
context_data = pd.read_csv('/stor/work/Harpak/regina_y/wc.covariates.txt', sep='\t')

print("phenotype data columns:")
print(phenotype_data.columns)
print("context data columns:")
print(context_data.columns)
print()

# print("set of IDs in context data part 1:")
# print(set(context_data['FID'].astype(str) + '_' + context_data['IID'].astype(str)))

#filter out all the individuals with invalid phenotype values
phenotype_data = phenotype_data[phenotype_data['height'] > 0]
context_data = context_data[context_data['IID'].isin(phenotype_data['IID'])]

#change the below line if you don't want randomly sampled individuals
#400 individuals were sampled here
sampled_individuals = pd.read_csv('../HEIGHT_create_filtered_vcf_versions_of_genotype_files/random_sample_ids.txt', sep=' ')

print("sampled individuals columns:")
print(sampled_individuals.columns)

#sample the phenotype and context data to only include the individuals we want
sampled_phenotype_data = phenotype_data[phenotype_data['IID'].isin(sampled_individuals['ID_2'])]
sampled_context_data = context_data[context_data['IID'].isin(sampled_individuals['ID_2'])]

# print("set of IDs in sampled_context_data part 2:")
# print(set(sampled_context_data['FID'].astype(str) + '_' + sampled_context_data['IID'].astype(str)))

#convert the vcf to a form that the NN will accept
#this ignores the positions of all the SNPs though?? is this ok??****
vcf_file = '../HEIGHT_create_filtered_vcf_versions_of_genotype_files/vcf_versions_of_files/vcf_version_all_chromosomes_filtered_for_missing_phenotype.vcf'

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

    return np.array(genotypes).transpose(1, 0, 2)

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
genotype_array = parse_and_encode_genotypes(vcf_file)
print("Genotype array shape:", genotype_array.shape)
print("head of genotype array:")
print(genotype_array[:10])

#save the array
#might need to adjust this depending on the size of the array??
np.save('../dataset/genotype_array.npy', genotype_array)

#get the individual IDs in the VCF so we can reorder the phenotype and covariate data
#to match the order of the genotype data
with open(vcf_file, 'r') as file:
    for line in file:
        if line.startswith('#CHROM'):
            vcf_ids = line.strip().split('\t')[9:]
            break
        
print("vcf IDs:")
print(vcf_ids[:10])
#DEBUGGING**************

# def find_missing_values(df, vcf_ids):
#     # Ensure 'FID_IID' is a string to avoid any type comparison issues
#     df['FID_IID'] = df['FID'].astype(str) + '_' + df['IID'].astype(str)

#     # Convert the DataFrame column and vcf_ids to sets
#     set_df_fid_iid = set(df['FID_IID'])
#     set_vcf_ids = set(vcf_ids)

#     # Find the difference
#     missing_values = set_vcf_ids - set_df_fid_iid

#     return missing_values

# # Usage
# missing_values = find_missing_values(sampled_context_data, vcf_ids)
# print(f"The following values are in vcf_ids but not in df['FID_IID']: {missing_values}")

#***********************

# function to reorder dataframes based on VCF IDs
def reorder_df(df, vcf_ids):
    #combine FID and IID into a single column for matching
    df['FID_IID'] = df['FID'].astype(str) + '_' + df['IID'].astype(str)
    #reorder based on VCF IDs and drop the combined column
    df = df.set_index('FID_IID').reindex(vcf_ids).reset_index(drop=True)
    return df

print()
print("sampled phenotype data before reordering:")
print(sampled_phenotype_data.head())

#read and reorder phenotype data
sampled_phenotype_data = reorder_df(sampled_phenotype_data, vcf_ids)

print()
print("sampled phenotype data after reordering:")
print(sampled_phenotype_data.head())

print()
print("sampled context data before reordering:")
print(sampled_context_data.head())

#read and reorder covariates data
sampled_context_data = reorder_df(sampled_context_data, vcf_ids)

print()
print("sampled context data after reordering:")
print(sampled_context_data.head())

# print("set of IDs in sampled_context_data part 3:")
# print(set(sampled_context_data['FID'].astype(str) + '_' + sampled_context_data['IID'].astype(str)))

#save the reordered data
sampled_phenotype_data.to_csv('../dataset/IID_reordered_filtered_phenotype_data_for_height.csv', index=False)
sampled_context_data.to_csv('../dataset/IID_reordered_filtered_covariates_data_for_height.csv', index=False)

#perform a consistency check
#print out any IDs that are missing in either the phenotype or covariates data
print("IDs that are missing in either the phenotype or covariates data:")
missing_in_phenotype = set(vcf_ids) - set(sampled_phenotype_data['FID'].astype(str) + '_' + sampled_phenotype_data['IID'].astype(str))
missing_in_covariates = set(vcf_ids) - set(sampled_context_data['FID'].astype(str) + '_' + sampled_context_data['IID'].astype(str))

# print("set of IDs in phenotype data:")
# print(set(sampled_phenotype_data['FID'].astype(str) + '_' + sampled_phenotype_data['IID'].astype(str)))
# print()
# print("set of IDs in context data:")
# print(set(sampled_context_data['FID'].astype(str) + '_' + sampled_context_data['IID'].astype(str)))
# print()

print("Missing in phenotype data:", missing_in_phenotype)
print("Missing in covariates data:", missing_in_covariates)

#create torch tensors from the phenotype and context dataframes
sampled_phenotype_data = sampled_phenotype_data.drop(columns=['FID', 'IID'])
sampled_context_data = sampled_context_data.drop(columns=['FID', 'IID'])

#normalize the phenotype data *****change the scaler later if you want!!!!
scaler = MinMaxScaler()
scaler.fit(sampled_phenotype_data)
normalized_phenotype_data = pd.DataFrame(scaler.transform(sampled_phenotype_data), columns=sampled_phenotype_data.columns)
joblib.dump(scaler, 'phenotype_scaler.joblib')

phenotype_array = normalized_phenotype_data.to_numpy()
context_array = sampled_context_data.to_numpy()

#prep data to be stored in a format that we can use TorchDataset on. if this all doesn't work
#then just create your own custom dataset class****
data = {
    'input_genome': genotype_array,
    'target': phenotype_array,
    'contexts': context_array
}

print("shape of data dict:")
print("data['input_genome'].shape:", data['input_genome'].shape)
print("data[target].shape:", data['target'].shape)
print("data[contexts].shape:", data['contexts'].shape)

#save as lmdb -- look online for a diff solution if this one doesn't work****
lmdb_path = '../dataset/HEIGHT_genome_phenotype_context_data.lmdb'

lmdb_writer = pxp.Writer(lmdb_path, 100000)
lmdb_writer.put_samples(data)
lmdb_writer.close()