__author__ = 'nikhilk'
# Import the BeautifulSoup
from bs4 import BeautifulSoup

# import urllib request and parse
from urllib import request
from urllib import parse

# import robot
from urllib import robotparser

# import regex module
import re


def canonicalize(pdomain, pscheme, childurl):
    # Assign None to url and split baseurl and childurl
    url = None
    childcomp = parse.urlparse(childurl)
    # Check for hostname is
    if childcomp.netloc:
        # print(childcomp.netloc)
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
    # print(url)
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


def nexturls(url, response, domain, scheme):
    urllist = set()
    # Get header Info for attributes(content-type, content-language)
    # Accept content-type as text/* or message/*
    # print(response.info()['content-type'])
    # Get the returned URL by server
    # print(response.geturl())
    # URLError

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
            newlink = canonicalize(domain, scheme, childurl)
            if newlink:
                urllist.add(newlink)
        return urllist


def visible(element):
    if element.parent.name in ['b', 'p']:
        return True


def main():
    test()


def test():
    '''
    openfile = open('test.txt', 'r')
    # Read each line from the input file
    for line in openfile:
        # Strip new line char and spaces
        line = line.strip()
        try:
            response = request.urlopen(line, timeout=5)
            # print(response.info()['Content-language'])
            print(response.info())
            # text = soupobj.get_text().encode('ascii', 'ignore')
            soupobj = BeautifulSoup(response)
            # print(soupobj.original_encoding)
            # print(soupobj.title.text.strip())
            print(str(soupobj.encode('ascii', 'ignore').decode('ascii')).replace('\n', '').replace('\r',''))
            texts = soupobj.findAll(text=True)
            visible_texts = filter(visible, texts)
            text_var = ''
            for text in visible_texts:
                text_var = text_var + str(text.encode('ascii', 'ignore').decode('ascii'))
                text_var = re.sub('[^a-zA-Z-0-9.,:;?{}()'' ]', ' ', text_var)
                text = re.sub(' +', ' ', text_var)
            # print(text_var)
            # text = soupobj.get_text().replace("[^\\x00-\\x7F]", "")
            # clean = "".join(i for i in text if ord(i) < 128)
            # clean = clean.encode('ascii', 'ignore')
            # filename = open('temp.txt', 'w')
            # filename.write(assign)
            # print(soupobj.text)
            # Get the URL components
            basecomp = parse.urlparse(line)
            domain = basecomp.netloc.lower()
            scheme = basecomp.scheme.lower()
        except Exception as ex:
            print("Error in opening url -> " + str(ex))
            continue
        urls = nexturls(line, response, domain, scheme)
        # for url in urls:
        #   print(url)
    openfile.close()

    # now = parse.urlparse("//www.internet.com/")
    # print(now)

    # sub = refinepath("../asd/asdasd/../abc")
    # print(sub)'''
    pass

if __name__ == '__main__':
    main()
