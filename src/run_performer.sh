#not sure if what I put for these paramters are correct, esp the
#database_name, inverse_transform!!!!!!(double check this) and dataset parameter****

python main.py \
        --total_num_trials 3 \
        --database_name ../hyperparamter_search_database \
        --datasets_dir /stor/work/Harpak/regina_y/GWASxML_algo/performer_model/dataset/ \
        --dataset HEIGHT_genome_phenotype_context_data.lmdb \
        --inverse_transform phenotype_scaler.joblib \
        --num_hparams_explor 10 \
        --batch_size 2 \
        --gene_length 100 \
        --gene_size 4 \
        --num_nodes 3 \
        --num_epochs 10 \
        
#whta happens if I both specify the batch size and say that I want to
#find the optimal number of batches (default)? idk****

#do I need to set the parameters for the gpus? idk****