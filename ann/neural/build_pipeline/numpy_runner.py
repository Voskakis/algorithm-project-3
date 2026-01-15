import numpy as np
import torch


def transform_to_numpy_array(blocks):
    y = np.array(blocks, dtype=np.int64)
    y = y - y.min()
    return y

def produce_long_tensor(blocks):
    y = np.array(blocks, dtype=np.int64)
    y = y - y.min()
    torch.from_numpy(y).long()