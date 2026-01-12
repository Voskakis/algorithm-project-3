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

def batched(iterable, n):
    for i in range(0, len(iterable), n):
        yield iterable[i:i+n]

def main():
    
    model, alphabet = esm.pretrained.esm2_t6_8M_UR50D()
    batch_converter = alphabet.get_batch_converter()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device).eval()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--data", required=True)
    parser.add_argument("-m", "--model", required=True)
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    data = [(h, s[:1022]) for (h, s) in read_fasta(args.data)]
    BATCH_SIZE = 16
    with open(args.output, "w") as out_f, torch.no_grad(): 
        for batch in batched(data, BATCH_SIZE):
            labels, strs, tokens = batch_converter(batch)
            tokens = tokens.to(device)
            results = model(tokens, repr_layers=[6])
            reps = results["representations"][6]
            for i, (lbl, seq) in enumerate(batch):
                L = len(seq)
                emb = reps[i, 1:L+1].mean(dim=0).detach().cpu().tolist()
                out_f.write(" ".join(map(str, emb)) + "\n")


if __name__ == "__main__":
    main()