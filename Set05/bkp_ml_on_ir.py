import random
import collections
# import pyliblinear
# from glob import glob


def querygen():
    fileloc = "query_desc.51-100.short.txt"
    querylist = list()
    qfile = open(fileloc)
    for line in qfile:
        querylist.append(line.split('.')[0])
    qfile.close()
    return querylist


def fetchqrel():
    qurydocdict = collections.defaultdict(list)
    docmapdict = dict()
    reversedocdict = dict()
    counter = 0
    fileloc = "qrels.adhoc.51-100.AP89.txt"
    qrelfile = open(fileloc)
    querylist = querygen()
    for line in qrelfile:
        values = line.split()
        if values[0] in querylist:
            counter += 1
            qurydocdict[values[0]].append(values[2])
            docmapdict[values[2]] = counter
            reversedocdict[counter] = values[2]
    return (qurydocdict, docmapdict, reversedocdict)


def randomquery(queries):
    train = list()
    for itr in range(0, 4):
        val = random.choice(queries)
        train.append(val)
        queries.remove(val)
    return (train, queries)


def modelscores():
    models = ["JLKM", "BM25", "TF", "TFIDF", "LML"]
    scores = dict()
    for model in models:
        filename = model + ".txt"
        docdict = dict()
        docfile = open(filename)
        for line in docfile:
            val = line.split()
            # Create a dict of dict such that qno -> docno -> score
            if val[0] in docdict:
                docdict[val[0]].update({val[2]: round(float(val[4]), 4)})
            else:
                docdict[val[0]] = {val[2]: round(float(val[4]), 4)}
        docfile.close()
        scores[model] = docdict
    return scores


def genmatfile():
    # Get dicts, qno-> (list docs) , docid -> label , label -> docid
    (qdict, docdict, revdict) = fetchqrel()
    # Get random 20 query ID
    (train, test) = randomquery(list(qdict.keys()))
    scores = modelscores()
    matrixfile = open("FeatureMatrix.txt", 'w')
    '''Write matrix to file such that each document vector is row in Feature
    matrix and the first column represents different documents identified with
    integer labels followed by index position and value tuple as index:tuple'''
    for qno in sorted(train):
        for doc in qdict[qno]:
            matrixfile.write(str(docdict[doc]) + "\t")
            itr = 0
            for model in scores:
                itr += 1
                if qno in scores[model]:
                    if doc in scores[model][qno]:
                            matrixfile.write(str(itr) + ":")
                            matrixfile.write(str(scores[model][qno][doc]) + "\t")
            matrixfile.write("\n")
    matrixfile.close()


def main():
    genmatfile()

if __name__ == '__main__':
    main()
