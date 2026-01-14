import math
import time
import subprocess
from ann.nlsh.nlsh import initialize_nlsh, search_nlsh
from blast.blast_results import results_by_BLAST, load_BLAST_results
from blast.blast_compare import blast_identity_by_fasta_id

#TODO port what needs porting

from enums import EndianType
from my_types import SearchInput

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
        initialize_nlsh(search_input.index_path,search_input.members,search_input.layers,search_input.nodes,
                        search_input.bins_check, search_input.input_data)



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

    start = time.time()
    results_by_BLAST(search_input.input_data, search_input.query_file, "blast_results.tsv")
    end = time.time()
    BLAST_time = (end - start)/len(search_input.query_data)
    BLAST_results = load_BLAST_results(search_input.nearest_neighbors, "blast_results.tsv")


    #TODO make embeds of the query file, result must me in the following format
    query_data_parsed = [('name','vector')]

    for q, index in zip(query_data_parsed, range(len(search_input.query_data))):
        query_vector  = q[1]
        query_name    = q[0]

        method_results  = []
        method_time     = []
        method_rec      = []
        method_included = []
        method_bid      = []
        method_distance = []

        for mode in modes:
            start = time.time()
            if (mode=="BLAST"):
                continue
            elif (mode=="Neural LSH"):
                method_results.append(exhaustive_search(
                    search_nlsh(query_vector),
                    query_vector, search_input.nearest_neighbors))

            elif (mode=="Euclidean LSH"):
                result = subprocess.check_output(
                    #["./lsh", "-d", f"./{build_input.input_file}", "-q", f"./{build_input.input_file}", "-k", f"10",
                    # "-L", f"{build_input.batch_size}", "-N",
                    # f"{build_input.knn_neighbors + 1}", "-o", "output.txt"] TODO handle LSH I/O
                )
                method_results.append(result.decode("utf-8"))


            end = time.time()
            method_time.append(end - start)
            temp_blast_results = BLAST_results[query_name]

            method_rec.append(sum(x not in method_results[-1] for x in temp_blast_results)
                         / len(temp_blast_results))

            included = []
            bid = []
            distance = []
            temp_method_results = []
            for protein in method_results:
                #TODO format it similarly by splitting name and vector, if needed
                temp_bid = blast_identity_by_fasta_id(search_input.fasta, query_vector, protein.name)
                if (temp_bid < 0.3):
                    bid.append(temp_bid)
                    temp_method_results.append(protein.name)
                    distance.append(euclidean(protein_vector, query_vector)) #TODO from protein_vectors.dat matching 'protein'
                    if protein not in temp_blast_results:
                        included.append("No")
                    else:
                        included.append("Yes")

            method_results = temp_method_results
            method_included.append(included)
            method_bid.append(bid)
            method_distance.append(distance)

        # output
        outputBlock = format_output(query_name, search_input.nearest_neighbors, modes, BLAST_time, method_rec,
                                    method_included, method_results, method_bid, method_distance, method_time)
        outputFile.write(outputBlock)
        print(outputBlock)
    outputFile.close()

if __name__ == "__main__":
    main()

