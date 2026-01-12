import torch
import esm
import argparse

def read_fasta(filepath: str):
    proteins = []
    current_header = None
    current_sequence = []
    with open(filepath, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current_header is not None:
                    proteins.append((current_header, "".join(current_sequence)))

                current_header = line[1:]
                current_sequence = []
            else:
                current_sequence.append(line)
        if current_header is not None:
            proteins.append((current_header, "".join(current_sequence)))
    return proteins

def main():
    # 1. Φόρτωση Μοντέλου
    model, alphabet = esm.pretrained.esm2_t6_8M_UR50D() 
    batch_converter = alphabet.get_batch_converter()
    
    # 2. Προετοιμασία Εισόδου (με Truncation)
    parser = argparse.ArgumentParser(
        description="Process vectors and query targets."
    )
    parser.add_argument(
        "-d", "--data",
        required=True,
        help="Input data file (e.g. vectors.dat)"
    )
    parser.add_argument(
        "-q", "--query",
        required=True,
        help="Query file (e.g. targets.fasta)"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output results file (e.g. results.txt)"
    )
    args = parser.parse_args()
    data = read_fasta(args.data)
    for item in data:
        if len(item[1]) > 1022:
            item[1] = item[1][:1022]
    query = read_fasta(args.query)
    labels, strs, tokens = batch_converter(data)

    # 3.Inference 
    with torch.no_grad(): 
        results = model(tokens, repr_layers=[6])
    
    # 4. Mean Pooling
    token_embeddings = results["representations"][6]
    embedding = token_embeddings.mean(dim=1)


if __name__ == "__main__":
    main()