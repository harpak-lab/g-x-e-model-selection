#!/bin/bash
#SBATCH -J run_stuff
#SBATCH -o run_stuff.o%j
#SBATCH -e run_stuff.e%j
#SBATCH -p normal
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mem=8G
#SBATCH -t 5:00:00
#SBATCH --mail-user=reginay3@utexas.edu
#SBATCH --mail-type=begin
#SBATCH --mail-type=end

python process_genetic_data.py