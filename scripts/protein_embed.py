import argparse
import torch
import esm
from torch.amp import autocast

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

def batch_by_tokens(pairs, max_tokens=6000, extra_tokens=2):
    pairs = sorted(pairs, key=lambda x: len(x[1]), reverse=True)
    batch = []
    tok_count = 0
    for h, s in pairs:
        n = len(s) + extra_tokens
        if batch and tok_count + n > max_tokens:
            yield batch
            batch = []
            tok_count = 0
        batch.append((h, s))
        tok_count += n
    if batch:
        yield batch

def mean_pool_per_sequence(reps, batch):
    out = []
    for i, (lbl, seq) in enumerate(batch):
        L = len(seq)
        emb = reps[i, 1 : L + 1].mean(dim=0)
        out.append((lbl, emb.detach().cpu()))
    return out

def main():
    parser = argparse.ArgumentParser(description="Embed protein sequences with ESM2 (OOM-safe batching).")
    parser.add_argument("-i", "--data", required=True, help="Input FASTA file")
    parser.add_argument("-o", "--output", required=True, help="Output embeddings (one line per sequence)")
    args = parser.parse_args()
    model, alphabet = esm.pretrained.esm2_t6_8M_UR50D()
    batch_converter = alphabet.get_batch_converter()
    use_cuda = torch.cuda.is_available() and torch.cuda.get_device_capability(0) >= (7, 0)
    device = torch.device("cuda" if use_cuda else "cpu")
    model = model.to(device).eval()
    data = [(h, s[:1022]) for (h, s) in read_fasta(args.data)]
    with open(args.output, "w") as out_f, torch.no_grad():
        for batch in batch_by_tokens(data, max_tokens=6000, extra_tokens=2):
            labels, strs, tokens = batch_converter(batch)
            tokens = tokens.to(device, non_blocking=True)
            if device.type == "cuda":
                with autocast('cuda'):
                    results = model(tokens, repr_layers=[6])
            else:
                results = model(tokens, repr_layers=[6])
            reps = results["representations"][6]
            for lbl, emb_cpu in mean_pool_per_sequence(reps, batch):
                out_f.write(lbl + "\t" + " ".join(map(str, emb_cpu.tolist())) + "\n")
                out_f.flush()
            del tokens, results, reps
            if device.type == "cuda":
                torch.cuda.empty_cache()


if __name__ == "__main__":
    main()