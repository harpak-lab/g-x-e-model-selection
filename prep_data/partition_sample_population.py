import os
import pandas as pd
from shared_utils import ensure_directory_exists

ensure_directory_exists('population_partitions')

qc_dir = os.getenv('QC_DIR')

with open('{}/ukb.filtered.imp.chr9.sample'.format(qc_dir), 'r') as file:
    header_line1 = file.readline().strip()
    header_line2 = file.readline().strip()

column_names = header_line1.split()

sample_df = pd.read_csv('{}/ukb.filtered.imp.chr9.sample'.format(qc_dir), delim_whitespace=True, skiprows=2, header=None, names=column_names)

print(sample_df.head())

sample_df = sample_df.sample(frac=1, random_state=1)

num_samples = len(sample_df)

gwas_samples = sample_df.iloc[:int(0.6 * num_samples)]
samples_to_use_as_performer_input = sample_df.iloc[int(0.6 * num_samples):]

for subset, filename in [(gwas_samples, 'population_partitions/gwas_samples.txt'), (samples_to_use_as_performer_input, 'population_partitions/performer_input_samples.txt')]:
    with open(filename, 'w') as file:
        file.write(header_line1 + '\n')
        file.write(header_line2 + '\n')
    subset.to_csv(filename, sep='\t', mode='a', index=False, header=False)