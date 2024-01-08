import random
import sys

def sample_snps(input_filename, output_filename, num_snps):
    with open(input_filename, 'r') as file:
        snp_ids = [line.strip() for line in file.readlines()]

    #ensure we're not trying to sample more SNPs than there are available
    num_snps = min(num_snps, len(snp_ids))

    sampled_snps = random.sample(snp_ids, num_snps)

    with open(output_filename, 'w') as file:
        for snp in sampled_snps:
            file.write(snp + '\n')

#check if the number of SNPs to sample is provided as a command-line argument
if len(sys.argv) > 1:
    try:
        num_snps_to_sample = int(sys.argv[1])  # Convert argument to an integer
    except ValueError:
        raise ValueError("The number of SNPs provided is not an integer.")
else:
    #default number of SNPs to sample if not provided
    num_snps_to_sample = 20000

input_file = 'combined_snp_ids.txt'
output_file = 'snps_to_use_as_NN_input.txt'

sample_snps(input_file, output_file, num_snps_to_sample)
