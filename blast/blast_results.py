import subprocess
from collections import defaultdict


def results_by_BLAST(input_data, query_file, results_directory):
    command = ("makeblastdb -in "
                   + input_data
                   +" -dbtype prot -out swissprot_db && blastp -db swissprot_db -query "
                   + query_file
                   +" -outfmt \"6 qseqid sseqid pident evalue bitscore\" -out "
                   + results_directory)

    subprocess.run(command, shell=True, capture_output=True, text=True)

def load_BLAST_results(k: int, results_directory: str, threshold: float= 0.01):
    data = defaultdict(list)

    with open(results_directory, "r", encoding="utf-8") as f:
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

    # Sort each list by bitscore (descending) and keep top k
    for key in data:
        data[key].sort(key=lambda x: x[2], reverse=True)
        data[key] = data[key][:k]

    return data