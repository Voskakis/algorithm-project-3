from collections import defaultdict


def build_graph_items(knn: list[list[int]]):
    adj_set = defaultdict(list)
    for u in range(len(knn)):
        for v in knn[u]:
            adj_set[u].append(v)
            adj_set[v].append(u)
    xadj = [0] * (len(knn) + 1)
    adjncy = []
    edge_count = 0
    for u in range(len(knn)):
        neighs = sorted(adj_set[u])
        adjncy.extend(neighs)
        edge_count += len(neighs)
        xadj[u + 1] = edge_count
    vwgt = [1] * len(knn)
    adjcwgt = [1] * len(adjncy)
    return adj_set, xadj, vwgt, adjcwgt, adjncy
