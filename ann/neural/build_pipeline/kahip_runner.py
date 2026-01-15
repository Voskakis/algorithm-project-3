import faulthandler

import kahip


def run_kahip(vwgt, xadj, adjcwgt, adjncy, nblocks, imbalance, seed, mode):
    """
    Calls the KaHIP library function kaffpa.
    Returns: blocks (list[int]), edgecut (int)
    """
    faulthandler.enable()

    edgecut, blocks = kahip.kaffpa(vwgt,  # The array should have size n.
        xadj,  # holds the pointers to the adjacency lists of the vertices. The array should have size n + 1.
        adjcwgt,  # holds the weights of the edges if they exist. The array should have size 2m.
        adjncy,  # holds the adjacency lists of the vertices. The array should have size 2m.
        nblocks, imbalance, 0, seed, mode)

    return blocks, edgecut
