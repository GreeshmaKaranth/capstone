import numpy as np
import torch
from torch import nn
from torch import optim
from torch.autograd import Variable
from torch.nn import functional as F
from utils import max_sentence_size
from utils import avg_cross_entropy_loss

# Hyperparams
postag_hn_size = 100
postag_nb_layers = 2
embedding_size = 512
nb_postags = 1


class BiasClassification(nn.Module):
    """ Returns the Part of Speech Tag for each word
        embedding in a given sentence.
    """

    def __init__(self):
        super(BiasClassification, self).__init__()

        self.w = nn.Parameter(torch.randn(postag_nb_layers * 2,
                                          max_sentence_size,
                                          postag_hn_size))
        self.h = nn.Parameter(torch.randn(postag_nb_layers * 2,
                                          max_sentence_size,
                                          postag_hn_size))

        # Bidirectional LSTM
        self.bi_lstm = nn.LSTM(embedding_size,
                               postag_hn_size,
                               postag_nb_layers,
                               bidirectional=True)

        self.fc = nn.Linear(postag_hn_size * 2, nb_postags)

    def forward(self, x):
        # Runs the LSTM for each word-vector in the sentence x
        x = [x]
        x = torch.tensor(x, dtype=torch.float32)
        out, hn = self.bi_lstm(x, (self.h[:, :x.size(1), :],
                                   self.w[:, :x.size(1), :]))

        # Runs a linear classifier on the outputed state vector
        tags = self.fc(out[0])

        return tags