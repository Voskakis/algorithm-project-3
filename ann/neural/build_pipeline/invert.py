def create_inverted_file(blocks:list[int], nblocks:int, output_file:str):
  inverted = [[] for _ in range(nblocks)]
  for i in range(len(blocks)):
    inverted[blocks[i]].append(i)
  output = open(output_file, "w")
  for line in inverted:
    print(*line, sep=" ", file=output)
  output.close()

def load_inverted_file(inverted_file:str) -> list[list[int]]:
    with open(inverted_file, "rb") as file:
        inverted = []
        for line in file:
            inverted.append([int(i) for i in line.split()])
        return inverted