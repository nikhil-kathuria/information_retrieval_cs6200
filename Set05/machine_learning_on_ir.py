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
    models = ["JLKM", "BM25", "TF", "TFIDF", "LML", "PROX"]
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
    # Get dicts, qno-> (list docs)
    (qdict, docdict, revdict) = fetchqrel()

    # Get random 20 query ID
    (train, test) = randomquery(list(qdict.keys()))
    scores = modelscores()
    traindocdict = collections.defaultdict(list)
    matrixfile = open("FeatureMatrix.txt", 'w')
    '''Write matrix to file such that each document vector is row in Feature
    matrix and the first column represents different documents identified with
    integer labels followed by index position and value tuple as index:tuple'''
    for qno in sorted(train):
        name = qno + ".txt"
        filename = open(name, 'w')
        for doc in sorted(qdict[qno]):
            traindocdict[qno].append(doc)
            matrixfile.write(str(qdict[qno][doc]) + "\t")
            filename.write(str(qdict[qno][doc]) + "\t")
            itr = 0
            for model in scores:
                itr += 1
                if qno in scores[model]:
                    if doc in scores[model][qno]:
                            matrixfile.write(str(itr) + ":")
                            matrixfile.write(str(scores[model][qno][doc]) + "\t")
                            filename.write(str(itr) + ":")
                            filename.write(str(scores[model][qno][doc]) + "\t")
            matrixfile.write("\n")
            filename.write("\n")
        filename.close()
    matrixfile.close()
    '''Write individual matrixfile for test query in same fashion as above
    As well as maintain a dcitionary qno -> (list of docs)'''
    testdocdict = collections.defaultdict(list)
    # testqdict = dict()
    for qno in sorted(test):
        name = qno + ".txt"
        filename = open(name, 'w')
        for doc in sorted(qdict[qno]):
            testdocdict[qno].append(doc)
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
    return (testdocdict, traindocdict)


def trainmodel(testdict, traindict):
    # Open Matrix file and create FeatureMatrix Object and load file
    matrixfile = open("FeatureMatrix.txt")
    fmobj = pyliblinear._liblinear.FeatureMatrix
    fmatrix = fmobj.load(matrixfile)
    # Create a Model object and train on FeatureMatrix Object created
    model = pyliblinear.Model
    modelinst = model.train(fmatrix)
    modelinst.save("Trained.txt")
    matrixfile.close()
    # Generate score file test and train data
    generatescorefile(model, modelinst, testdict, "TestScore.txt")
    generatescorefile(model, modelinst, traindict, "TrainScore.txt")


def generatescorefile(modelobj, modelinst, dictobj, output):
    cnt = 0
    for tdata in sorted(dictobj.keys()):
        tname = open(tdata + '.txt', 'r')
        # Create a matrix for the test data over queries
        tfmobj = pyliblinear._liblinear.FeatureMatrix
        tfmatrix = tfmobj.load(tname)
        tname.close()
        ''' Predict the lables by model generated. Now the output label list
        and docid list needs to zipped and later we need to sort the Final
        tuple list i.e. (docid, label) as per label descending'''
        tmodprdc = modelobj.predict(modelinst, tfmatrix)
        scoremap = zip(dictobj[tdata], tmodprdc)
        scoredict = dict()
        for data in scoremap:
            scoredict[data[0]] = data[1]
        sortedmap = sorted(scoredict.items(), key=lambda x: x[1], reverse=True)
        scorefile = open(output, 'a')
        length = len(sortedmap)
        for itr in range(0, length):
            scorefile.write(str(tdata) + " Q0 " + str(sortedmap[itr][0])
                 + " " + str(itr + 1) + " " + str(length - itr) + " Exp\n")
        scorefile.close()
        cnt += 1


def main():
    # Generate the matrix and write on file
    (testdict, traindict) = genmatfile()
    # Rewrite the Final scores file
    scorefile = open("TestScore.txt", 'w')
    scorefile.write("")
    scorefile.close()
    scorefile = open("TrainScore.txt", 'w')
    scorefile.write("")
    scorefile.close()
    # Call liblinear to train on data
    trainmodel(testdict, traindict)


if __name__ == '__main__':
    main()
