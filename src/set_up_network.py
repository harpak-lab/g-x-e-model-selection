#code credit: based off of Måløy et al.'s code
# here: https://github.com/haakom/pay-attention-to-genomic-selection

import torch.nn as nn
from optuna.importance import FanovaImportanceEvaluator, get_param_importances

from transformer_network import MultimodalPerformer


def suggest_network(suggester_trial, hparams, network_type: int,
                    batch_size: int, optimizer: str, learning_rate: float,
                    momentum: float, weight_decay: float):
    """
    Creates and returns a network to be optimized
    """
    optuna_dropout_rate = suggester_trial.suggest_uniform(
        "dropout_rate", 0.1, 0.9)

    network_name = ''
    if hparams['separate_embedding']:
        network_name += 'separate_embedding_'
    network_name += 'MultimodalPerformer'
    optuna_n_performer_layers = suggester_trial.suggest_int(
        'n_performer_layers', 1, 4)

    model = MultimodalPerformer(
        hparams["cross_entropy"],
        optuna_dropout_rate,
        hparams["dropout_input"],
        hparams["dropout_input_rate"],
        suggester_trial,
        batch_size,
        hparams["nystrom_attention"],
        optuna_n_performer_layers,
        hparams["separate_embedding"],
        hparams["gene_size"],
        hparams["gene_length"], #create hparam for context data?******
    )
    model_hparams = model.get_optuna_params()
    hyperparams = {
        'lr': learning_rate,
        'Sampler': hparams["sampler"],
        'batch_size': batch_size,
        'optimizer': optimizer,
        'momentum': momentum,
        'weight_decay': weight_decay,
        'n_linear_layers': 0.0,
        'n_conv_layers': 0.0,
        'n_performer_layers': optuna_n_performer_layers,
        'n_heads': model_hparams["n_performer_heads"],
        'head_dim': model_hparams["performer_head_dim"],
        'ff_size': model_hparams["performer_ff_size"],
        'gen_attn': model_hparams["performer_generalized_attention"],
        'nystrom_attention': hparams["nystrom_attention"],
        # 'n_weather_performer_layers': 0.0,  #create hparam for context data?******
        # 'weather_data': 1.0
    }

    # Initialize model weights using xavier
    for p in model.parameters():
        if p.dim() > 1:
            nn.init.xavier_uniform_(p)

    return model, hyperparams, network_name