import os
from phenotype_names_common_data import phenotypes

def extract_index_snps(input_file_pattern, output_file_pattern, phenotypes, num_chromosomes):
    for phenotype in phenotypes:
        output_file = output_file_pattern.format(phenotype)

        with open(output_file, 'w') as output:
            for chr_num in range(1, num_chromosomes + 1):
                input_file = input_file_pattern.format(phenotype, chr_num)

                if os.path.exists(input_file):
                    with open(input_file, 'r') as file:
                        #skip header line
                        next(file)
                        for line in file:
                            if line.strip():
                                columns = line.split()
                                snp = columns[2]
                                output.write(snp + '\n')

input_file_pattern = 'intermediate_files_{}/SNPs_{}_clumped.clumped'
output_file_pattern = 'intermediate_files_{}/index_snps.txt'

extract_index_snps(input_file_pattern, output_file_pattern, phenotypes, 22)