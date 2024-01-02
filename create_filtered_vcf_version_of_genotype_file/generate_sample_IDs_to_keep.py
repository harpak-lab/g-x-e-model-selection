import random
import sys

# default number of people to select if no argument is provided
default_num_people = 400

# check if a command line argument is provided
if len(sys.argv) > 1:
    try:
        num_people_to_randomly_select = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid integer for the number of people to select.")
        sys.exit(1)
else:
    num_people_to_randomly_select = default_num_people

# read the Withdrawal List (assuming FID and IID are identical)
with open('/stor/work/Harpak/regina_y/GWASxML_algo/withdrawn_from_study_individuals.csv', 'r') as wd_file:
    # skip the header
    next(wd_file)
    # create a set of withdrawn IDs
    withdrawn_ids = {line.split()[1] for line in wd_file}

# filter out withdrawn individuals
with open('/stor/work/Harpak/regina_y/GWASxML_algo/ukb.filtered.imp.chr1.sample', 'r') as f:
    lines = f.readlines()

#extract the header
header = lines[:2]

#filter out withdrawn individuals (assuming the first column is the relevant ID)
filtered_samples = [line for line in lines[2:] if line.split()[0] not in withdrawn_ids]

# Check if there are enough samples to select
if num_people_to_randomly_select > len(filtered_samples):
    print(f"Number of people to select ({num_people_to_randomly_select}) is greater than the available samples ({len(filtered_samples)}).")
    sys.exit(1)

#randomly select samples
random_samples = random.sample(filtered_samples, num_people_to_randomly_select)

#write to the output file
with open('random_sample_ids.txt', 'w') as out:
    out.writelines(header + random_samples)