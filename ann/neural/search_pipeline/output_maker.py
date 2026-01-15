def format_output(image_id: int, results: list[list[int]], r: int = 0) -> str:
    header = "Query: {qID}\n"
    bodyPiece = "Nearest neighbor-{count}: {neighborID}\ndistanceApproximate: {dis}\ndistanceTrue: {disT}\n\n"
    rPiece = "R-near neighbors:\n"

    output = header.format(qID=image_id)
    for result, index in zip(results, range(len(results))):
        output += bodyPiece.format(count=index, neighborID=result[0], dis=result[1], disT=result[2])
    if r != 0:
        output += rPiece
        for result in results:
            if result[1] < r:
                output += str(result[0])
    return output


def format_footer(queryCount: int, N: int, apTime: float, truTime: float, AFcount: int, recNcount: int) -> str:
    footer = "\nAverage AF: {avAF}\nRecall@N: {recN}\nQPS: {qps}\ntApproximateAverage: {tAvg}\ntTrueAverage: {tTrueAvg}"
    avAF = AFcount / queryCount
    recN = recNcount / (queryCount * N)
    tAvg = apTime / N
    tTrue = truTime / N
    return footer.format(avAF=avAF, recN=recN, qps=1 / tAvg, tAvg=tAvg, tTrueAvg=tTrue)
