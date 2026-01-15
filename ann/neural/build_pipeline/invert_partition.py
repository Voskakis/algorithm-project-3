def invert_partition(blocks: list[int], nblocks: int) -> list[list[int]]:
    """
    Given block assignment per vertex, return list where index = block,
    value = list of vertices in that block.
    """
    inv = [[] for _ in range(nblocks)]
    for v, b in enumerate(blocks):
        inv[b].append(v)
    return inv


def write_inverted(inv: list[list[int]], path: str):
    with open(path, "w") as f:
        for line in inv:
            f.write(f"{line}\n")
