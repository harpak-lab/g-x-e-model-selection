#code credit: based off of Måløy et al.'s code
# here: https://github.com/haakom/pay-attention-to-genomic-selection

import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange, repeat
from torch.autograd import Variable

from transformer_performer_layers import (TransformerPerformerDecoderLayer,
                                          TransformerPerformerEncoderLayer)


class FixedPositionalEmbedding(nn.Module):

    def __init__(self, dim, max_seq_len):
        super().__init__()

        inv_freq = 1. / (10000**(torch.arange(0, dim, 2).float() / dim))
        position = torch.arange(0, max_seq_len, dtype=torch.float)
        sinusoid_inp = torch.einsum("i,j->ij", position, inv_freq)
        emb = torch.cat((sinusoid_inp.sin(), sinusoid_inp.cos()), dim=-1)
        self.register_buffer('emb', emb)

    def forward(self, x):
        return self.emb[None, :x.shape[1], :].to(x.device)

class MultimodalPerformer(nn.Module):

    def __init__(
        self,
        XE,
        dropout,
        input_dropout,
        input_dropout_rate,
        frozen_trial,
        batch_size,
        nystrom_attention,
        n_performer_layers,
        separate_embedding,
        gene_dimension,
        gene_length,
        context_length, #added
    ):
        self.XE = XE
        if self.XE:
            out = 7
        else:
            out = 1
        self.DIMENSION = gene_dimension
        super(MultimodalPerformer, self).__init__()
        self.n_performer_layers = n_performer_layers
        self.nystrom_attention = nystrom_attention
        self.normalization = 1
        self.frozen_trial = frozen_trial
        self.separate_embedding = separate_embedding

        self.input_dropout = input_dropout
        self.input_dropout_rate = input_dropout_rate

        # Identity function
        self.to_cls_token = nn.Identity()

        self.wt_upsample_size = self.DIMENSION

        if self.separate_embedding:
            print("Using separate embeddings")
            self.g_pos_embedding = nn.Parameter(
                torch.randn(1, gene_length + 1, self.DIMENSION)) #why aren't we using fixed positional embedding for gene data??****
            self.c_pos_embedding = FixedPositionalEmbedding(
                self.DIMENSION, context_length) #last parameter here was originally 200 for some reason? changed it to context_length***
        else:
            self.pos_embedding = nn.Parameter(
                torch.randn(1, gene_length + context_length + 1,
                            self.DIMENSION)) #why aren't we using FixedPositionalEmbedding method here??****

        # Linear upsampling layers
        self.upsample_z = nn.Linear(1, self.DIMENSION, bias=False) #idk why the first parameter was set to 2 before but I changed it******

        # Create cls_token
        self.cls_token = nn.Parameter(torch.randn(1, 1, self.DIMENSION))

        # Set dropout rate
        self.dropout_rate = dropout

        self.performer_head_dims = int(
            frozen_trial.suggest_categorical("gene_performer_head_dims",
                                             [2, 4, 8]))

        self.n_performer_heads = int(
            frozen_trial.suggest_categorical("n_gene_performer_heads",
                                             [4, 8, 16]))

        self.performer_ff_size = int(
            frozen_trial.suggest_categorical("n_gene_performer_ff_size",
                                             [32, 64, 128]))

        # Nystrom attention does not use kernels to approximate functions. No need to search through them.
        if self.nystrom_attention:
            self.generalized_attention = 0
            self.n_performer_landmarks = int(
                frozen_trial.suggest_categorical("n_gene_performer_landmarks",
                                                 [32, 64, 128, 256, 512]))
        else:
            self.generalized_attention = frozen_trial.suggest_int(
                "generalized_attention", 0, 1)
            self.n_performer_landmarks = 0

        self.performer = torch.nn.TransformerEncoder(
            TransformerPerformerEncoderLayer(
                d_model=self.DIMENSION,
                nystrom_attention=self.nystrom_attention,
                nhead=self.n_performer_heads,
                dim_feedforward=self.performer_ff_size,
                dim_head=self.performer_head_dims,
                dropout=self.dropout_rate,
                activation='gelu',
                nb_features=
                300,  #Since we are combining both context (changed from weather) and gene data, we should strive for perfect attention
                generalized_attention=self.generalized_attention,
                n_landmarks=self.n_performer_landmarks),
            num_layers=self.n_performer_layers,
            norm=torch.nn.LayerNorm(self.DIMENSION))

        # Dropouts
        self.d1 = nn.Dropout(self.dropout_rate)

        # If we are doing data augmentation through dropout at input
        if self.input_dropout:
            self.dropout_in_gene = nn.Dropout(self.input_dropout_rate)
            self.dropout_in_context = nn.Dropout(self.input_dropout_rate)

        # Layer Norm
        self.norm = nn.LayerNorm(self.DIMENSION)

        # Prediction Layer
        self.predictor = nn.Linear(self.DIMENSION, out)

    def get_optuna_params(self):
        return {
            'n_performer_heads': self.n_performer_heads,
            'performer_head_dim': self.performer_head_dims,
            'performer_ff_size': self.performer_ff_size,
            'performer_generalized_attention': self.generalized_attention,
        }

    def performer_forward(self, x, z):
        # Run through the performer

        if self.separate_embedding:
            b, n, _ = x.shape
            cls_tokens = repeat(self.cls_token, "() n d -> b n d", b=b)
            x = torch.cat((cls_tokens, x), dim=1)
            x += self.g_pos_embedding[:, :(n + 1)]
            z += self.c_pos_embedding(z)
            # Add cls token

        # Concatenate context to gene
        x = torch.cat((x, z), 1)

        if not self.separate_embedding:
            b, n, _ = x.shape
            cls_tokens = repeat(self.cls_token, "() n d -> b n d", b=b)
            x = torch.cat((cls_tokens, x), dim=1)
            # Add positional embedding
            x += self.pos_embedding[:, :(n + 1)]

        # Make input fit with pytorch performers
        x = x.permute(1, 0, 2)

        # Make output of performer fit with traditional expectations
        x = self.performer(x).permute(1, 0, 2)

        # Extract cls token
        x = self.to_cls_token(x[:, 0])

        return x

    def forward(self, batch):
        btch = batch[0]

        # Fetch gene
        x = btch["input_genome"]

        # Do dropout at input if we're doing augmentation
        if self.input_dropout:
            x = self.dropout_in_gene(x)
        
        z = btch["contexts"].unsqueeze(dim=1).float()

        # Do dropout at input if we're doing augmentation
        if self.input_dropout:
            z = self.dropout_in_context(z)

        # Permute tensor to fit our model
        z = z.permute(0, 2, 1)

        # Upsample to correct size
        z = self.upsample_z(z)

        # Encode that the two weather tensors are a different type of data
        z = z + 1

        # Run through performer
        x = self.performer_forward(x, z)

        # Predict
        x = self.predictor(self.d1(self.norm(x)))
        return torch.sigmoid(x)