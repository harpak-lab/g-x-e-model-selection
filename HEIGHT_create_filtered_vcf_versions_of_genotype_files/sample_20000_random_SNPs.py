import random

def sample_snps(input_filename, output_filename, num_snps):
    with open(input_filename, 'r') as file:
        snp_ids = [line.strip() for line in file.readlines()]

    #ensure we're not trying to sample more SNPs than there are available
    num_snps = min(num_snps, len(snp_ids))

    sampled_snps = random.sample(snp_ids, num_snps)

    with open(output_filename, 'w') as file:
        for snp in sampled_snps:
            file.write(snp + '\n')

input_file = 'combined_snp_ids.txt'
output_file = 'snps_to_use_as_NN_input.txt'

# number of SNPs to sample
num_snps_to_sample = 20000

sample_snps(input_file, output_file, num_snps_to_sample)
