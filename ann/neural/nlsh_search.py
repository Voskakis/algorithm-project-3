import time

import torch
import torch.nn.functional as F

from build_pipeline import load_inverted_file
from build_pipeline.neural import MLPClassifier
from enums import EndianType
from my_types import SearchInput
from search_pipeline.helpers import exhaustive_search
from search_pipeline.output_maker import format_output, format_footer


def main():
    search_input = SearchInput.parse_args()
    inverted_file = load_inverted_file(search_input.index_path.name + "/inverted_file.txt")

    input_dim = 128 if search_input.type is EndianType.Sift else 28 * 28
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MLPClassifier(d_in=input_dim, n_out=search_input.members, layers=search_input.layers,
                          nodes=search_input.nodes).to(device)
    model.load_state_dict(torch.load(search_input.index_path.name + "/model.pt"))
    model.eval()

    totalAproximateTime = 0
    totalExhaustTime = 0
    AFcount = 0
    recNcount = 0

    outputFile = open(search_input.output_file, "w")
    outputFile.write("Neural LSH\n")

    for q, index in zip(search_input.query_data, range(len(search_input.query_data))):
        start = time.time()
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
        end = time.time()
        totalAproximateTime += (end - start)

        # brute force
        start = time.time()
        exhaustResults = exhaustive_search(search_input.input_data, q, search_input.nearest_neighbors)
        end = time.time()
        totalExhaustTime += (end - start)

        # output
        AFcount += results[0][1] / exhaustResults[0][1]
        recNcount += sum(x not in results for x in exhaustResults)

        outputFile.write(
            format_output(index, [r1 + r2[1:] for r1, r2 in zip(results, exhaustResults)], search_input.search_radius))
    outputFile.write(format_footer(len(search_input.query_data), search_input.nearest_neighbors, totalAproximateTime,
                                   totalExhaustTime, AFcount, recNcount))
    outputFile.close()


if __name__ == "__main__":
    main()
