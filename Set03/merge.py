from elasticsearch import Elasticsearch
from glob import glob


elasrch = Elasticsearch(
    "localhost:9200", timeout=600, max_retries=10, revival_delay=0)


def parseinlinks():
    inlinkdict = dict()
    inlinkfile = open('./web-data/inlinks.txt', 'r')
    for line in inlinkfile:
        inlist = line.split('\t')
        inlinks = ""
        for itr in range(1, len(inlist)):
            inlinks = inlinks + "," + inlist[itr]
        inlinkdict[inlist[0]] = inlinks.strip(',')
    inlinkfile.close()
    return inlinkdict


def process(elasrch):
    inlinkdict = parseinlinks()
    linecount = 0
    for filename in glob('./web-data/'):
        openfile = open(filename, encoding='utf-8')
        # Read each line from the input file
        for line in openfile:
            linecount = linecount + 1
            # Check for line number
            # print(linecount % 8)
            if (linecount % 8) == 2:
                url = line.split('<DOCNO>')[1].split('</DOCNO>')[0]
            elif (linecount % 8) == 3:
                head = line.split('<HEAD>')[1].split('</HEAD>')[0]
            elif (linecount % 8) == 4:
                header = line.split(
                    '<HTTP-HEADER>')[1].split('</HTTP-HEADER>')[0]
            elif (linecount % 8) == 5:
                text = line.split('<TEXT>')[1].split('</TEXT>')[0]
            elif (linecount % 8) == 6:
                raw = line.split('<RAW-HTML>')[1].split('</RAW-HTML>')[0]
            elif (linecount % 8) == 7:
                out = line.split('</OUTLINKS>')[0].split('<OUTLINKS>')[0]
            elif (linecount % 8) == 0:
                result = elasrch.search(index='webcrawler', doc_type='document', body={"query": {"match": {"docno": url}}})
                # Check for presence of document in INDEX
                if len(result['hits']['hits']) > 0:
                    oldlinks = result['hits']['hits'][0]['_source']['inlinks']
                    if url in inlinkdict:
                        inlinks = inlinkdict[url]
                        inlinks = set(inlinks)
                        oldlinks = set(oldlinks.split(','))
                        # Union of new inlinks and oldlinks
                        newlinks = inlinks | oldlinks
                        newlinks = ','.join(newlinks)
                    # If no inlinks available with us
                    else:
                        newlinks = oldlinks
                # If the document does not exist in Index already
                else:
                    newlinks = inlinkdict[url]
                # Form the DBlock object to be inseted as body of url
                dblock = {"docno": url, "head": head, "text": text, "rawhtml": raw, "headers": header, "inlinks": newlinks, "outlinks": out}
                elasrch.index(index='webcrawler', doc_type='document', id=url, body=dblock)
    openfile.close()


def main():
    process(elasrch)
    pass


if __name__ == '__main__':
    main()
