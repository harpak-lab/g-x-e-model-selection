import math
import pandas as pd
import numpy as np
import pyxis.pyxis as pxp
import joblib
from sklearn.preprocessing import MinMaxScaler
from shared_utils import ensure_directory_exists
import sys

#debugging
import os
print("current working")
print(os.getcwd())

#load in data
# phenotypes = ["height", "bmi", "diastolicBP_auto", "HDL"]
if len(sys.argv) > 1:
    pheno_name = sys.argv[1]
    print("The pheno_name passed in is".format(pheno_name))
else:
    print("No argument was passed. Exiting")
    exit()
    
covariates_file = os.getenv('COVARIATES_FILE')
pheno_dir = os.getenv('PHENO_DIR')

print("pheno_name:", pheno_name)
phenotype_data = pd.read_csv(pheno_dir + '/pheno_' + pheno_name + '.filledna.txt', sep='\t')
context_data = pd.read_csv(covariates_file, sep='\t')

print("phenotype data columns:")
print(phenotype_data.columns)
print("context data columns:")
print(context_data.columns)
print()

sampled_individuals = pd.read_csv('random_sample_ids.txt', sep=' ')

print("sampled individuals columns:")
print(sampled_individuals.columns)

#sample the phenotype and context data to only include the individuals we want
sampled_phenotype_data = phenotype_data[phenotype_data['IID'].isin(sampled_individuals['ID_2'])]
sampled_context_data = context_data[context_data['IID'].isin(sampled_individuals['ID_2'])]
        
#convert the vcf to a form that the NN will accept
#this ignores the positions of all the SNPs though?? is this ok??****
vcf_file = 'vcf_versions_of_files/{}/vcf_version_all_chromosomes.vcf'.format(pheno_name)

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

#get the individual IDs in the VCF so we can reorder the phenotype and covariate data
#to match the order of the genotype data
with open(vcf_file, 'r') as file:
    for line in file:
        if line.startswith('#CHROM'):
            vcf_ids = line.strip().split('\t')[9:]
            break
        
print("vcf IDs:")
print(vcf_ids[:10])

# function to reorder dataframes based on VCF IDs
def reorder_df(df, vcf_ids):
    #combine FID and IID into a single column for matching
    df['FID_IID'] = df['FID'].astype(str) + '_' + df['IID'].astype(str)
    #reorder based on VCF IDs and drop the combined column
    df = df.set_index('FID_IID').reindex(vcf_ids).reset_index(drop=True)
    return df

print()
print("sampled phenotype data before reordering:")
print(sampled_phenotype_data)

#read and reorder phenotype data
sampled_phenotype_data = reorder_df(sampled_phenotype_data, vcf_ids)

print()
print("sampled context data before reordering:")
print(sampled_context_data)

#read and reorder covariates data
sampled_context_data = reorder_df(sampled_context_data, vcf_ids)

#perform a consistency check
#print out any IDs that are missing in either the phenotype or covariates data
print("IDs that are missing in either the phenotype or covariates data:")
missing_in_phenotype = set(vcf_ids) - set(sampled_phenotype_data['FID'].astype(str) + '_' + sampled_phenotype_data['IID'].astype(str))
missing_in_covariates = set(vcf_ids) - set(sampled_context_data['FID'].astype(str) + '_' + sampled_context_data['IID'].astype(str))

print("Missing in phenotype data:", missing_in_phenotype)
print("Missing in covariates data:", missing_in_covariates)

#filter out all the individuals with invalid phenotype values
sampled_phenotype_data = sampled_phenotype_data.dropna(subset=[pheno_name])
sampled_phenotype_data['FID'] = sampled_phenotype_data['FID'].astype(int)
sampled_phenotype_data['IID'] = sampled_phenotype_data['IID'].astype(int)
sampled_phenotype_data[pheno_name] = sampled_phenotype_data[pheno_name].astype(float) #maybe change later
sampled_phenotype_data = sampled_phenotype_data[sampled_phenotype_data[pheno_name] > 0] #maybe change if you add other phenotypes********
sampled_context_data = sampled_context_data[sampled_context_data['IID'].isin(sampled_phenotype_data['IID'])]
valid_indices = sampled_phenotype_data.index
genotype_array = genotype_array[valid_indices]
#do i need to drop the invalid values/convert the IID to int from the context data too?? i don't think so

print()
print("sampled phenotype data after reordering and filtering:")
print(sampled_phenotype_data)

print()
print("sampled context data after reordering and filtering:")
print(sampled_context_data)

print("Genotype array shape:", genotype_array.shape)
print("head of genotype array after reordering and filtering:")
print(genotype_array[:10])

ensure_directory_exists('../dataset')

#save the reordered data
sampled_phenotype_data.to_csv('../dataset/IID_reordered_filtered_phenotype_data_for_{}.csv'.format(pheno_name), index=False)
sampled_context_data.to_csv('../dataset/IID_reordered_filtered_covariates_data_for_{}.csv'.format(pheno_name), index=False)
np.save('../dataset/{}_invalid_vals_dropped_genotype_array.npy'.format(pheno_name), genotype_array)

#create torch tensors from the phenotype and context dataframes
sampled_phenotype_data = sampled_phenotype_data.drop(columns=['FID', 'IID'])
sampled_context_data = sampled_context_data.drop(columns=['FID', 'IID'])

#normalize the phenotype data *****change the scaler later if you want!!!!
scaler = MinMaxScaler()
scaler.fit(sampled_phenotype_data)
normalized_phenotype_data = pd.DataFrame(scaler.transform(sampled_phenotype_data), columns=sampled_phenotype_data.columns)
joblib.dump(scaler, '{}_phenotype_scaler.joblib'.format(pheno_name))

phenotype_array = normalized_phenotype_data.to_numpy()
context_array = sampled_context_data.to_numpy()

#prep data to be stored in a format that we can use TorchDataset on. if this all doesn't work
#then just create your own custom dataset class****
data = {
    'input_genome': genotype_array,
    'target': phenotype_array,
    'contexts': context_array
}

#delete later
std_dev = np.std(phenotype_array)
print("********")
print("Standard Deviation of {} data: {}".format(pheno_name, std_dev))

print("shape of data dict:")
print("data['input_genome'].shape:", data['input_genome'].shape)
print("data[target].shape:", data['target'].shape)
print("data[contexts].shape:", data['contexts'].shape)

#save as lmdb
lmdb_path = '../dataset/genome_{}_phenotype_context_data.lmdb'.format(pheno_name)

total_size_in_bytes = (data['input_genome'].nbytes + 
                    data['target'].nbytes + 
                    data['contexts'].nbytes)

buffer_percentage = 0.10  #or 0.20 for a 20% buffer
total_size_with_buffer = total_size_in_bytes * (1 + buffer_percentage)

print("total size with buffer:", total_size_with_buffer)

lmdb_writer = pxp.Writer(lmdb_path, int(math.ceil(total_size_with_buffer))) #increase size later if needed*****
lmdb_writer.put_samples(data)
lmdb_writer.close()