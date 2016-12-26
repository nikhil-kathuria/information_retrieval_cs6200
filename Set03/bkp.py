__author__ = 'nikhilk'
# Import the
from bs4 import BeautifulSoup
#import urlparse
from urllib import request
from urllib import parse
# import regex
import re


def canonical_url(pdomain, pscheme ,childurl):
    # Assign None to url and split baseurl and childurl
    url = None
    childcomp = parse.urlparse(childurl)
    # Check for hostname is
    if childcomp.netloc:
        if childcomp.port == "80" or childcomp.port == "443":
            domain = childcomp.netloc.split(':')[0].lower()
        else:
            domain = childcomp.netloc.lower()
        if childcomp.path and not childcomp.path.startswith('#'):
            path = refinepath(childcomp.path)
            if childcomp.scheme:
                scheme = childcomp.scheme.lower()
                url = scheme + "://" + domain + path
            # Added http as per discussion with team
            else:
                url = "http://" + domain + path
    else:
        if childcomp.path and not childcomp.path.startswith('#'):
            path = refinepath(childcomp.path)
            url = pscheme + "://" + pdomain + path
    return url
    pass


def refinepath(path):
    # Make to absolute path if relative
    path = re.sub('\.\./', '/', path)
    # Replace multiple occurence of / with single /
    path = re.sub('//+', '/', path)
    # In case path is /
    if path == "/":
        path = ""
    # In case path does not start with /
    elif (not path.startswith("/")) and (not path == ""):
        path = "/" + path
    return path


def process1url(url):
    urllist = set()
    # fetch URL content
    try:
        response = request.urlopen(url)
    # Get the URL components
        basecomp = parse.urlparse(url)
        print(basecomp)
        domain = basecomp.netloc.lower()
        scheme = basecomp.scheme.lower()
    except:
        print("Error in opening url -> " + url)
    # Get header Info for attributes(content-type, content-language)
    # Accept content-type as text/* or message/*
    # print(response.info()['content-type'])
    # Get the returned URL by server
    # print(response.geturl())

    # Save html in html String variable
    # html = response.read()
    # print(html)
    soupobj = BeautifulSoup(response, from_encoding='utf-8')
    if soupobj:
        for link in soupobj.find_all('a'):
            href = link.get('href')
            if href is None:
                continue
            else:
                childurl = href.strip()
            newlink = canonical_url(domain, scheme, childurl)
            if newlink:
                urllist.add(newlink)
                print(newlink)
        return urllist




def main():
    # list1 = process1url("http://www.theguardian.com/environment/2015/mar/26/climate-change-farmers-urge-coalition-to-restore-emissions-trading-scheme")
    # list1 = process1url('http://www.epa.gov/climatechange/science/future.html')
    list1 = process1url("http://en.wikipedia.org/wiki/Climate_change")
    print(len(list1))
    # now = parse.urlparse("//www.internet.com/")
    # print(now)
    
    # sub = refinepath("../asd/asdasd/../abc")
    # print(sub)

if __name__ == '__main__':
    main()
