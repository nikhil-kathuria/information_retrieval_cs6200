
import time
from glob import glob

import heapq

from collections import defaultdict

# import robot
from urllib import robotparser
import sys

from elasticsearch import Elasticsearch
elasrch = Elasticsearch(
    "localhost:9200", timeout=600, max_retries=10, revival_delay=0)


def parent():
    l1 = [2, 3, 4, 5, 7, 8]
    outlink = defaultdict(list)
    outlink[1] = l1
    child(outlink)
    print(outlink)


def child(d):
    l2 = [5, 8, 9]
    d[2] = l2


def main():
    se = set([3, 4])
    ne = set(["Hello", "how", "are"])
    a = 1
    se = se | {a}
    line = "<OUTLINKS><OUTLINKS>"
    te = line.split('</OUTLINKS>')[0].split('<OUTLINKS>')[0]
    print(te)
    az = ','.join(ne)
    print(az)


def call(l1):
    heapq.heapify(l1)
    print(len(l1))


if __name__ == '__main__':
    main()


'''
dict = AttrDict({
            # do we need to follow HTTP redirects?
            'follow_redirects': True,
            # scores should we append to all links?
            'append_to_links': '',
            # scores page links do we need to parse?
            'valid_links': ['(.*)'],
            # scores URLs must be excluded
            'exclude_links': [],
            # scores is an entry point for crawler?
            'start_page': '/',
            # which domain should we parse?
            'domain': '',
            # should we ignor pages outside of the given domain?
            'stay_in_domain': True,
            # which protocol do we need to use?
            'protocol': 'http://',
            # autostart crawler right after initialization?
            'autostart': False,
            # cookies to be added to each request
            'cookies': {},
            # custom headers to be added to each request
            'headers': {},
            # precrawl function to execute
            'precrawl': None,
            # postcrawl fucntion to execute
            'postcrawl': None,
            # custom callbacks list
            'callbacks': {}
        })'''
