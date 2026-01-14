from pathlib import Path

from build_pipeline.neural import MLPClassifier, load_inverted_file
import torch
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader, Dataset
from transformers.models.auto.image_processing_auto import model_type

model = None
inverted_file = None
input_data = None
constants = [] #TODO fill these

def initialize_nlsh(_input):
    index_path = Path(constants[0])
    members = constants[1]
    layers = constants[2]
    nodes = constants[3]
    input_dim = 320
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    global model
    global inverted_file
    global input_data
    model = MLPClassifier(d_in=input_dim, n_out=members, layers=layers,
                          nodes=nodes).to(device)
    model.load_state_dict(torch.load(index_path.name + "/model.pt"))
    model.eval()
    inverted_file = load_inverted_file(index_path.name + "/inverted_file.txt")
    bins_check= constants[4]
    input_data = _input


def search_nlsh(q):
    global model
    global inverted_file
    bins_check = constants[4]
    global input_data
    # prediction
    query_tensor = torch.tensor(q, dtype=torch.float32).unsqueeze(0).view(1, -1)
    with torch.no_grad():
        logits = model(query_tensor)
        probs = F.softmax(logits, dim=1)
    # multiprobe
    top_k_probs, top_k_labels = torch.topk(probs, bins_check, 1)
    # candidates
    search_space = []
    print(top_k_labels)
    for label_tensor in top_k_labels[0]:
        label = label_tensor.item()
        for pointID in inverted_file[label]:
            search_space.append(input_data[pointID])
    # exhaustive search
    return search_space