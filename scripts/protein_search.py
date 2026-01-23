import argparse
import os

os.environ["PATH"]=r"C:\Users\User\mingw64\bin;" + os.environ["PATH"]

import sys
import tempfile
import time
import subprocess
from pathlib import Path

from numpy.f2py.auxfuncs import throw_error

# from ann.neural import initialize_nlsh, search_nlsh, euclidean
from blast.blast_results import results_by_BLAST, load_BLAST_results
from blast.blast_compare import blast_identity_by_fasta_id
from scripts import protein_embed

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

def main():
    parser = argparse.ArgumentParser(description="Query on an embedded database")
    parser.add_argument("-d", "--database", required=True, help="Input embeds file")
    parser.add_argument("-q", "--query", required=True, help="List of sequence queries")
    parser.add_argument("-o", "--output", required=True, help="Output directory")
    parser.add_argument("-m", "--method", required=True, help="Options are all/lsh/neural/hypercube/ivf")
    parser.add_argument("-f", "--fasta", required=True, help="Pre-embedding fasta file")
    parser.add_argument("-n", "--number", required=True, help="Count of results to retrieve")
    args = parser.parse_args()

    #if args.method == "all" or args.method == "neural":
    #    initialize_nlsh(args.database)



    outputFile = open(args.output, "a")

    modes = ["BLAST"]
    match args.method:
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
    #results_by_BLAST(args.fasta, args.query, "blast_results.tsv")
    end = time.time()
    BLAST_time = (end - start)/len(args.query)
    BLAST_results = load_BLAST_results(int(args.number), "blast_results.tsv")

    query_data_parsed = []
    argv_holder = sys.argv
    sys.argv = ["protein_embed.py",'-i', args.query, '-o', 'query_vectors.dat']
    protein_embed.main()
    sys.argv = argv_holder

    query_sequences = []
    with open(args.query, 'r') as fasta:
        for line in fasta:
            if line[0] == ">":
                query_sequences.append("")
            else:
                query_sequences[-1]+=line[:len(line)-1]

    protein_names = []
    with open(args.fasta, 'r') as fasta:
        for line in fasta:
            if line[0] == ">":
                protein_names.append(line[1:].split()[0])

    with open('query_vectors.dat', "r") as q_vecs:
        for line in q_vecs:
            elements = line.split('\t')
            query_data_parsed.append((elements[0], elements[1:]))

    database_parsed = []
    with open(args.database, 'r') as database:
        datumIndexCount = 0
        for datum in database:
            elements = datum.split(' ')
            database_parsed.append((protein_names[datumIndexCount], elements))
            datumIndexCount+=1


    for q, query_sequence, index in zip(query_data_parsed, query_sequences, range(len(args.query))):
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
            if mode== "BLAST":
                continue
            elif mode== "Neural LSH":
                #result = search_nlsh(query_vector, args.number),     #this one's output is of the format [num_id, num_id,...]
                temp_results = []
                for r in result:
                    temp_results.append(database_parsed[r])
                method_results.append(temp_results)

            elif mode== "Euclidean LSH":
                result = ""
                with open("query_vector_holder.txt", 'w') as tmp:
                    tmpString = "\t".join(query_vector)
                    tmp.write(tmpString)
                    QUERY_FULL_NAME = os.path.abspath(tmp.name)
                    ROOT = Path(__file__).resolve().parents[1]
                    LSH_EXEC = ROOT / "ann" / "lsh" / "lsh.exe"
                    DATASET_FULL_NAME = ROOT / args.database

                    tmp.close()

                    result = subprocess.run( #output format is "num_id num_id num_id ..."
                        [str(LSH_EXEC), "-d", str(DATASET_FULL_NAME), "-q", QUERY_FULL_NAME,
                         "-N", f"{args.number}", "-o", "none"], capture_output=True, text=True, shell=True
                    )
                    if result=="":
                        throw_error("protein_search, line 135ish, 'with' scope issue")
                    temp_results = []
                    for r in result.stdout.split(' '):
                        result_index = int(r)
                        temp_results.append(database_parsed[result_index])
                    method_results.append(temp_results)

            #method_results must be of form [(2, [2,2,2,2]),...]
            end = time.time()
            method_time.append(end - start)
            temp_blast_results = BLAST_results[query_name]

            method_rec.append(sum(x not in method_results[-1] for x in temp_blast_results)
                         / len(temp_blast_results))

            included = []
            bid = []
            distance = []
            temp_method_results = []
            for protein in method_results[-1]:
                temp_bid = blast_identity_by_fasta_id(args.fasta, query_sequence, protein[0])
                if temp_bid < 0.3:
                    bid.append(temp_bid)
                    temp_method_results.append(protein[0])
                    #distance.append(euclidean(protein[1], query_vector))
                    if protein[0] not in temp_blast_results:
                        included.append("No")
                    else:
                        included.append("Yes")

            method_results = temp_method_results
            method_included.append(included)
            method_bid.append(bid)
            method_distance.append(distance)

        # output
        outputBlock = format_output(query_name, args.number, modes, BLAST_time, method_rec,
                                    method_included, method_results, method_bid, method_distance, method_time)
        outputFile.write(outputBlock)
        print(outputBlock)
    outputFile.close()

if __name__ == "__main__":
    main()

# executable B