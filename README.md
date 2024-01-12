# Performer Model for Phenotype Prediction
Regina Ye

Instructions for scripts.
# Gene-Environment Interaction Analysis with Performer Neural Networks

This project is an implementation of performer neural networks to analyze Gene-Environment (GxE) interactions and their impact on phenotypic predictions. It's based on the code developed by Måløy et al., available at [https://github.com/haakom/pay-attention-to-genomic-selection](https://github.com/haakom/pay-attention-to-genomic-selection).

## Features

- 10-fold Cross-Validation
- Hyperparameter optimization with Optuna
- Support for SLURM-based cluster optimization
- Customizable settings for dataset handling and model training

## Installation

To install the necessary components for this project, ensure that you have Anaconda installed. To clone the repository and set up the environment:

1. Clone the repository:
git clone https://github.com/harpak-lab/g-x-e-model-selection.git

2. Navigate to the source directory:
cd g-x-e-model-selection/src

3. Create the Anaconda environment from the `environment.yml` file:
conda env create -f environment.yml

After creating the environment, activate it using `conda activate GxE_predict_phenotypes`

You will also need to manually install ([cat-bgen](https://enkre.net/cgi-bin/code/bgen/dir?ci=trunk)), ([plink](https://www.cog-genomics.org/plink/)), and ([plink2](https://www.cog-genomics.org/plink/2.0/)).

## Phenotype files
Phenotype files are obtained from the UK Biobank and renamed pheno_(phenotype code).txt.

## Genotype files
Imputed data for the UK Biobank was downloaded using the ([ukbgene utility](https://biobank.ctsu.ox.ac.uk/crystal/refer.cgi?id=664)) in the Oxford bgen format.

## Context (Environment) files
Context files are obtained from the UK Biobank and renamed wc.covariates.txt

## Data Preprocessing

Before running the main model, it's essential to preprocess your data using the provided script.

### Steps for Data Preprocessing

1. **Locate the Preprocessing Script and Configuration File**: Find `preprocess_data.sh` and `config.sh` in the prep_data directory.

3. **Provide File Paths in the `config.sh` File**: Provide the paths to your data files in the config.sh file. Ensure that your .bgen files have the naming scheme ukb_imp_chr${CHR}_v3.bgen and the .sample
files have the naming scheme ukb61666_imp_chr${CHR}_v3_s487280.sample.

2. **Run the Preprocessing Script**: 

Execute the preprocessing script:

`./preprocess_data.py`

This script may require several hours to finish executing.

## Usage

To run the project:

python main.py <additional flags>

### Key Arguments

- `--hyper_search`: Set to 1 for hyperparameter search.
- `--total_num_trials`: Number of trials for the study.
- `--database_name`: Path to the hyperparameter search database.
- `--datasets_dir`: Directory where datasets are stored.
- `--dataset`: Name of the dataset to use.
- `--inverse_transform`: Path to the inverse transform of the target data.
- `--standardize_genome`: Set to 1 to standardize the genome data.
- `--batch_size`: Batch size for training.
- `--num_epochs`: Number of epochs for training.
- More arguments can be configured in the script.

For example, in the src folder, you can run:

```
python main.py \
        --total_num_trials 3 \
        --database_name ../hyperparameter_search_database.sqlite \
        --datasets_dir ../dataset/ \
        --dataset genome_HDL_phenotype_context_data.lmdb \
        --inverse_transform HDL_phenotype_scaler.joblib \
        --num_hparams_explor 10 \
        --batch_size 50 \
        --gene_length 3000 \
        --gene_size 4 \
        --num_nodes 3 \
        --num_epochs 10 \
        --gpus 0 \
```

## Credits

This project is based on the work of ([Måløy et al.] (https://github.com/haakom/pay-attention-to-genomic-selection)) Please refer to their repository for the original implementation.
Parts of the project use code written by ([Phil Wang] (https://github.com/lucidrains/nystrom-attention)).
Parts of this README and the QC.sh file are taken from ([Zhu et al.'s] (https://github.com/harpak-lab/amplification_gxsex) )work.