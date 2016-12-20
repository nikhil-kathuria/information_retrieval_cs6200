from elasticsearch import Elasticsearch
from glob import glob
import re
from stemming.porter import stem
import operator
import math
import json
import random

# Create a elasticsearch object by connecting at localhost:9200
elasrch = Elasticsearch("localhost:9200", timeout=600, max_retries=10, revival_delay=0)
# Declare variables, doc list, doc-text hash map, boolean var and empty string

# ignore 404 and 400
# elasrch.indices.delete(index='docset', ignore=[400, 404])

# ignore 400 cause by IndexAlreadyExistsException when creating an index
# elasrch.indices.create(index='docset', ignore=400)

# Parses all docs of AP89 and stores them in index 'docset'


def parsedocs(elasrch):
    # Define local variables
    doclist = []
    intext = False
    interimline = ""
    keymap = {}
    # Read all the files in glob
    # add /ap' + '*'
    for filename in glob('./AP_DATA/ap89_collection/ap' + '*'):
        openfile = open(filename)
        # Read each line from the input file
        for line in openfile:
            # Strip new line char and spaces
            line = line.strip()
            # Append the line of text
            if intext:
                if not re.match('</TEXT>', line):
                    interimline = interimline + " " + line
            # Check for the Docno closing tag
            if re.search('</DOCNO>', line):
                # Extract the docno out of document
                docno = (line.split('</DOCNO>')[0]).split('<DOCNO>')[1].strip()
                doclist.append(docno)
                # Flush the docno value and interimline to hash table
                text = interimline.strip()
                keymap[docno] = interimline.strip()
                elasrch.index(index='ap_89', doc_type='document', id=docno,
                              body={"docno": docno, "text": text})
                # Set interimline to empty string
                interimline = ""
            # Check for start text tag
            elif re.match('<TEXT>', line):
                intext = True
            elif re.match('</TEXT>', line):
                intext = False
            elif re.match('</DOC>', line):
                # Flush the docno value and interimline to hash table
                text = interimline.strip()
                keymap[docno] = interimline.strip()
                elasrch.index(index='ap_89', doc_type='document', id=docno,
                              body={"docno": docno, "text": text})
    # Checking the list
    # Create index
    # elasrch.index('docset',doclist[0], keymap[doclist[0]])
    # elasrch.index(index='docset', doc_type='document', id=doclist[0],
    #              body={"id": "doclist[0]", "text": keymap[doclist[0]]})
    # Traverse the list
    # for itr in (0,length):

# Searches for a term and give back an array of docids


def parsequery():
    # Create a list to store stopwords
    stoplist = []
    # Check for stoplist file
    for filename in glob('./AP_DATA/stoplist.txt'):
        # Open the file
        openfile = open(filename)
        # Read each line from the input file
        for line in openfile:
            # Strip new line char and spaces
            line = line.strip()
            # Append the word to list
            stoplist.append(line)

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
                querystr = querystr.lower()
                querystr = re.sub('[,.`"()]', '', querystr)
                querystr = re.sub('[-]', ' ', querystr)
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
                querystr = querystr.lower()
                querystr = re.sub('[,.`"()]', '', querystr)
                querystr = re.sub('[-]', ' ', querystr)
            querymap[queryno] = querystr
    # print querymap["59"]
    # print stoplist
    # print len(stoplist)
    return querymap


def search(elasrch, term):
    # for term in query.split():
    # result = elasrch.search(index='docset', q='text:' + term)
    # result = elasrch.search(index='docset', doc_type='docment', body={
    #                        "query": {"match": {"text": "'" + term + "'"}}})
    result = elasrch.search(index='ap_89', doc_type="document", body={
                            "query": {"match": {"text": "'" + term + "'"}}}, size =100000)
    # docs = [doc['_id'] for doc in result['hits']['hits']
    docs = []
    for doc in result['hits']['hits']:
        docs.append(doc['_id'])
    return docs


def trmfreq(elasrch, docid, term):
    result = elasrch.termvector(
        index='ap_89', doc_type="document", id=docid, term_statistics="true")
    # From jason object result parse values
    try:
        term_freq = result['term_vectors']['text']['terms'][term]['term_freq']
    except KeyError:
            print term + " -> is absent"
            term_freq = 1
    # Iterate over all term frequency in doc
    return term_freq


def docfreq(elasrch, docid, term):
    result = elasrch.termvector(
        index='ap_89', doc_type="document", id=docid, term_statistics="true")
    # From jason object result parse values
    try:
        doc_freq = result['term_vectors']['text']['terms'][term]['doc_freq']
    except KeyError:
        doc_freq = 1
    # Iterate over all term frequency in doc
    return doc_freq


def corpusfreq(elasrch, docid, term):
    result = elasrch.termvector(
        index='ap_89', doc_type="document", id=docid, term_statistics="true")
    try:
        crp_freq = result['term_vectors']['text']['terms'][term]['ttf']
    except KeyError:
        crp_freq = 1
    return crp_freq


def queryfreq(word, querystring):
    qryfrq = 0
    for term in querystring.split():
        if stem(word) == stem(term):
            qryfrq = qryfrq + 1
    return qryfrq


def avgdoclength(elasrch):
    result = elasrch.termvector(index='ap_89', doc_type="document",
                                id="AP891011-0104", term_statistics="true")
    doc_count = result['term_vectors']['text']['field_statistics']['doc_count']
    corpus_length = result['term_vectors']['text']['field_statistics']['sum_ttf']
    # Calculate  the avg doc lenth
    avgdoclngth = float(corpus_length) / doc_count
    return avgdoclngth


def totaldoc(elasrch):
    result = elasrch.termvector(index='ap_89', doc_type="document",
                                id="AP891011-0104", term_statistics="true")
    doc_count = result['term_vectors']['text']['field_statistics']['doc_count']
    return doc_count


def doclength(elasrch, docid):
    result = elasrch.search(index='ap_89', doc_type="document", body={"query"
        :{"match":{"docno": docid }}, "facets": {"text": {"statistical"
        : {"script": "doc['text'].values.size()"}}}})
    return result['facets']['text']['total']


def vocabsize(elasrch):
    result = elasrch.get(index='ap_89', body={"aggs" :
        {"unique_terms" : {"cardinality" : {"script" : "text"}}}})
    return result


def sumttf():
    result = elasrch.termvector(index='ap_89', doc_type="document",
                                id="AP891011-0104", term_statistics="true")
    corpus_length = result['term_vectors']['text']['field_statistics']['sum_ttf']
    return corpus_length

def okapitfcalc(elasrch, query, tfreq, doclen):
    # tf for all matching docs for current term in loop
    doctf = {}
    # Store avg length of doc
    avglen = avgdoclength(elasrch)
    querywrds = query.split()
    for word in querywrds:
        print word
        # Create stem word of query
        word = stem(word)
        # fetch all the docids for a query term
        docids = search(elasrch, word)
        # For each docid get term_freq and its score
        for docid in docids:
            try:
                # Calculate term frequency call trmdoc
                term_freq = tfreq[docid][word]
                # Calculate document length
                doc_len = doclen[docid]
                # Calculate tf score based on formula
            except KeyError:
                print word + " -> is absent"
                continue
            div = term_freq + .5 + (1.5 * (doc_len / avglen))
            tfscore = term_freq / div
            # Insert in map for docid -> tf
            if docid not in doctf:
                doctf[docid] = tfscore
            else:
                doctf[docid] = doctf[docid] + tfscore
    return doctf


def tfidfcalc(elasrch, query, tfreq, dcfreq, doclen):
    doctf = {}
    totaldocs = totaldoc(elasrch)
    avglen = avgdoclength(elasrch)
    querywrds = query.split()
    for word in querywrds:
        # Create stem word of query
        word = stem(word)
        print word
        # fetch all the docids for a query term
        docids = search(elasrch, word)
        # For each docid get term_freq and its score
        for docid in docids:
            try:
                # Calculate term frequency call trmdoc
                term_freq = tfreq[docid][word]
                # Calculate document length
                doc_len = doclen[docid]
                # Calculate document frequency
                doc_freq = dcfreq[word]['doc_freq']
            except KeyError:
                print word + " -> is absent"
                continue
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
    return doctf

def okapibm25calc(elasrch, query, tfreq, dcfreq, doclen):
    # Define constants
    k1 = 1.2
    k2 = 250
    b = .75
    # Initialize socre to document mapping dictionary
    doctf = {}
    totaldocs = totaldoc(elasrch)
    avglen = avgdoclength(elasrch)
    querywrds = query.split()
    for word in querywrds:
        # Create stem word of query
        word = stem(word)
        print word
        # fetch all the docids for a query term
        docids = search(elasrch, word)
        # For each docid get term_freq and its score
        for docid in docids:
            try:
                # Calculate term frequency call trmdoc
                term_freq = tfreq[docid][word]
                # Calculate document length
                doc_len = doclen[docid]
                # Calculate doc frequency calling doc_freq
                doc_freq = dcfreq[word]['doc_freq']
                # Calculate query frequency calling query_freq'''
                query_freq = queryfreq(word, query)
            except KeyError:
                # print word + " -> is absent"
                continue
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
    return doctf


def lmlaplacecalc(elasrch, query, tfreq, dcfreq, doclen):
    doctf = {}
    totaldocs = totaldoc(elasrch)
    avglen = avgdoclength(elasrch)
    querywrds = query.split()
    vocabsize = 178050
    for word in querywrds:
        # Create stem word of query
        word = stem(word)
        print word
        # fetch all the docids for a query term
        docids = search(elasrch, word)
        # For each docid get term_freq and its score
        for docid in docids:
            try:
                # Calculate term frequency call trmdoc
                term_freq = tfreq[docid][word]
                # Calculate document length
                doc_len = doclen[docid]
            except KeyError:
                print word + " -> is absent"
                continue
            lpscore = float(term_freq + 1) / (doc_len + vocabsize)
            if docid not in doctf:
                doctf[docid] = math.log1p(lpscore)
            else:
                doctf[docid] = doctf[docid] + math.log1p(lpscore)
    return doctf


def jelinekmecercalc(elasrch, query, tfreq, dcfreq, doclen):
    doctf = {}
    querywrds = query.split()
    vocabsize = 178050
    for word in querywrds:
        # Create stem word of query
        word = stem(word)
        print word
        # fetch all the docids for a query term
        docids = search(elasrch, word)
        # For each docid get term_freq and its score
        all_tf = 0
        all_ln = 0
        bckgrd = 0
        fregrd = 0
        for othdoc in docids:
            try:
                # Calculate term frequency call trmdoc
                all_tf = all_tf + tfreq[othdoc][word]
                # Calculate document length
                all_ln = all_ln + doclen[othdoc]
            except KeyError:
                continue
        for docid in docids:
            try:
                # Calculate term frequency call trmdoc
                term_freq = tfreq[docid][word]
                # Calculate document length
                doc_len = doclen[docid]
                # Calucate corpus frequency
            except KeyError:
                #print word + " -> is absent"
                continue
            bckgrd = float(all_tf - term_freq) / (all_ln - doc_len)
            fregrd = float(term_freq) / doc_len
            ratio = fregrd / bckgrd
            # Calulate lamba
            lmbda = .4
            jlmscore = lmbda * fregrd + (1 - lmbda) * bckgrd
            if docid not in doctf:
                doctf[docid] = math.log1p(jlmscore)
            else:
                doctf[docid] = doctf[docid] + math.log1p(jlmscore)
    return doctf


def modelgen(elasrch, querymap, tfreq, dcfreq, doclen, modelname, filename):
    # Create and empry score file file
    scorefile = open(filename, 'w')
    scorefile.write("")
    scorefile.close()
    mymap = {}
    for qno in xrange(50, 101):
        if str(qno) in querymap:
            print qno
            # Assign the string of corresponding query number
            querystr = querymap[str(qno)]
            # Get the dictionary of docno -> score
            if modelname == "okapitf":
                myscore = okapitfcalc(elasrch, querystr, tfreq, doclen)
            elif modelname == "tfidf":
                myscore = tfidfcalc(elasrch, querystr, tfreq, dcfreq, doclen)
            elif modelname == "okapibm25":
                myscore = okapibm25calc(elasrch, querystr, tfreq, dcfreq, doclen)
            elif modelname == "lmlaplace":
                myscore = lmlaplacecalc(elasrch, querystr, tfreq, dcfreq, doclen)
            elif modelname == "jelinekmecer":
                myscore = jelinekmecercalc(elasrch, querystr, tfreq, dcfreq, doclen)
            # Get a list of tuple (value, key)
            myscore = sorted(myscore.items(), key=operator.itemgetter(1), reverse=True)
            # Get length and run the loop till 100 or lenght which is greater
            scorelength = len(myscore)
            # Check for matching document list size
            if scorelength < 1500:
                doc_count = scorelength
            else:
                doc_count = 1500
            # Print to output filename
            scorefile = open(filename, 'a')
            for itr in xrange(0, doc_count):
                value = str(qno) + " Q0 " + str(myscore[itr][0]) + " " + str(itr + 1) + " " + str(myscore[itr][1]) + " Exp\n"
                scorefile.write(value)
                mymap[len(mymap)] = value
            scorefile.close()

    # Final File
    scorefile = open('Trec-Text-long.txt', 'w')
    keys = list(mymap.keys())
    random.shuffle(keys)
    for key in keys:
        scorefile.write(mymap[key])
    scorefile.close()


def main():
    print "Main executed"
    docindex = open("docindex.json", 'r')
    input = json.load(docindex)
    tfreq = input['tfreq']
    dcfreq = input['dcfreq']
    doclen = input['doclen']
    #parsedocs(elasrch)
    # temp = search(elasrch, "agreement,")
    # print temp
    # docids = search(elasrch, "mci")
    # print docids
    #print trmfreq(elasrch, "AP890102-0003", "high")
    # print corpusfreq(elasrch, "AP890102-0003", "high")
    # print docfreq(elasrch, "AP890102-0003", "high")
    querymap = parsequery()
    # okapitfcalc(elasrch, querymap['60'])
    # modelgen(elasrch, querymap, tfreq, dcfreq, doclen, "okapitf", "OkapiTF.txt")
    modelgen(elasrch, querymap, tfreq, dcfreq, doclen, "tfidf", "TdfId.txt")
    # modelgen(elasrch, querymap, tfreq, dcfreq, doclen, "okapibm25", "OkapiBM25.txt")
    # modelgen(elasrch, querymap, tfreq, dcfreq, doclen, "lmlaplace", "LMlaplace.txt")
    # modelgen(elasrch, querymap, tfreq, dcfreq, doclen, "jelinekmecer", "JLKMCRlaplace.txt")
    # print avgdoclength(elasrch)

if __name__ == '__main__':
    main()
