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

    totalAproximateTime = 0
    totalExhaustTime = 0
    AFcount = 0
    recNcount = 0

    outputFile = open(search_input.output_file, "a")
    outputFile.write("Neural LSH\n")

    modes = [] #TODO load all modes here by name as string, if ALL then fill manually, always contain BLAST
    for mode in modes:
        for q, index in zip(search_input.query_data, range(len(search_input.query_data))):
            start = time.time()
            if (mode=="neural"):
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

            elif (mode=="BLAST"):
                BLAST() #TODO blast part

            end = time.time()
            totalAproximateTime += (end - start)

            # output
            AFcount += results[0][1]/exhaustResults[0][1]
            recNcount += sum(x not in results for x in exhaustResults)

            outputFile.write(format_output(index, [r1 +r2[1:] for r1, r2 in zip(results, exhaustResults)],search_input.search_radius))
    outputFile.write(format_footer(len(search_input.query_file), search_input.nearest_neighbors, totalAproximateTime, totalExhaustTime, AFcount, recNcount))
    outputFile.close()

if __name__ == "__main__":
    main()