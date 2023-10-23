#code credit: based off of Måløy et al.'s code
# here: https://github.com/haakom/pay-attention-to-genomic-selection

import torch.nn as nn
import torch
class RMSELoss(nn.Module):
    def __init__(self, eps=1e-6):
        super().__init__()
        self.mse = nn.MSELoss()
        self.eps = eps

    def forward(self,yhat,y):
        loss = torch.sqrt(self.mse(yhat,y) + self.eps)
        return loss