# Import the System module
import sys
import math
import collections


def otherpr(outcount, outlist, oldscore):
    score = 0
    for link in outlist:
        if (link not in outcount) or (outcount[link]) == 0:
            continue
        else:
            score = score + oldscore[link] / outcount[link]
    return score


def getoutcount(linkdict):
    outlinks = collections.defaultdict(list)
    for source in linkdict:
        for dest in linkdict[source]:
            outlinks[dest].append(source)
    # Return dict Source ->  Oucount
    return dict((k, len(v)) for k, v in outlinks.items())


def calcpr(linkdict):
    # Damping factor as .85 and epsilon
    dampfact = .85
    epsilon = .001
    # Assign score of 1 to each url for pagerank as oldscore
    oldscore = dict((k, 1) for k in linkdict.keys())
    # Assign score of 0 to each url for pagerank as newsocre
    newscore = dict((k, 0) for k in linkdict.keys())
    # Create a outlink count for each link
    outcount = getoutcount(linkdict)
    print(len(outcount))
    # print(outcount['WT01-B01-47'])
    # Get the list of links for page rank to be calulated
    links = list(linkdict.keys())
    counter = 0
    while len(links) > 0:
        print(len(links))
        for score in links:
            if math.fabs(oldscore[score] - newscore[score]) < epsilon:
                links.remove(score)
            else:
                # Assingn the old score the current value
                oldscore[score] = newscore[score]
                constant = 1 - dampfact
                varyscore = dampfact * otherpr(outcount, linkdict[score], oldscore)
                newscore[score] = constant + varyscore
        # print("Done")
        counter += 1
        if counter > 1000000:
            print("Breaking at million walks")
            break
    print("Page rank computed with damping factor " + str(dampfact))
    print(" And with converging epsilon as " + str(epsilon))
    return newscore


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
    print(len(linkdict))
    prscore = calcpr(linkdict)
    print("\nTop 50 pages by page-rank:")
    prsorted = sorted(prscore.items(), key=lambda x: x[1], reverse=True)
    for itr in prsorted[:50]:
        print(itr[0], "\t", itr[1])
    outlinkfile = open(filename, 'w')

def main():
    # Check the length of argumemnts
    if len(sys.argv) != 2:
        print("Usage: python Page_Rank.py <LinkGraphFile>\n")
        exit()
    creatematrix()
    pass

if __name__ == '__main__':
    main()
