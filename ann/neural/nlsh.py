import math
from pathlib import Path

from ann.neural.build_pipeline import MLPClassifier, load_inverted_file
import torch
import torch.nn.functional as F
from torch.utils.data import TensorDataset
from ann.neural.build_pipeline import run_kahip, build_graph_items, create_inverted_file

model = MLPClassifier
inverted_file = list
input_data = list
constants = ["./data/lsh.output.txt", 100, 3, 64, 5, 0.03, 1, 10, 128, 0.001]

def euclidean(vector1, vector2):
    total = 0
    for x, y in zip(vector1, vector2):
        total += (x - y) ** 2
    return math.sqrt(total)

def add_better_result_modular(point, q, result_list, N):
    distance = euclidean(point[1], q)
    if len(result_list) < N:
        result_list.append([point, distance])
    elif distance < result_list[0][1]:
        result_list[0] = [point, distance]
    if len(result_list) >= N > 1:
        max_index = max(range(len(result_list)), key=lambda x: result_list[x][1])
        result_list[0], result_list[max_index] = result_list[max_index], result_list[0]
    return result_list


def exhaustive_search_modular(point_set: list[tuple[int, list[int]]], q:list[int], N:int) -> list[tuple[int, list[int]]]:
    result_list = []
    for point in point_set:
        result_list = add_better_result_modular(point, q, result_list, N)
    result_list = sorted(result_list, key=lambda x: x[1])
    return [(result[0][0]) for result in result_list]

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
    input_data = _input


def search_nlsh(q, num):
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
            search_space.append((input_data[pointID], pointID))
    # exhaustive search
    return exhaustive_search_modular(search_space, q, num)


def build_modular_nlsh():
    index_path = Path(constants[0])
    members = constants[1]
    layers = constants[2]
    nodes = constants[3]
    imbalance = constants[5]
    seed = constants[6]
    epochs = constants[7]
    batch_size = constants[8]
    learn_rate = constants[9]
    resultFile = open("lsh.output.txt", 'r')
    result = resultFile.readlines()
    knn = [list(map(int, line.split())) for line in result]
    for i in knn:
        del i[0]
    adj_set, xadj, vwgt, adjcwgt, adjncy = build_graph_items(knn)

    blocks, edgecut = run_kahip(vwgt, xadj, adjcwgt, adjncy, members, imbalance,
                                seed, 2)

    # initialize classifier

    input_dim = 320
    num_classes = members
    model_wrapper = MLPClassifier(d_in=input_dim, n_out=num_classes, layers=layers, nodes=nodes)

    # Train the classifier
    X = torch.tensor(input_data, dtype=torch.float32)
    y = torch.tensor(blocks, dtype=torch.long)

    prepared_dataset = TensorDataset(X, y)

    model_wrapper.train_classifier(dataset=prepared_dataset, output=num_classes, epochs=epochs,
                                   batch_size=batch_size, lr=learn_rate)
    # save model weights
    index_path.mkdir(parents=True, exist_ok=True)
    torch.save(model_wrapper.state_dict(), index_path.name + "/model.pt")
    # save inverted index
    create_inverted_file(blocks, members, index_path.name + "/inverted_file.txt")

