from glob import glob
import re
import collections
import os
from sets import Set
import json
from stemming.porter import stem


def filenamedoccount():
    filelist = []
    # Add ap' + '*' to end to check for all
    for filename in glob('./AP_DATA/ap89_collection/ap' + '*'):
        count = 0
        openfile = open(filename)
        # Read each line from the input file
        for line in openfile:
            if re.match('<DOCNO>.+</DOCNO>', line):
                count += 1
        # Add a tupple (filename, Number of docid in file)
        filelist.append((filename, count))
    # File already sorted
    return filelist


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


def parsedocs(filename):
    # Define local variables
    doclist = []
    intext = False
    interimline = ""
    keymap = {}
    # Read all the files in glob
    # add /ap' + '*'
    for filename in glob(filename):
        openfile = open(filename)
        # Read each line from the input file
        for line in openfile:
            # Strip new line char and spaces
            # line = line.strip()
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
                text = textmod(interimline)
                keymap[docno] = text
                # Set interimline to empty string
                interimline = ""
            # Check for start text tag
            elif re.match('<TEXT>', line):
                intext = True
            elif re.match('</TEXT>', line):
                intext = False
            elif re.match('</DOC>', line):
                # Flush the docno value and interimline to hash table
                text = textmod(interimline)
                keymap[docno] = text
    return keymap


def processor():
    # Sets the limit for max documents to be checked
    docmax = 1000
    # Count of current docs present in memory
    doc_count = 0
    # A dict for docid -> id, counter, dict for id -> len, sumttf counter
    dmap = {}
    dcounter = 0
    dlen = {}
    sumttf = 0
    # Inverted index dictionary i.e. term -> DBLOCKS
    invidx = {}
    # Catalog dictionary i.e. term -> (offset, offset)
    catidx = {}
    # Call filenamedoccount for tuple list i.e. (filename, doc_count)
    filelist = filenamedoccount()
    stoplist = stopwordslist()
    # Iterate over all files in collection
    for itr in xrange(0, len(filelist)):
        print filelist[itr]
        # Check doc_count over threshold or not
        if doc_count + filelist[itr][1] >= docmax:
            print "Exceeded"
            # Call mergewrite for merging Current and InvIdx index
            catidx = mergewrite(catidx, invidx)
            # Doc count as zero and invidx re initialized
            doc_count = 0
            invidx = {}
        # Increment document counter
        doc_count = doc_count + filelist[itr][1]
        # Call parsedocs to fetch docid -> text map of all docs in file
        docs = parsedocs(filelist[itr][0])
        # Iterate over the docid -> text map
        for docid in docs:
            dcounter = dcounter + 1
            # Assign and increment the designated ID
            dmap[dcounter] = docid
            # Split doc in array and subtract stop words and stem each word
            trmary = stopandstem(docs[docid].split(), stoplist)
            # Store the length as doc lenth in dlen
            dlen[dcounter] = len(trmary)
            # termdic a dictionary to hold positions
            termdict = collections.defaultdict(list)
            # Iterate over all terms of document docidy
            for pos in xrange(0, len(trmary)):
                termdict[trmary[pos]].append(pos)
            # Now merge termdict with invidx
            for term in termdict:
                # Increment the sum ttf by one
                sumttf = sumttf + 1
                # Append the current docid and termlist as string
                dblock = str(dcounter) + ":" + listtostring(termdict[term])
                # When term not present in invidx then add term->dblock in dict
                # Otherwise update the invidx with new docs for term
                if term not in invidx:
                    invidx[term] = dblock
                else:
                    # print invidx[term]
                    invidx[term] = invidx[term] + "|" + dblock
    # Call to Merge the last invidx with HDD index
    if len(invidx) > 0:
        print "lastmerge"
        catidx = mergewrite(catidx, invidx)
    # Call postprocess to write vocab, sum_ttf
    postprocess(sumttf, len(catidx))
    # Call to dumpcatalog to dump catalog as json
    dumpcatalog(catidx)
    # Call to dump dlen dict i.e. id -> dlen
    dumpdoclen(dlen)
    # Call to dump dict i.e. docid -> id
    dumpdocid(dmap)


def mergewrite(catidx, invidx):
    # Extract keys from both catidx and invidx and make a set by doing union
    looplist = Set(invidx.keys()) | Set(catidx.keys())
    # Initialize new catalog dictionary
    # print len(catidx)
    catalog = {}
    # Dump contents when catidx is empty i.e. first merge
    if (not catidx):
        # Call firstmerge and return catalog after
        catalog = firstmerge(invidx)
        return catalog
    # Open old and new Index Files "Index.json" and InterimIndex.json
    indexfile = open("Index.txt", 'r')
    newfile = open("InterimIndex.txt", 'w')
    print len(looplist)
    # Loop length counter
    for term in looplist:
        if term in catidx:
            if term in invidx:
                # Call equalwrite
                catalog = equalwrite(indexfile, newfile, term, catidx, invidx, catalog)
            else:
                # Call bigwrite
                catalog = bigwrite(indexfile, newfile, term, catidx, catalog)
        else:
            # Call smallwrite
            catalog = smallwrite(newfile, term, invidx, catalog)
    # Close file handlers
    indexfile.close()
    newfile.close()
    # Replace the current Index.json with InterimIndex.json
    os.system("/bin/mv InterimIndex.txt Index.txt")
    # Return the new catalog
    return catalog


def firstmerge(invidx):
    # Initialize catalog dictionary
    catalog = {}
    # Open the indexfile for in write mode
    indexfile = open("Index.txt", 'w')
    print "firstmerge"
    # Proceed keys of dict
    for key in invidx:
        start = indexfile.tell()
        indexfile.write(invidx[key] + '\n')
        end = indexfile.tell()
        # Dump the term and offset in catalog
        catalog[key] = (start, end)
    # Close the file handler
    indexfile.close()
    # Return the catalog dict created
    return catalog


def equalwrite(ifile, nfile, term, cat, inv, ctl):
    # Go to byte offset location of Index.json
    ifile.seek(cat[term][0])
    # Read the inverted list from index.json
    invlist = ifile.read(cat[term][1] - cat[term][0])
    # Form a dblock by appending dblock with "|" delimter
    dblock = invlist.strip() + "|" + inv[term]
    # Store the current byte offset of new file
    start = nfile.tell()
    # Write the  new dblock fomred variable to file
    nfile.write(dblock + '\n')
    # Store the new byte offset
    end = nfile.tell()
    # Add the entry to new catalog dict i.e. term -> (start, end)
    ctl[term] = (start, end)
    return ctl


def smallwrite(nfile, term, inv, ctl):
    # Store the current byte offset, write and then againg store offset
    start = nfile.tell()
    nfile.write(inv[term] + '\n')
    end = nfile.tell()
    # Add the entry to new catalog dict i.e. term -> (start, end)
    ctl[term] = (start, end)
    return ctl


def bigwrite(ifile, nfile, term, cat, ctl):
    # Go to byte offset location denoted by first value
    ifile.seek(cat[term][0])
    # Read the inverted list from index.json
    invlist = ifile.read(cat[term][1] - cat[term][0])
    # Store the current byte offset, write and then againg store offset
    start = nfile.tell()
    nfile.write(invlist.strip() + '\n')
    end = nfile.tell()
    # Add the entry to new catalog dict i.e. term -> (start, end)
    ctl[term] = (start, end)
    return ctl


def listtostring(lst):
    final = ""
    for term in lst:
        final = final + str(term) + " "
    return final.strip()


def stopwordslist():
    # Create a list to store stopwords
    stoplist = []
    # Open the file
    openfile = open('stopwords.txt')
    # Read each line from the input file
    for line in openfile:
        # Strip new line char and spaces
        line = line.strip()
        # Append the word to list
        stoplist.append(line)
    return stoplist


def stopandstem(trmary, stoplist):
    nwtmary = []
    for term in trmary:
        if term in stoplist:
            continue
        else:
            nwtmary.append(stem(term))
    return nwtmary


def stemmer(lst):
    for itr in xrange(0, len(lst)):
        lst[itr] = stem(lst[itr])
    return lst


def postprocess(sumttf, vocab):
    stats = {}
    stats['sum_ttf'] = sumttf
    stats['vocab_size'] = vocab
    with open('statistics.json', 'w') as outfile:
        json.dump(stats, indent=1, separators=(',', ': '), fp=outfile)


def dumpcatalog(catidx):
    with open('catalog.json', 'w') as outfile:
        json.dump(catidx, indent=1, separators=(',', ': '), fp=outfile)


def dumpdoclen(dlen):
    with open('doclen.json', 'w') as outfile:
        json.dump(dlen, indent=1, separators=(',', ': '), fp=outfile)


def dumpdocid(dmap):
    with open('docid.json', 'w') as outfile:
        json.dump(dmap, indent=1, separators=(',', ': '), fp=outfile)


def readcatalog(ctlg):
    # Open file and load via json.load
    return json.load(open("ctlg", 'r'))


def main():
    processor()
    # filename = parsedocs('./AP_DATA/ap89_collection/ap891026')

    # print stopandstem(filename['AP891026-0274'].split(), stopwordslist())

    # with open('file.json', 'w') as outfile:
    #    json.dump(filename, indent=1, separators=(',', ': '), fp=outfile)
    # processor()
    # doc = parsedocs(filename[0][0])
    # print doc['AP890101-0059'].split()

if __name__ == '__main__':
    main()
