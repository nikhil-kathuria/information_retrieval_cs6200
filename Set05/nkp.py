import random
import collections
import pyliblinear
# from glob import glob


def querygen():
    fileloc = "query_desc.51-100.short.txt"
    querylist = list()
    qfile = open(fileloc)
    for line in qfile:
        querylist.append(line.split('.')[0])
    qfile.close()
    # Retrun a list of query numbers present in query file
    return querylist


def fetchqrel():
    ''' Returns three dict first a  mapping from  qno -> docno -> reelevance
    i.e docs which are present in qrelfile. Second a dict from docID -> newID
    Third a reverse dictionary of above i.e. newID -> DocID'''
    qurydocdict = dict()
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
            if values[0] in qurydocdict:
                qurydocdict[values[0]].update({values[2]: int(values[3])})
            else:
                qurydocdict[values[0]] = {values[2]: int(values[3])}
            docmapdict[values[2]] = counter
            reversedocdict[counter] = values[2]
    return (qurydocdict, docmapdict, reversedocdict)


def randomquery(train):
    '''Returns two list where first is list of remaining queries of input list
    where the second list of 5 members fromed random selection from input'''
    test = list()
    for itr in range(0, 5):
        val = random.choice(train)
        test.append(val)
        train.remove(val)
    return (train, test)


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
        for doc in sorted(qdict[qno]):
            matrixfile.write(str(qdict[qno][doc]) + "\t")
            itr = 0
            for model in scores:
                itr += 1
                if qno in scores[model]:
                    if doc in scores[model][qno]:
                            matrixfile.write(str(itr) + ":")
                            matrixfile.write(str(scores[model][qno][doc]) + "\t")
            matrixfile.write("\n")
    matrixfile.close()
    '''Write individual matrixfile for test query in same fashion as above
    As well as maintain a dcitionary qno -> (list of docs)'''
    counter = 0
    testdocdict = collections.defaultdict(list)
    # testqdict = dict()
    for qno in sorted(test):
        counter += 1
        name = str(counter) + ".txt"
        filename = open(name, 'w')
        for doc in sorted(qdict[qno]):
            testdocdict[counter].append(doc)
            filename.write(str(qdict[qno][doc]) + "\t")
            itr = 0
            for model in scores:
                itr += 1
                if qno in scores[model]:
                    if doc in scores[model][qno]:
                            filename.write(str(itr) + ":")
                            filename.write(str(scores[model][qno][doc]) + "\t")
            filename.write("\n")
        filename.close()
    return (test, testdocdict)


def trainmodel(predict, preddict):
    matrixfile = open("FeatureMatrix.txt")
    # Now load the file in Feature Matrix
    fmobj = pyliblinear._liblinear.FeatureMatrix
    fmmatrix = fmobj.load(matrixfile)
    # save(fmmatrix)
    model = pyliblinear.Model
    modinst = model.train(fmmatrix)
    # Open first file
    name1 = open('1.txt', 'r')
    fmobj1 = pyliblinear._liblinear.FeatureMatrix
    mmatrix1 = fmobj1.load(name1)
    modprdc = model.predict(modinst, mmatrix1)
    # modinst.save("Trained.txt")
    scoremap = zip(preddict[1], modprdc)
    for data in scoremap:
        print(data)
    sortedmap = sorted(scoremap, key=lambda x: x[1], reverse=True)
    predict.sort()
    val = predict[0]
    print(len(sortedmap))
    print(sortedmap)
    scorefile = open("FinalScore.txt", 'a')
    for itr in range(0, len(sortedmap)):
        scorefile.write(str(val) + " Q0 " + str(sortedmap[itr][0]) + " "
            + str(itr + 1) + " " + str(sortedmap[itr][1]) + " Exp\n")
    scorefile.close()


def main():
    # Generate the matrix and write on file
    (predict, qdict) = genmatfile()
    # Call liblinear to train on data
    trainmodel(predict, qdict)


if __name__ == '__main__':
    main()
