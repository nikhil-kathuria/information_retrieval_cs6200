from stemming.porter import stem
import collections
import os
import json



def main():
    text = 
    strr = "help:asd"
    print strr.split("|")
    dlendict = json.load(open("doclen.json", 'r'))
    diddict = json.load(open("docid.json", 'r'))
    catdict = json.load(open("catalog.json", 'r'))
    statdict = json.load(open("statistics.json", 'r'))

    getdoc(catdict, "mci")




def getdoc(catdict, term):
    ifile = open("Index.txt", 'r')
    ifile.seek(catdict[term][0])
    invlist = ifile.read(catdict[term][1] - catdict[term][0])
    dblocks = invlist.split("|")
    for block in dblocks:
        blkary = block.split(":")
        docid = blkary[0]
            # Calculate term frequency call trmdoc
        term_freq = len(blkary[1].split(" "))
        print term_freq
    ifile.close()

'''
    d = collections.OrderedDict()
    # d = {}
    d[12] = (43, 12)
    d[102] = (44, 32)
    d[49] = (11, 30)
    d[147] = (121, 87)
    l = len(d.keys())
    print l
    print "hello world\n".strip()

    for key in xrange(0, len(l)):
        print l[key]
    # print (invidxlist)
    # invidxlist.sort()
    # print invidxlist


    dic = collections.OrderedDict()
    dic[11] = "one"
    dic[34] = "two"
    dic[65] = "three"
    keys = dic.keys()
    print keys
    # Unordered
    udic  = {}
    udic[11] = "one"
    udic[34] = "two"
    udic[65] = "three"
    keys = udic.keys()
    print keys



                    if trmary[pos] in termdict:
                    termdict['trmary[pos]'].append(pos)
                else:
                    termdict[trmary[pos]] = termdict[trmary[pos]].append(pos)
'''

if __name__ == '__main__':
    main()
