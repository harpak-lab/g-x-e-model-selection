import random

num_people_to_randomly_select = 400

with open('/scratch/09217/ssmith21/ageamplification/geneticfiles/wholecohort_bychr/ukb.filtered.imp.chr1.sample', 'r') as f:
    lines = f.readlines()

# extract the header
header = lines[:2]

samples = lines[2:]

# randomly select 400 samples
random_samples = random.sample(samples, num_people_to_randomly_select)

# write to the output file
with open('random_sample_ids.txt', 'w') as out:
    out.writelines(header + random_samples)
