# Import the System module
import sys
import math
import collections


def otherpr(outcount, inlist, newscore):
    score = 0
    for link in inlist:
        score = score + float(newscore[link]) / outcount[link]
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
    epsilon = .000001
    # Assign score of 1 to each url for pagerank as newsocre
    newscore = dict((k, float(1)) for k in linkdict.keys())
    # Create a outlink count for each link
    outcount = getoutcount(linkdict)
    print("Outlink sources " + str(len(outcount)))
    # Get the list of links for page rank to be calulated
    links = list(linkdict.keys())
    # Set couter for total ierations and flag as True
    counter = 0
    flag = True
    while flag:
        for link in links:
            flag = False
            # Assingn the old score the current value
            oldvalue = newscore[link]
            constant = 1 - dampfact
            varyscore = dampfact * otherpr(outcount, linkdict[link], newscore)
            score = constant + varyscore
            # If any value has not converged then set flag as True
            if math.fabs(score - oldvalue) > epsilon:
                flag = True
                newscore[link] = score
            else:
                newscore[link] = score
        counter += 1
        print("At iteration " + str(counter))
        if counter > 1000000:
            print("Breaking at million walks")
            break
    print("Page rank computed with damping factor " + str(dampfact))
    print("And with converging epsilon as " + str(epsilon))
    return newscore


def gengraph():
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
    print("Inlink sources " + str(len(linkdict)))
    prscore = calcpr(linkdict)
    # Print top 50 pages by page rank
    print("\nTop 50 pages by page-rank:")
    prsorted = sorted(prscore.items(), key=lambda x: x[1], reverse=True)
    for itr in prsorted[:1000]:
        print itr[0] ,  itr[1] ,  len(linkdict[itr[0]])
    # Dump the output to the file
    outlinkfile = open("PageRankFile.txt", 'w')
    sumpr = float(0)
    for itr in range(0, len(prsorted)):
        outlinkfile.write(str(prsorted[itr][0]) + '\t' + str(prsorted[itr][1]) + "\n")
        sumpr = sumpr + prsorted[itr][1]
    print("Average Page Rank of all documents " + str(sumpr / len(prsorted)))
    outlinkfile.close()


def main():
    # Check the length of argumemnts
    if len(sys.argv) != 2:
        print("Usage: python Page_Rank.py <LinkGraphFile>\n")
        exit()
    gengraph()
    pass

if __name__ == '__main__':
    main()
