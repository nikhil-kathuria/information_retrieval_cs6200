# Import the priority queue module
import heapq

# Import from fetchurl.py
from fetchurl import canonicalize
from fetchurl import nexturls

# Import the BeautifulSoup
from bs4 import BeautifulSoup

# Import defaultdict for list as value
from collections import defaultdict

# Import time module for timestamp and sleep
import time

# import urllib request and parse
from urllib import request
from urllib import parse
from urllib import robotparser

# import regex module
import re

# import glob module
# import json
from glob import glob


def getinitialseed():
    seedlist = list()
    openfile = open('seedfile.txt', 'r')
    # Read each line from the input file
    itr = 0
    for line in openfile:
        # Strip new line char and spaces
        line = line.strip()
        # Append the word to list
        line = canonicalize(None, None, line)
        seedlist.append((itr, line))
        itr += 1
    openfile.close()
    return seedlist


def getresponse(response):
    flagtyp = False
    flaglng = False
    # print(response.info())
    typ = response.info()['Content-Type']
    lng = response.info()['Content-language']
    if typ is None or re.match('html|text', typ):
        flagtyp = True
    if lng is None or re.match('en', lng):
        flaglng = True
    # Return true only when both flags are true
    if flagtyp and flaglng:
        return True
    else:
        return False


def robotblock(scheme, domain, url):
    rp = robotparser.RobotFileParser()
    rp.set_url(scheme + "://" + domain + "/robots.txt")
    try:
        rp.read()
    except:
        # robots.txt missing
        return False
    return rp.can_fetch('*', url)


def dumpinlink(inlink):
    # Open file
    inlinkfile = open('./web-data/inlinks.txt', 'w')
    for link in inlink:
        links = inlink[link]
        inlinkstr = ""
        for each in links:
            inlinkstr = inlinkstr + "\t" + inlinkstr
        inlinkfile.write(link + "\t" + inlinkstr.strip() + "\n")
    # Close the file
    inlinkfile.close()


'''
def filtertag(element):
    if element.parent.name in ['style', 'script', 'document', 'head', 'title']:
        return False
    elif element.name in ['style', 'script', 'document', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    elif re.match('\n', str(element)):
        return False
    else:
        return True

'''


def filtertag(element):
    if element.parent.name in ['b', 'p']:
        return True


def gettext(texts):
    available_text = filter(filtertag, texts)
    txt = ''
    # Get all text available
    for text in available_text:
        txt = txt + str(text.encode('ascii', 'ignore').decode('ascii'))
    # Replace non meaningful chars
    # txt = re.sub('[^a-zA-Z-0-9.,:;?@$&!{}()/'' ]', ' ', txt)
    txt = re.sub(' +', ' ', txt)
    return txt.strip()


def dumpall(outlink, urlresponse):
    # Form file number via File
    fname = (len(glob('./web-data/*')))
    filename = './web-data/' + str(fname) + ".txt"
    outlinkfile = open(filename, 'w')
    for link in outlink:
        # Assign variables
        links = outlink[link]
        outlinkstr = ""
        head = ""
        html = ""
        text = ""
        header = ""
        response = urlresponse[link]
        # Write Doc Docno tags
        outlinkfile.write('<DOC>' + "\n")
        outlinkfile.write('<DOCNO>' + link + '</DOCNO>' + "\n")
        soupobj = BeautifulSoup(urlresponse[link])
        header = str(response.info()).replace('\n', '').replace('\r', '')
        if soupobj:
            if soupobj.title:
                head = soupobj.title.text.strip()
            elif soupobj.head:
                head = soupobj.head.text.strip()
            # Get Visible text and get HTML page in single String Line
            text = gettext(soupobj.findAll(text=True))
            page = str(soupobj.encode('ascii', 'ignore').decode('ascii'))
            html = page.replace('\n', '').replace('\r', '')
        # Write Head, Http-header, text, raw-html, outlinks, and /doc tag
        outlinkfile.write('<HEAD>' + head + '</HEAD>' + "\n")
        outlinkfile.write('<HTTP-HEADER>' + header + '</HTTP-HEADER>' + "\n")
        outlinkfile.write('<TEXT>' + text + '</TEXT>' + "\n")
        outlinkfile.write('<RAW-HTML>' + html + '</RAW-HTML>' + "\n")
        for each in links:
            outlinkstr = outlinkstr + "," + each
        outlinkfile.write('<OUTLINKS>' + outlinkstr.strip(',') + '</OUTLINKS>\n')
        outlinkfile.write('</DOC>' + "\n")
    outlinkfile.close()
    outlink.clear()
    urlresponse.clear()


def crawlwave(inlink, current, timedict, urlparsed):
    future = set()
    outlink = defaultdict(list)
    urlresponse = {}
    length = len(current)
    # process the elements of current frontier
    while current:
        url = heapq.heappop(current)[1]
        print(url)
        # Check if url has been crawled earlier, if so skip
        if url in urlparsed:
            continue
        try:
            response = request.urlopen(url, timeout=5)
            # Get the URL components
            basecomp = parse.urlparse(url)
            domain = basecomp.netloc.lower()
            scheme = basecomp.scheme.lower()
        except Exception as ex:
            print("Error in opening url ->  " + str(ex))
            continue
        # Check for valid content and langaue from response.info method
        if not robotblock(scheme, domain, url):
            continue
        if not getresponse(response):
            continue
        # Check last call to domain
        #urls = nexturls(url, response, domain, scheme)
        if domain not in timedict:
            timedict[domain] = time.time()
            urls = nexturls(url, response, domain, scheme)
        else:
            if (time.time() - timedict[domain]) < 1:
                print("Sleeping for " + str((time.time() - timedict[domain])))
                time.sleep(time.time() - timedict[domain])
                urls = nexturls(url, response, domain, scheme)
            else:
                timedict[domain] = time.time()
                urls = nexturls(url, response, domain, scheme)
        # Add in urlseen i.e all urls discovered
        urlparsed = urlparsed | {url}
        future = future | urls
        # Feed urls in outlink dict
        urls = list(urls)
        outlink[url] = urls
        urlresponse[url] = response
        # Check for inlink of previous url by matching
        for link in urls:
            if link in urlparsed:
                inlink[url].append(link)
        # If Heapq 70 % empty and not initial seeds, then break loop
        if (len(current) / length) < .3 and len(current) > 3:
            dumpall(outlink, urlresponse)
            break  
        # Dump outlinks and data if multiple of 100 reached.
        if (len(urlparsed) % 100) == 0:
            dumpall(outlink, urlresponse)
        # Dump inlinks when specified limit has reached
        elif len(urlparsed) > 12000:
            dumpinlink(inlink)
            exit()
    return future


def preparefrontier(future, inlink):
    # Initialize occurence of domain in frontier
    occourdict = {}
    current = list()
    totalurl = len(future)
    # Get occurence as Domain -> Occurence dict
    for link in future:
        comp = parse.urlparse(link)
        domain = comp.netloc.lower()
        if domain in occourdict:
            occourdict[domain] += 1
        else:
            occourdict[domain] = 1
    # Now calculate a score for each link
    for link in future:
        comp = parse.urlparse(link)
        domain = comp.netloc.lower()
        rarity = occourdict[domain] / totalurl
        '''We will reward rare document and document with high inlink
        Since the heapq works on popping the element based on rank/priority
        we score accordingly i.e. multiply by rarity and divide by inlink
        i.e. most prestige gets lowest score to imitate ranking'''
        if link in inlink:
            score = float(1 * rarity) / len(inlink[link])
        else:
            score = float(1 * rarity)
        current.append((score, link))
    # Make heap priority queue and return
    heapq.heapify(current)
    return current


def frontiercall():
    # Initialize the current frontier, inlinks and outlinks dict
    inlink = defaultdict(list)
    frontier = getinitialseed()
    # Initialize domain -> timestamp dictionary, url seen
    timedict = {}
    urlparsed = set()
    while True:
        future = crawlwave(inlink, frontier, timedict, urlparsed)
        frontier = preparefrontier(future, inlink)


def main():
    frontiercall()

if __name__ == '__main__':
    main()
