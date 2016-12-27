# Import the System module
import sys
import math
import collections

import numpy as np
# from scipy.linalg import eig


def getoutgraph(linkdict):
    outlinks = collections.defaultdict(list)
    for source in linkdict:
        for dest in linkdict[source]:
            outlinks[dest].append(source)
    # Return dict Source ->  Oucount
    return outlinks


def calcpr(linkdict):
    # Create a outlink count for each link
    outgraph = getoutgraph(linkdict)
    outlnk = outgraph.keys()
    inlnk = linkdict.keys()
    links = list(outlnk | inlnk)
    # Initialized a N*N transition matrix with default val as Zero
    tranmat = np.zeros([len(links), len(links)], dtype=float)
    print(len(links))
    for itri in range(0, len(links)):
        if links[itri] in outgraph:
            print(str(itri))
            # print(outgraph[links[itri]])
            length = len(outgraph[links[itri]])
            # Fetch all the index positions of the outlinks as per out list
            indexlist = [links.index(val) for val in outgraph[links[itri]]]
            # print(indexlist)
            for itrj in range(0, len(links)):
                if itrj in indexlist:
                    tranmat[itri][itrj] = 1 / length
    print("Performing eigen vector")
    # Now calculate Eigen Vector
    v, V = np.linalg.eig(tranmat.T)
    left_vec = V[:, 0].T
    # Get the vector sorted
    # left_vec = V[:, v.argmax()]
    # Normailize (i.e sum of all ranks = 1)
    left_vec /= left_vec.sum()
    return left_vec


def creatematrix():
    try:
        link_file = open(sys.argv[1])
    except:
        print("Failed to open file LinkGraph File -> " + sys.argv[1])
        exit()
    linkdict = dict()
    # Parse the link graph and storing in dict link -> outlinks
    for line in link_file:
        linkarray = line.split()
        link = linkarray[0]
        del linkarray[0]
        linkdict[link] = set(linkarray)
    prscore = calcpr(linkdict)
    print("\nTop 50 pages by page-rank:")
    prsorted = sorted(prscore.items(), key=lambda x: x[1], reverse=True)
    for itr in prsorted[:50]:
        print(itr[0], "\t", itr[1])


def main():
    # Check the length of argumemnts
    if len(sys.argv) != 2:
        print("Usage: python Page_Rank.py <LinkGraphFile>\n")
        exit()
    creatematrix()
    pass

if __name__ == '__main__':
    main()