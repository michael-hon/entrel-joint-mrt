
import torch
import torch.nn as nn
from module.CharEmbedding import CharEmbedding


class WordCharEmbedding(nn.Module):
    """
    Generate word embedding inputed into Bi-LSTM :
             concatenate word embedding (look up table) with char embedding (generated by cnn on characters of word)
    """
    def __init__(self, vocab_size, embedding_size, char_embed_kwargs, dropout=0.5,
                 aux_embedding_size=None, padding_idx=0, concat=False):
        super(WordCharEmbedding, self).__init__()
        self.char_embeddings = CharEmbedding(**char_embed_kwargs)
        self.word_embeddings = nn.Embedding(vocab_size, embedding_size, padding_idx=padding_idx)
        self.dropout = nn.Dropout(dropout)
        if concat and aux_embedding_size is not None:
            self.aux_word_embeddings = nn.Embedding(vocab_size, aux_embedding_size)
        self.concat = concat

    def forward(self, X, X_char=None):
        word_vecs = self.word_embeddings(X)
        if X_char is not None:
            batch_size, sent_size, char_size = X_char.size()
            X_char = X_char.view(-1, char_size)
            char_vecs = self.char_embeddings(X_char)
            char_vecs = char_vecs.view(batch_size, sent_size, -1)
            if self.concat:
                embedding_list = [char_vecs, word_vecs]
                if hasattr(self, 'aux_embedding_size'):
                    aux_vecs = self.aux_embedding_size(X)
                    embedding_list.append(aux_vecs)
                word_vecs = torch.cat(embedding_list, 2)
            else:
                word_vecs = char_vecs + word_vecs
        return self.dropout(word_vecs)
