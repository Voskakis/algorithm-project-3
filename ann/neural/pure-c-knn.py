from my_types import SearchInput
import time, math

def format_output(image_id: int, results: list[list[int]], r:int=0) -> str:
    header = "Query: {qID}\n"
    bodyPiece = "Nearest neighbor-{count}: {neighborID}\ndistanceApproximate: {dis}\ndistanceTrue: {disT}\n\n}"
    rPiece = "R-near neighbors:\n"

    output = header.format(qID = image_id)
    for result, index in zip(results, range(len(results))):
        output += bodyPiece.format(count=index, neighborID = result[0], dis = result[1], disT=result[2])
    if r!=0:
        output += rPiece
        for result in results:
            if result[1]<r:
                output += str(result[0])
    return output

def format_footer(queryCount: int, N:int, apTime:float, truTime: float, AFcount:int, recNcount:int)->str:
    footer = "Average AF: {avAF}\nRecall@N: {recN}\nQPS: {qps}\ntApproximateAverage: {tAvg}\ntTrueAverage: {tTrueAvg}"
    avAF = AFcount/queryCount
    recN = recNcount/(queryCount*N)
    tAvg = apTime/N
    tTrue = truTime/N
    return footer.format(avAF=avAF, recN=recN, QPS = 1/tAvg, tAvg=tAvg, tTrue=tTrue)

def euclidean(vector1, vector2):
    total = 0
    for x, y in zip(vector1, vector2):
        total += (x - y)**2
    return math.sqrt(total)

def add_better_result(point, q, result_list, N):
    distance = euclidean(point, q)
    if len(result_list) < N:
        result_list.append([point, distance])
    elif distance < result_list[0][1]:
        result_list[0] = [point, distance]
    if len(result_list) >= N > 1:
        max_index = max(range(len(result_list)), key=lambda x: x[1])
        result_list[0], result_list[max_index] = result_list[max_index], result_list[0]
    return result_list

def exhaustive_search(point_set: list[list[int]], q, N) -> list[list[int]]:
    result_list = []
    for point in point_set:
        result_list = add_better_result(point, q, result_list, N)
    result_list = sorted(result_list, key=lambda x: x[1])
    return result_list

def main():
    search_input = SearchInput.parse_args()

    buckets_file = [] #TODO use C to get every point of each bucket here

    totalAproximateTime = 0
    totalExhaustTime = 0
    AFcount = 0
    recNcount = 0

    outputFile = open(search_input.output_file, "a")
    outputFile.write("C LSH\n")

    for q, index in zip(search_input.query_file, range(len(search_input.query_file))):
        start = time.time()
        # calculate hash buckets to use with c
        labels = [] #TODO do it using C
        # candidates
        search_space = []
        for label in labels:
            for pointID in buckets_file[label]:
                search_space.append(search_input.input_file[pointID])
        # exhaustive search
        results = exhaustive_search(search_space, q, search_input.nearest_neighbors)
        end = time.time()
        totalAproximateTime += (end - start)

        # brute force
        start = time.time()
        exhaustResults = exhaustive_search(search_input.input_file, q, search_input.nearest_neighbors)
        end = time.time()
        totalExhaustTime += (end - start)

        # output
        AFcount += results[0][1] / results[0][2]
        recNcount += sum(x not in results for x in exhaustResults)

        outputFile.write(
            format_output(index, [r1 + r2[1:] for r1, r2 in zip(results, exhaustResults)], search_input.search_radius))
    outputFile.write(format_footer(len(search_input.query_file), search_input.nearest_neighbors, totalAproximateTime,
                                   totalExhaustTime, AFcount, recNcount))
    outputFile.close()


if __name__ == "__main__":
    main()