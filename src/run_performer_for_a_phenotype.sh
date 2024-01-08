source ../config.sh

#adjust the number of trials, hyperparameters, and epochs as needed
#can run using `nohup parallel run_performer_for_a_phenotype.sh ::: "${phenotypes[@]}" &`

pheno=$1

python main.py \
        --total_num_trials 3 \
        --database_name ../hyperparameter_search_database.sqlite \
        --datasets_dir ../dataset/ \
        --dataset genome_${pheno}_phenotype_context_data.lmdb \
        --inverse_transform ../prep_data/${pheno}_phenotype_scaler.joblib \
        --num_hparams_explor 10 \
        --batch_size 50 \
        --gene_length 3000 \
        --gene_size 4 \
        --num_nodes 3 \
        --num_epochs 100 \
        --gpus 0 \