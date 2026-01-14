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

def load_BLAST_results(k: int, threshold: float= 0.01):
    data = defaultdict(list)

    with open("blast_results.tsv", "r", encoding="utf-8") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")

            # Skip malformed rows
            if len(cols) < 5:
                continue

            key = cols[0]
            sseqid = cols[1]
            pident = cols[2]

            try:
                evalue = float(cols[3])
                bitscore = float(cols[4])
            except ValueError:
                continue

            if evalue < threshold:
                data[key].append((sseqid, pident, bitscore, evalue))

    # Sort each list by 12th column (descending) and keep top k
    for key in data:
        data[key].sort(key=lambda x: x[2], reverse=True)
        data[key] = data[key][:k]

    return data

def format_output(protein_ID: str, TopN: int, methods: list[str], BLAST_time: float,
                  method_rec: list[float], method_included: list[list[str]],
                  method_results: list[list[str]], method_bid: list[list[float]], method_distance: list[list[float]],
                  method_time: list[int]) -> str:
    header1 = ("Query Protein: {qID}\nN = {TN}\n"
              "-----------------------------------------------------------------------------------\n"
              "Method\t| Time/query (s)\t| QPS\t| Recall@N vs BLAST Top-N\n"
              "-----------------------------------------------------------------------------------\n")
    bodyPiece1 = "{mthd}\t| {tqs}\t| {qps}\t| {RN}\n"
    header2 = ("Method: {mthd}\nRank\t| Neighbor ID\t| L2 Dist\t| BLAST Identity\t| In BLAST Top-N?\t| Bio comment\n"
               "-----------------------------------------------------------------------------------\n")
    bodyPiece2 = "{rank}\t|{nid}\t|{l2d}\t|{Bid}%\t|{inBlast}\t| \n"

    output = header1.format(qID = protein_ID, TN=TopN)
    for method, index in zip(methods, range(len(methods))):
        if (index==0):
            output += bodyPiece1.format(mthd=method, tqs = BLAST_time, qps = 1/BLAST_time, RN="1")
        else:
            output += bodyPiece1.format(mthd=method, tqs=method_time[index-1], qps=1 / method_time[index-1], RN=method_rec[index-1])
    output += "-----------------------------------------------------------------------------------\n\n\n"
    for method, index in zip(methods, range(1, len(methods)+1)):
        output += header2.format(mthd=method)
        for protein, index2 in zip(method_results[index], range(len(method_results[index]))):
            output += bodyPiece2.format(rank=index2+1, nid=protein, l2d= method_distance[index][index2],
                                        Bid= method_bid[index][index2], inBlast = method_included)

        output += "\n\n"

    return output

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

    if (search_input.mode == "all" or search_input.mode == "neural"):
        inverted_file = load_inverted_file(search_input.index_path.name + "/inverted_file.txt")
        input_dim = 128  if search_input.type is EndianType.Sift else 28 * 28
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = MLPClassifier(d_in=input_dim, n_out=search_input.members, layers=search_input.layers, nodes=search_input.nodes).to(device)
        model.load_state_dict(torch.load(search_input.index_path.name + "/model.pt"))
        model.eval()

    #TODO make embeds of the query file, I think

    outputFile = open(search_input.output_file, "a")

    modes = ["BLAST"]
    match search_input.mode:
        case "all":
            modes.append("Euclidean LSH")
            # modes.append("hypercube")
            modes.append("Neural LSH")
            # modes.append("ivf")
        case "lsh":
            modes.append("Euclidean LSH")
        case "neural":
            modes.append("Neural LSH")
        # case "hypercube":
        #     modes.append("Hypercube")
        # case "ivf":
        #     modes.append("IVF")

    #Handle BLAST work
    command = ("makeblastdb -in "
               + search_input.input_data
               +" -dbtype prot -out swissprot_db\nblastp -db swissprot_db -query "
               + search_input.query_file
               +" -outfmt \"6 qseqid sseqid pident evalue bitscore\" -out blast_results.tsv")
    start = time.time()
    subprocess.run(command, shell=True, capture_output=True, text=True)
    end = time.time()
    BLAST_time = (end - start)/len(search_input.query_data)
    BLAST_results = load_BLAST_results(search_input.nearest_neighbors)

    for q, index in zip(search_input.query_data, range(len(search_input.query_data))):
        proteinID = "" #TODO make sure we pass protein ID via the above
        method_results = []
        method_time = []
        method_rec = []
        method_included = []
        method_bid = []
        method_distance = []
        for mode in modes:
            start = time.time()
            if (mode=="BLAST"):
                continue
            elif (mode=="Neural LSH"):
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
                method_results.append(exhaustive_search(search_space, q, search_input.nearest_neighbors))

            elif (mode=="Euclidean LSH"):
                result = subprocess.check_output(
                    #["./lsh", "-d", f"./{build_input.input_file}", "-q", f"./{build_input.input_file}", "-k", f"10",
                    # "-L", f"{build_input.batch_size}", "-N",
                    # f"{build_input.knn_neighbors + 1}", "-o", "output.txt"] TODO configure properly
                )
                method_results.append(result.decode("utf-8")) #TODO actually parse these


            end = time.time()
            method_time.append(end - start)
            temp_blast_results = BLAST_results[proteinID]

            method_rec.append(sum(x not in method_results[-1] for x in temp_blast_results)
                         / len(temp_blast_results))

            included = []
            bid = []
            distance = []
            temp_method_results = []
            for protein in method_results:
                if protein not in temp_blast_results:
                    #TODO calculate bid
                    if (temp_bid < 0.3):
                        bid.append(temp_bid)
                        temp_method_results.append(protein)
                        included.append("No")
                        distance.append(euclidean(target_vector, subject_vector))
                else:
                    #TODO look up bid in BLAST
                    if (temp_bid < 0.3):
                        bid.append(temp_bid)
                        temp_method_results.append(protein)
                        included.append("Yes")
                        distance.append(euclidean(target_vector, subject_vector))

            method_results = temp_method_results
            method_included.append(included)
            method_bid.append(bid)
            method_distance.append(distance)

        # output
        outputBlock = format_output(proteinID, search_input.nearest_neighbors, modes, BLAST_time, method_rec,
                                    method_included, method_results, method_bid, method_distance, method_time)
        outputFile.write(outputBlock)
        print(outputBlock)
    outputFile.close()

if __name__ == "__main__":
    main()