import random
import sys
import os

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

with open('population_partitions/performer_input_samples.txt' , 'r') as f:
    lines = f.readlines()

header = lines[:2]
valid_sample_ids = lines[2:]

#check if there are enough samples to select
if num_people_to_randomly_select > len(valid_sample_ids):
    print(f"Number of people to select ({num_people_to_randomly_select}) is greater than the available samples ({len(valid_sample_ids)}).")
    sys.exit(1)

#randomly select samples
random_samples = random.sample(valid_sample_ids, num_people_to_randomly_select)

#write to the output file
with open('random_sample_ids.txt', 'w') as out:
    out.writelines(header + random_samples)