# Import the System module
import sys
import math

# Set verbose flag as false
verbose = False

# Check the length of argumemnts
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print("Usage:  trec_eval [-q] <qrel_file> <trec_file>\n")
    exit()


# Check for first argument
if sys.argv[1] == "-q":
    verbose = True
    # Read the qrel_file
    try:
        qrel_file = open(sys.argv[2])
    except:
        print("Failed to open file QREL_FILE -> " + sys.argv[1])
        exit()
    # Read the file to be scored
    try:
        rank_file = open(sys.argv[3])
    except:
        print("Failed to open file INPUT_FILE -> " + sys.argv[2])
        exit()
else:
    # Read the qrel_file
    try:
        qrel_file = open(sys.argv[1])
    except:
        print("Failed to open file QREL_FILE -> " + sys.argv[0])
        exit()
    # Read the file to be scored
    try:
        rank_file = open(sys.argv[2])
    except:
        print("Failed to open file INPUT_FILE -> " + sys.argv[1])
        exit()


# Read the qrels file and keep in dict
try:
    qrel_dict = dict()
    for line in qrel_file:
        val = line.strip().split()
        # Check if Query is seen earlier if not then create new dict
        if val[0] not in qrel_dict:
            qrel_dict[val[0]] = {val[2]: int(val[3])}
            # print({val[2]: val[3]})
        # Else update the dictionary with new value
        else:
            # print(qrel_dict[val[0]])
            qrel_dict[val[0]].update({val[2]: int(val[3])})
            # qrel_dict[val[0]] = qrel_dict[val[0]].update({val[2]: val[3]})
except Exception as e:
    print(str(e))
    print("The qrel_file format is incorrect")
    exit()


# Read the input file and keep in dict
try:
    rank_dict = dict()
    for line in rank_file:
        val = line.strip().split()
        # Check if Query is seen earlier if not then create new dict
        if val[0] not in rank_dict:
            rank_dict[val[0]] = {val[2]: float(val[4])}
        # Else update the dictionary with new value
        else:
            rank_dict[val[0]].update({val[2]: float(val[4])})
except Exception as e:
    print(str(e))
    print("The input file format is incorrect")
    exit()


# Function to cacluate relevant documents in QREL File
def qu_rel(querydict, query):
    docseen = 0
    for query in querydict:
        # print(querydict[key])
        if int(querydict[query]) != 0:
            docseen += 1
    return docseen


'''Function to print Precision, Recall, F-Measure @ K
And to print Average Precision, R-Precision and nDCG
for current query'''


def printstat(num, atk, avgprec, rprec, ndcg):
    print("\nQuery id : " + str(num))
    print("@k\t" + "Precision " + "Recall " + "F-Measure")
    for key in sorted(atk.keys()):
        pr = "{0:.4f}".format(atk[key][0])
        if atk[key][1] == 0:
            rc = "{0:.4f}".format(0)
        else:
            rc = "{0:.4f}".format(atk[key][1])
        if float(pr) == 0 and float(rc) == 0:
            f1 = "{0:.4f}".format(0)
        else:
            f1 = "{0:.4f}".format((2 * float(pr) * float(rc)) / (float(pr) + float(rc)))
        print(str(key) + "\t" + pr + "\t" + rc + "\t" + f1)
    print("Average Precision of Query is : \t" + "{0:.4f}".format(avgprec))
    print("R Precision of Query is : \t\t" + "{0:.4f}".format(rprec))
    print("nDCG value of Query is : \t\t" + "{0:.4f}".format(ndcg))
    print("\n")
    atk.clear()


'''Calculate the ndcg value by operating over list of grade values
and divding the result of above operationg by perfoming calulation
over sorted list'''


def ndcgcalc(dcglist):
    dcgscore = dcglist[0]
    for itr in range(1, len(dcglist)):
        dcgscore = dcgscore + dcglist[itr] / math.log(itr + 1, 2)
    # Sort the dcglist in Descending order
    dcglist.sort(reverse=True)
    dcgsorted = dcglist[0]
    for itr in range(1, len(dcglist)):
        dcgsorted = dcgsorted + dcglist[itr] / math.log(itr + 1, 2)
    dcglist.clear()
    if dcgsorted == 0:
        return dcgscore
    else:
        return dcgscore / dcgsorted


# The array for printing  precision at doc intervals
intervals = [5, 10, 15, 20, 50, 100, 200, 500, 1000]
# Global docseen for retrieved docs
relretdict = dict()
reldict = dict()
# Dict for storing avg precision
avgprec = dict()

# Retrieved docs dict as queryno -> count of retrieved docs
retrvdict = dict()

# R Precision dict queryno -> R precision value
rprecdict = dict()

# atk dict to store tuple (prec@k ,relret)
atk = dict()

# dcg list containing relvant grade(0 1 2) or 0
dcglist = list()
ndcgdict = dict()


''' Start processing each query from QREL, check if they are in
in document file.'''
for queryno in sorted(qrel_dict):
    # Get the docs and corresponding score for a query
    if queryno in rank_dict:
        docsdict = rank_dict[queryno]
    else:
        continue
    # Sort dict on score and output as tuple (docid, score)
    sorteddocs = sorted(docsdict.items(), key=lambda x: x[1], reverse=True)
    # Fetch query DocID -> Score dict for query
    querydict = qrel_dict[queryno]
    docseen = float(0)
    relret = float(0)
    avgprecsum = float(0)
    dcgscore = float(0)
    grade = float(0)
    # Fetch all the relevant docs as count from qrel file of query
    reldict[queryno] = qu_rel(querydict, queryno)
    # Skip the query if no relevant docs fond in qrel
    if reldict[queryno] == 0:
        print("No relevant document found in qrel. Skiping Query")
        continue
    # Traverse over the sorted list having (score, docid) tuple
    for scoredoc in sorteddocs:
        # Break in case we have seen 1000 documents
        if docseen >= 1000:
            break
        docseen += 1
        # If retrieved and relevant
        if scoredoc[0] in querydict and querydict[scoredoc[0]] != 0:
            # print(scoredoc[0])
            relret += 1
            grade = querydict[scoredoc[0]]
            # Calculate precision @ K till now
            avgprecsum = avgprecsum + (relret / docseen)
            # print(docseen)
        # Store the R Precision where Recall and Precision value matches
        if docseen == reldict[queryno]:
            rprecdict[queryno] = relret / docseen
        # If current docseen equals k i.e. 5 10 15 20...
        if docseen in intervals:
            falseneg = reldict[queryno] - relret
            recall = relret / (relret + falseneg)
            atk[docseen] = (relret / docseen, recall)
        # Accumulate the grade for ndcg calc
        dcglist.append(grade)
        grade = float(0)
    # Store Relevant and Retrieved in dict
    relretdict[queryno] = relret
    # Calculate Avg score as with Recall and precision value
    avgprec[queryno] = avgprecsum / reldict[queryno]
    # print("Query NO " + str(queryno) + " has rel " + str(reldict[queryno]))
    retrvdict[queryno] = len(sorteddocs)
    # Calculate and store dcg value for query
    ndcgdict[queryno] = ndcgcalc(dcglist)
    if verbose:
        printstat(queryno, atk, avgprec[queryno], rprecdict[queryno], ndcgdict[queryno])


print("")
print("Total Queries \t" + str(len(relretdict)))
print("Total number of documents over all queries")

# Calculate Total retrieved docs
totalret = 0
for key in retrvdict:
    totalret = totalret + retrvdict[key]
print("\tRetrieved: " + str(totalret))

# Calculate Total relevant docs
totalrel = 0
for key in reldict:
    totalrel = totalrel + reldict[key]
print("\tRelevant: " + str(totalrel))

# Calculate Relevant retrieved i.e. True positives
totalrelret = 0
for key in relretdict:
    totalrelret = totalrelret + relretdict[key]
print("\tRel_ret: " + str(int(totalrelret)))

# Print avg precision at each query and total avg precision
total = 0
for key in avgprec:
    total = total + avgprec[key]
# Calculate and print total avg precision for all queries
totalavg = total / len(avgprec)
print("Average precision (non-interpolated) for all rel docs(averaged over queries)")
print("\t\t" + "{0:.4f}".format(totalavg))


# Variable to store total fetched and total relevant for all queries
globrprec = 0
# Print recall precision at each query and total avg precision
for key in rprecdict:
    globrprec = globrprec + rprecdict[key]
print("R-Precision (precision after R (= num_rel for a query) docs retrieved))")
print("Exact : " + "\t" + "{0:.4f}".format(float(globrprec) / len(rprecdict)))


# Variable to store total fetched and total relevant for all queries
globndcg = 0
# Print recall precision at each query and total avg precision
for key in ndcgdict:
    globndcg = globndcg + ndcgdict[key]
totalavg = globndcg / len(ndcgdict)
print("nDCG average over all queries is ")
print("\t\t" + "{0:.4f}".format(totalavg))
