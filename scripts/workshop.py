import math
import time
import subprocess

import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader, Dataset
import torch
from build_pipeline.neural import MLPClassifier #TODO port what needs porting
from build_pipeline import load_inverted_file
from enums import EndianType
from my_types import SearchInput

from collections import defaultdict

def load_tsv_to_map(k: int, threshold: float= 0.01):
    data = defaultdict(list)

    with open("blast_results.tsv", "r", encoding="utf-8") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")

            # Skip malformed rows
            if len(cols) < 12:
                continue

            key = cols[0]     # 1st column
            col2 = cols[1]    # 2nd column
            col3 = cols[2]    # 3rd column

            try:
                col11 = float(cols[10])  # 11th column
                col12 = float(cols[11])  # 12th column
            except ValueError:
                continue

            if col11 < threshold:
                data[key].append((col2, col3, col12))

    # Sort each list by 12th column (descending) and keep top k
    for key in data:
        data[key].sort(key=lambda x: x[2], reverse=True)
        data[key] = data[key][:k]

    return data

def format_output(image_id: int, results: list[list[int]], r:int=0) -> str:
    header = "Query: {qID}\n"
    bodyPiece = "Nearest neighbor-{count}: {neighborID}\ndistanceApproximate: {dis}\ndistanceTrue: {disT}\n\n"
    rPiece = "R-near neighbors:\n"

    output = header.format(qID = image_id)
    for result, index in zip(results, range(len(results))):
        output += bodyPiece.format(count=index, neighborID = result[0], dis = result[1], disT=result[2])
    if r!=0:
        output += rPiece
        for result in results:
            if result[1]<r:
                output += str(result[0])
    return output

def format_footer(queryCount: int, N:int, apTime:float, truTime: float, AFcount:int, recNcount:int)->str:
    footer = "Average AF: {avAF}\nRecall@N: {recN}\nQPS: {qps}\ntApproximateAverage: {tAvg}\ntTrueAverage: {tTrueAvg}"
    avAF = AFcount/queryCount
    recN = recNcount/(queryCount*N)
    tAvg = apTime/N
    tTrue = truTime/N
    return footer.format(avAF=avAF, recN=recN, QPS = 1/tAvg, tAvg=tAvg, tTrue=tTrue)

def euclidean(vector1, vector2):
    total = 0
    for x, y in zip(vector1, vector2):
        total += (x - y)**2
    return math.sqrt(total)

def add_better_result(point, q, result_list, N):
    distance = euclidean(point, q)
    if len(result_list) < N:
        result_list.append([point, distance])
    elif distance < result_list[0][1]:
        result_list[0] = [point, distance]
    if len(result_list) >= N > 1:
        max_index = max(range(len(result_list)), key=lambda x: result_list[x][1])
        result_list[0], result_list[max_index] = result_list[max_index], result_list[0]
    return result_list

def exhaustive_search(point_set: list[list[int]], q, N) -> list[list[int]]:
    result_list = []
    for point in point_set:
        result_list = add_better_result(point, q, result_list, N)
    result_list = sorted(result_list, key=lambda x: x[1])
    return result_list

def main():
    search_input = SearchInput.parse_args()
    inverted_file = load_inverted_file(search_input.index_path.name + "/inverted_file.txt")

    input_dim = 128  if search_input.type is EndianType.Sift else 28 * 28
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MLPClassifier(d_in=input_dim, n_out=search_input.members, layers=search_input.layers, nodes=search_input.nodes).to(device)
    model.load_state_dict(torch.load(search_input.index_path.name + "/model.pt"))
    model.eval()

    outputFile = open(search_input.output_file, "a")
    outputFile.write("Neural LSH\n")

    modes = ["BLAST"] #TODO load all modes here by name as string, if ALL then fill manually

    #Handle BLAST work
    command = ("makeblastdb -in "
               + search_input.input_data
               +" -dbtype prot -out swissprot_db\nblastp -db swissprot_db -query "
               + search_input.query_file
               +" -outfmt 6 -out blast_results.tsv")
    start = time.time()
    subprocess.run(command, shell=True, capture_output=True, text=True)
    end = time.time()
    BLAST_time = (end - start)/len(search_input.query_data)
    BLAST_results = load_tsv_to_map(search_input.nearest_neighbors)

    for q, index in zip(search_input.query_data, range(len(search_input.query_data))):
        method_results = []
        method_time = []
        for mode in modes:
            start = time.time()
            if (mode=="BLAST"):
                continue
            elif (mode=="neural"):
                # prediction
                query_tensor = torch.tensor(q, dtype=torch.float32).unsqueeze(0).view(1, -1)
                with torch.no_grad():
                    logits = model(query_tensor)
                    probs = F.softmax(logits, dim=1)
                # multiprobe
                top_k_probs, top_k_labels = torch.topk(probs, search_input.bins_check, 1)
                # candidates
                search_space = []
                print(top_k_labels)
                for label_tensor in top_k_labels[0]:
                    label = label_tensor.item()
                    for pointID in inverted_file[label]:
                        search_space.append(search_input.input_data[pointID])
                # exhaustive search
                results = exhaustive_search(search_space, q, search_input.nearest_neighbors)

            elif (mode=="lsh"):
                result = subprocess.check_output(
                    #["./lsh", "-d", f"./{build_input.input_file}", "-q", f"./{build_input.input_file}", "-k", f"10",
                    # "-L", f"{build_input.batch_size}", "-N",
                    # f"{build_input.knn_neighbors + 1}", "-o", "output.txt"] TODO configure properly
                )


            end = time.time()
            method_time.append(end - start)

        # output
        recNcount = sum(x not in method_results[-1] for x in method_results[0])/len(method_results[0])

        #TODO overhaul output
        outputFile.write(format_output(index, [r1 +r2[1:] for r1, r2 in zip(results, BLAST_results["queryName"])],search_input.search_radius))
        outputFile.write(format_footer(len(search_input.query_file), search_input.nearest_neighbors, totalAproximateTime, totalExhaustTime, AFcount, recNcount))
    outputFile.close()

if __name__ == "__main__":
    main()