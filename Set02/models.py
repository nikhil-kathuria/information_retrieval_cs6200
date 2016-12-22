from glob import glob
import re
from stemming.porter import stem
import operator
import math
import json
from sets import Set


def textmod(text):
    # Remove apostrophe and next succeeding alphabatic character
    text = re.sub('[\'][a-zA-Z] ', ' ', text)
    # Remove all occurences where they do not match pattern \w
    text = re.sub('[^a-zA-Z0-9. ]', ' ', text)
    # Replace multiple occurence of dot with single dot
    text = re.sub('\.\.+', '.', text)
    # Remove dot after each word and each sentence
    text = re.sub('[.] |[.]$', ' ', text)
    # Remove sigle occurence of alphabet surrounded by blanks
    text = re.sub(' [a-zA-Z] ', ' ', text)
    # text = re.match("\\w+(\\.?\\w+)*", text)
    text = text.lower()
    return text


def parsequery():
    stoplist = list()
    # Open the file
    openfile = open('stopwords.txt', 'r')
    # Read each line from the input file
    for line in openfile:
        # Strip new line char and spaces
        line = line.strip()
        # Append the word to list
        stoplist.append(line)
    openfile.close()
    # Now start processing query
    querymap = {}
    # Check for query file
    for filename in glob('./AP_DATA/query_desc.51-100.short.txt'):
        # Open the file
        openfile = open(filename)
        # Read each line from the input file
        for line in openfile:
            # Strip new line char and spaces
            queryline = line.strip()
            querysects = queryline.split('.')
            # Ignore blank lines or lines will not '.'
            if len(querysects) == 3:
                queryno = querysects[0].strip()
                querywrds = querysects[1].strip().split()
                querystr = ""
                # For each query term check against stopword
                # Ignoring first three terms of querywrds
                for itr in xrange(3, len(querywrds)):
                    if querywrds[itr] not in stoplist:
                        querystr = querystr + querywrds[itr] + " "
                querystr = textmod(querystr)
            elif len(querysects) > 3:
                querywrds = ""
                queryno = querysects[0].strip()
                for itr in xrange(1, len(querysects)):
                    querywrds = querywrds + querysects[itr]
                querywrds = querywrds.strip().split()
                querystr = ""
                # For each query term check against stopword
                # Ignoring first three terms of querywrds
                for itr in xrange(3, len(querywrds)):
                    if querywrds[itr] not in stoplist:
                        querystr = querystr + querywrds[itr] + " "
                querystr = textmod(querystr)
            querymap[queryno] = querystr
    # print querymap["59"]
    # print stoplist
    # print len(stoplist)
    return querymap


def search(catdict, term):
    # Initialize list to store docids
    docs = list()
    ifile = open("Index.txt", 'r')
    ifile.seek(catdict[term][0])
    # Read the inverted in bytes i.e. stopoffset - startoffset
    invlist = ifile.read(catdict[term][1] - catdict[term][0])
    ifile.close()
    dblocks = invlist.split("|")
    for blk in dblocks:
        docid = blk.split(":")[0]
        docs.append(docid)
    return docs


def trmfreq(catdict, docid, term):
    ifile = open("Index.txt", 'r')
    ifile.seek(catdict[term][0])
    # Read the inverted in bytes i.e. stopoffset - startoffset
    invlist = ifile.read(catdict[term][1] - catdict[term][0])
    ifile.close()
    # Get dblokcs in array by splitting on "|"
    dblocks = invlist.split("|")
    for blk in dblocks:
        did = blk.split(":")[0]
        if did == docid:
            return len(blk.split(":")[1])


def docfreq(catdict, term):
    ifile = open("Index.txt", 'r')
    ifile.seek(catdict[term][0])
    # Read the inverted in bytes i.e. stopoffset - startoffset
    invlist = ifile.read(catdict[term][1] - catdict[term][0])
    ifile.close()
    # Get dblokcs in array by splitting on "|"
    doc_freq = len(invlist.split("|"))
    return doc_freq


def queryfreq(word, querystring):
    qryfrq = 0
    for term in querystring.split():
        if stem(word) == stem(term):
            qryfrq = qryfrq + 1
    return qryfrq


def avgdoclength(statdict, dlendict):
    avgdoclngth = statdict['sum_ttf'] / len(dlendict)
    return avgdoclngth


def vocab(statdict):
    return statdict['vocab_size']


def sumttf(statdict):
    return statdict['sum_ttf']


def okapitfcalc(catdict, query, statdict, dlendict):
    # tf for all matching docs for current term in loop
    doctf = {}
    # Store avg length of doc
    avglen = avgdoclength(statdict, dlendict)
    querywrds = query.split()
    ifile = open("Index.txt", 'r')
    for term in querywrds:
        # Create stem word of query
        term = stem(term)
        print term
        try:
            ifile.seek(catdict[term][0])
        except KeyError:
            print term.upper() + " -> IS ABSENT"
            continue
        # Read the inverted in bytes i.e. stopoffset - startoffset
        invlist = ifile.read(catdict[term][1] - catdict[term][0])
        dblocks = invlist.split("|")
        for block in dblocks:
            blkary = block.split(":")
            docid = blkary[0]
            # Calculate term frequency call trmdoc
            term_freq = len(blkary[1].split(" "))
            # Calculate document length
            doc_len = dlendict[docid]
            # Calculate tf score based on formula
            div = term_freq + .5 + (1.5 * (doc_len / avglen))
            tfscore = term_freq / div
            # Insert in map for docid -> tf
            if docid not in doctf:
                doctf[docid] = tfscore
            else:
                doctf[docid] = doctf[docid] + tfscore
        print len(doctf)
    ifile.close()
    return doctf


def tfidfcalc(catdict, query, statdict, dlendict):
    doctf = {}
    totaldocs = len(dlendict)
    avglen = avgdoclength(statdict, dlendict)
    querywrds = query.split()
    ifile = open("Index.txt", 'r')
    for word in querywrds:
        # Create stem word of query
        word = stem(word)
        print word
        try:
            ifile.seek(catdict[word][0])
        except KeyError:
            print word.upper() + " -> IS ABSENT"
            continue
        # Read the inverted in bytes i.e. stopoffset - startoffset
        invlist = ifile.read(catdict[word][1] - catdict[word][0])
        dblocks = invlist.split("|")
        for block in dblocks:
            blkary = block.split(":")
            docid = blkary[0]
            # Calculate term frequency call trmdoc
            term_freq = len(blkary[1].split(" "))
            # Calculate document length
            doc_len = dlendict[docid]
            # Calculate the document frequency
            doc_freq = len(dblocks)
            # Calculate tf score based on formula
            div = term_freq + .5 + (1.5 * (float(doc_len) / avglen))
            tfscore = term_freq / div
            # Calculate doc frequency calling docfreq
            idf = math.log1p(totaldocs / doc_freq)
            tfidscore = idf * tfscore
            if docid not in doctf:
                doctf[docid] = tfidscore
            else:
                doctf[docid] = doctf[docid] + tfidscore
        print len(doctf)
    ifile.close()
    return doctf


def okapibm25calc(catdict, query, statdict, dlendict):
    # Define constants
    k1 = 1.2
    k2 = 250
    b = .75
    # Initialize socre to document mapping dictionary
    doctf = {}
    totaldocs = len(dlendict)
    avglen = avgdoclength(statdict, dlendict)
    querywrds = query.split()
    ifile = open("Index.txt", 'r')
    for word in querywrds:
        # Create stem word of query
        word = stem(word)
        print word
        try:
            ifile.seek(catdict[word][0])
        except KeyError:
            print word.upper() + " -> IS ABSENT"
            continue
        # Read the inverted in bytes i.e. stopoffset - startoffset
        invlist = ifile.read(catdict[word][1] - catdict[word][0])
        dblocks = invlist.split("|")
        for block in dblocks:
            blkary = block.split(":")
            docid = blkary[0]
            # Calculate term frequency call trmdoc
            term_freq = len(blkary[1].split(" "))
            # Calculate document length
            doc_len = dlendict[docid]
            # Calculate query frequency calling query_freq'''
            query_freq = queryfreq(word, query)
            # Calculate the document frequency
            doc_freq = len(dblocks)
            # Calculate idf similar score value
            idfscore = math.log1p(totaldocs + .5 / float(doc_freq + .5))
            # Calculate okapi tf similar score value
            tfnum = term_freq + k1 * term_freq
            tfdeno = term_freq + k1 * ((1 - b) + b * (float(doc_len) / avglen))
            tfscore = tfnum / tfdeno
            # Calculate query frequency related score
            try:
                queryscore = query_freq + k2 * query_freq / float(query_freq + k2)
            except ZeroDivisionError:
                print "-> query score error"
                queryscore = 1
            # Calculate the product of all score for bm 25
            bm25score = idfscore * tfscore * queryscore
            if docid not in doctf:
                doctf[docid] = bm25score
            else:
                doctf[docid] = doctf[docid] + bm25score
        print len(doctf)
    ifile.close()
    return doctf


def lmlaplacecalc(catdict, query, statdict, dlendict):
    doctf = {}
    querywrds = query.split()
    vocabsize = vocab(statdict)
    ifile = open("Index.txt", 'r')
    for word in querywrds:
        # Create stem word of query
        word = stem(word)
        print word
        try:
            ifile.seek(catdict[word][0])
        except KeyError:
            print word.upper() + " -> IS ABSENT"
            continue
        # Read the inverted in bytes i.e. stopoffset - startoffset
        invlist = ifile.read(catdict[word][1] - catdict[word][0])
        dblocks = invlist.split("|")
        print len(dblocks)
        for block in dblocks:
            blkary = block.split(":")
            docid = blkary[0]
            # Calculate term frequency call trmdoc
            term_freq = len(blkary[1].split(" "))
            # Calculate document length
            doc_len = dlendict[docid]
            lpscore = float(term_freq + 1) / (doc_len + vocabsize)
            if docid not in doctf:
                doctf[docid] = math.log1p(lpscore)
            else:
                doctf[docid] = doctf[docid] + math.log1p(lpscore)
        print len(doctf)
    ifile.close()
    return doctf


def jelinekmecercalc(catdict, query, statdict, dlendict):
    doctf = {}
    querywrds = query.split()
    ifile = open("Index.txt", 'r')
    for word in querywrds:
        # Create stem word of query
        word = stem(word)
        print word
        try:
            ifile.seek(catdict[word][0])
        except KeyError:
            print word.upper() + " -> IS ABSENT"
            continue
        # Read the inverted in bytes i.e. stopoffset - startoffset
        invlist = ifile.read(catdict[word][1] - catdict[word][0])
        dblocks = invlist.split("|")
        # For each docid get term_freq and its score
        all_tf = 0
        all_ln = 0
        bckgrd = 0
        fregrd = 0
        for block in dblocks:
            blkary = block.split(":")
            docid = blkary[0]
            trmpos = blkary[1]
            # Calculate term frequency call trmdoc
            all_tf = all_tf + len(trmpos.split())
            # Calculate document length
            all_ln = all_ln + dlendict[docid]
        for block in dblocks:
            blkary = block.split(":")
            docid = blkary[0]
            # Calculate term frequency call trmdoc
            term_freq = len(blkary[1].split())
            # Calculate document length
            doc_len = dlendict[docid]
            # Calucate corpus frequency
            try:
                bckgrd = float(all_tf - term_freq) / (all_ln - doc_len)
                fregrd = float(term_freq) / doc_len
            except ZeroDivisionError:
                print "ERROR ->All document lenght sum same as document length"
            # Calulate lamba
            lmbda = .4
            jlmscore = lmbda * fregrd + (1 - lmbda) * bckgrd
            if docid not in doctf:
                doctf[docid] = math.log1p(jlmscore)
            else:
                doctf[docid] = doctf[docid] + math.log1p(jlmscore)
    return doctf


def proximsrch(catdict, query, statdict, dlendict):
    doctf = {}
    querywrds = query.split()
    vocabsize = vocab(statdict)
    ifile = open("Index.txt", 'r')
    for itr in xrange(0, len(querywrds) - 1):
        # Assign the current and next word to be compared for proximity
        curword = stem(querywrds[itr])
        nexword = stem(querywrds[itr + 1])
        # Get doc list and docid -> term_pos dict for both current and next word
        curid = list()
        curposdict = {}
        nexid = list()
        nexposdict = {}
        try:
            # Get the D blocks for term current
            ifile.seek(catdict[curword][0])
            curlist = ifile.read(catdict[curword][1] - catdict[curword][0])
            curblocks = curlist.split("|")
            # Get all docid in curid and corresponding term pos in curpos dict
            for block in curblocks:
                blkary = block.split(":")
                curid.append(blkary[0])
                curposdict[blkary[0]] = blkary[1]
            # Get the D blocks for term next
            ifile.seek(catdict[nexword][0])
            nexlist = ifile.read(catdict[nexword][1] - catdict[nexword][0])
            nexblocks = nexlist.split("|")
        # Get all docid in nexid and corresponding term pos in nextpos dict
            for block in nexblocks:
                blkary = block.split(":")
                nexid.append(blkary[0])
                nexposdict[blkary[0]] = blkary[1]
        except KeyError:
            continue
        # Get common docs and proceed on them
        commomdoc = Set(curid) & Set(nexid)
        if len(commomdoc) > 0:
            # print len(commomdoc)
            for docid in commomdoc:
                row = 10000
                citr = 0
                nitr = 0
                # Get integer term pos list of current and next word
                cposlst = curposdict[docid].split()
                nposlst = nexposdict[docid].split()
                cposlst = [int(x) for x in cposlst]
                nposlst = [int(x) for x in nposlst]
                # Perform the lowest span finding algorithm
                for dumyitr in xrange(0, (len(cposlst) + len(nposlst) - 1)):
                    if abs(cposlst[citr] - nposlst[nitr]) < row:
                        row = abs(cposlst[citr] - nposlst[nitr])
                    if (cposlst[citr] < nposlst[nitr]) or (nitr >= len(nposlst) - 1):
                        citr = citr + 1
                    elif (nposlst[nitr] < cposlst[citr]) or (citr >= len(cposlst) - 1):
                        nitr = nitr + 1
                    if nitr >= (len(nposlst) - 1):
                        nitr = (len(nposlst) - 1)
                    if citr >= (len(cposlst) - 1):
                        citr = (len(cposlst) - 1)
                # print row
                # Calculate score add or update the score for document
                score = (1500 - row) * (len(cposlst) + len(nposlst))
                if docid not in doctf:
                    doctf[docid] = score
                else:
                    doctf[docid] = doctf[docid] + score
    ifile.close()
    return doctf


def modelgen(catdict, querymap, dlendict, diddict, statdict, modelname, filename):
    # Create and empry score file file
    scorefile = open(filename, 'w')
    scorefile.write("")
    scorefile.close()
    for qno in xrange(50, 101):
        if str(qno) in querymap:
            print qno
            # Assign the string of corresponding query number
            querystr = querymap[str(qno)]
            # Get the dictionary of docno -> score
            if modelname == "okapitf":
                myscore = okapitfcalc(catdict, querystr, statdict, dlendict)
            elif modelname == "tfidf":
                myscore = tfidfcalc(catdict, querystr, statdict, dlendict)
            elif modelname == "okapibm25":
                myscore = okapibm25calc(catdict, querystr, statdict, dlendict)
            elif modelname == "lmlaplace":
                myscore = lmlaplacecalc(catdict, querystr, statdict, dlendict)
            elif modelname == "jelinekmecer":
                myscore = jelinekmecercalc(catdict, querystr, statdict, dlendict)
            elif modelname == "proximity":
                myscore = proximsrch(catdict, querystr, statdict, dlendict)
            # Get a list of tuple (value, key)
            myscore = sorted(myscore.items(), key=operator.itemgetter(1), reverse=True)
            # Get length and run the loop till 100 or lenght which is greater
            scorelength = len(myscore)
            # Check for matching document list size
            if scorelength < 1000:
                doc_count = scorelength
            else:
                doc_count = 1000
            # Print to output filename
            scorefile = open(filename, 'a')
            for itr in xrange(0, doc_count):
                docid = diddict[myscore[itr][0]]
                scorefile.write(str(qno) + " Q0 " + str(docid) + " "
                    + str(itr + 1) + " " + str(myscore[itr][1]) + " Exp\n")
            scorefile.close()


def main():
    print "Main executed"
    dlendict = json.load(open("doclen.json", 'r'))
    diddict = json.load(open("docid.json", 'r'))
    catdict = json.load(open("catalog.json", 'r'))
    statdict = json.load(open("statistics.json", 'r'))
    # parsedocs(elasrch)
    # temp = search(elasrch, "agreement,")
    # print temp
    # docids = search(elasrch, "mci")
    # print docids
    # print trmfreq(elasrch, "AP890102-0003", "high")
    # print corpusfreq(elasrch, "AP890102-0003", "high")
    # print docfreq(elasrch, "AP890102-0003", "high")

    # querymap = json.load(open('proximquery.json', 'r'))
    querymap = parsequery()
    # with open('query.json', 'w') as outfile:
    #   json.dump(querymap, indent=1, separators=(',', ': '), fp=outfile)
    # print querymap
    # okapitfcalc(elasrch, querymap['60'])
    # modelgen(catdict, querymap, dlendict, diddict, statdict, "okapitf", "OkapiTF.txt")
    # modelgen(catdict, querymap, dlendict, diddict, statdict, "tfidf", "TdfId.txt")
    # modelgen(catdict, querymap, dlendict, diddict, statdict, "okapibm25", "OkapiBM25.txt")
    # modelgen(catdict, querymap, dlendict, diddict, statdict, "lmlaplace", "LMlaplace.txt")
    # modelgen(catdict, querymap, dlendict, diddict, statdict, "jelinekmecer", "JLKMCRlaplace.txt")
    # modelgen(catdict, querymap, dlendict, diddict, statdict, "proximity", "ProximitySearch.txt")



if __name__ == '__main__':
    main()
