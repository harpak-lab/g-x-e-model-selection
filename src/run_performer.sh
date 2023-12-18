#not sure if what I put for these paramters are correct, esp the
#database_name, inverse_transform!!!!!!(double check this) and dataset parameter****

#height
python main.py \
        --total_num_trials 3 \
        --database_name ../hyperparameter_search_database.sqlite \
        --datasets_dir /stor/work/Harpak/regina_y/GWASxML_algo/performer_model/dataset/ \
        --dataset genome_height_phenotype_context_data.lmdb \
        --inverse_transform height_phenotype_scaler.joblib \
        --num_hparams_explor 10 \
        --batch_size 50 \
        --gene_length 3000 \
        --gene_size 4 \
        --num_nodes 3 \
        --num_epochs 100 \
        --gpus 0 \

# #BMI
# python main.py \
#         --total_num_trials 3 \
#         --database_name ../hyperparameter_search_database.sqlite \
#         --datasets_dir /stor/work/Harpak/regina_y/GWASxML_algo/performer_model/dataset/ \
#         --dataset genome_bmi_phenotype_context_data.lmdb \
#         --inverse_transform bmi_phenotype_scaler.joblib \
#         --num_hparams_explor 10 \
#         --batch_size 2 \
#         --gene_length 100 \
#         --gene_size 4 \
#         --num_nodes 3 \
#         --num_epochs 10 \
#         --gpus 0 \

# #HDL
# python main.py \
#         --total_num_trials 3 \
#         --database_name ../hyperparameter_search_database.sqlite \
#         --datasets_dir /stor/work/Harpak/regina_y/GWASxML_algo/performer_model/dataset/ \
#         --dataset genome_HDL_phenotype_context_data.lmdb \
#         --inverse_transform HDL_phenotype_scaler.joblib \
#         --num_hparams_explor 10 \
#         --batch_size 2 \
#         --gene_length 100 \
#         --gene_size 4 \
#         --num_nodes 3 \
#         --num_epochs 10 \
#         --gpus 0 \

# #diastolic BP
# python main.py \
#         --total_num_trials 3 \
#         --database_name ../hyperparameter_search_database.sqlite \
#         --datasets_dir /stor/work/Harpak/regina_y/GWASxML_algo/performer_model/dataset/ \
#         --dataset genome_diastolicBP_auto_phenotype_context_data.lmdb \
#         --inverse_transform diastolicBP_auto_phenotype_scaler.joblib \
#         --num_hparams_explor 10 \
#         --batch_size 2 \
#         --gene_length 100 \
#         --gene_size 4 \
#         --num_nodes 3 \
#         --num_epochs 10 \
#         --gpus 0 \
        
#whta happens if I both specify the batch size and say that I want to
#find the optimal number of batches (default)? idk****

#do I need to set the parameters for the gpus? idk****