from elasticsearch import Elasticsearch
from models import parsequery
import json
from stemming.porter import stem

# Create a elasticsearch object by connecting at localhost:9200
elasrch = Elasticsearch(
    "localhost:9200", timeout=600, max_retries=10, revival_delay=0)
# Declare variables, doc list, doc-text hash map, boolean var and empty string


def termindex(wordlist):
    result = elasrch.search(index='docset', doc_type="document", size=100000)
    # Make dict for docid -> term -> term frequency
    d_tfreq = {}
    # Make dict for docid -> doclen
    d_doclen = {}
    # Make dic for term -> doc, corpus frequency
    d_dcfreq = {}
    for doc in result['hits']['hits']:
        # Term vectors
        trmvec = elasrch.termvector(
            index='docset', doc_type="document", id=doc['_id'], term_statistics="true")
        # Doc length search
        docsize = elasrch.search(index='docset', doc_type="document", body={"query"
        :{"match":{"docno": doc['_id'] }}, "facets": {"text": {"statistical"
        : {"script": "doc['text'].values.size()"}}}})

        d_doclen[doc['_id']] = docsize['facets']['text']['total']
        # Make the dictionary to store word
        word = {}
        # print wordlist
        for term in wordlist:
            term = stem(term)
            # Initialize dictionary to store frequencies
            dcfreq = {}
            # Fetch term , document, corpus frequency
            try:
                term_freq = trmvec['term_vectors'][
                    'text']['terms'][term]['term_freq']
            except KeyError:
                term_freq = 0
                doc_freq = 0
                crp_freq = 0
                continue
            doc_freq = trmvec['term_vectors'][
                'text']['terms'][term]['doc_freq']
            # print doc_freq
            crp_freq = trmvec['term_vectors'][
                'text']['terms'][term]['ttf']
            # Capture all frequency
            if term_freq != 0:
                word[term] = term_freq
                dcfreq['doc_freq'] = doc_freq
                dcfreq['crp_freq'] = crp_freq
            # Add to dictionary
            if dcfreq:
                d_dcfreq[term] = dcfreq
        # Add word dict to docs dict
        if word:
            d_tfreq[doc['_id']] = word
    docindex = {}
    docindex['tfreq'] = d_tfreq
    docindex['dcfreq'] = d_dcfreq
    docindex['doclen'] = d_doclen
    with open('docindex.json', 'w') as outfile:
        json.dump(docindex, indent=3, separators=(',', ': '), fp=outfile)


def querysplit(querymap):
    words = []
    for num in querymap:
        words = words + querymap[num].split()
    return words


def main():
    querymap = parsequery()
    wordlist = querysplit(querymap)
    # for term in wordlist:
    #   print term
    termindex(wordlist)


if __name__ == '__main__':
    main()
