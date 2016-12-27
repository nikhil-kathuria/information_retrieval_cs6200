from time import time
from parseap89 import parsedocs
from clustercheck import ClusterCheck


from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.cluster import KMeans
#from sklearn.cluster import DBSCAN


from elasticsearch import Elasticsearch
from collections import defaultdict



class Data:
    def __init__(self, query):
        self._es = Elasticsearch(
        "localhost:9200", timeout=600, max_retries=10, revival_delay=0)
        self._pp = "/Users/nikhilk/Documents/NEU_MSCS/IR/Set08/scores/"
        self._qp = "/Users/nikhilk/Documents/NEU_MSCS/IR/Set04/qrels.adhoc.51-100.AP89.txt"
        self._query = query


    def querygen(self):
        qset = set()
        fileloc = "../Set01/AP_DATA/query_desc.51-100.short.txt"
        qfile = open(fileloc)
        for line in qfile:
            qset.add(line.split('.')[0])
        qfile.close()
        return qset


    def all_qrel(self):
        qset = self.querygen()

        fobj = open(self._qp, 'r')
        dlist = set()
        for line in fobj:
            arr = line.split()
            if arr[0] in qset and arr[3] != "0":
                dlist.add(arr[2])

        self._dlist = list(dlist)
        fobj.close()



    def score(self):
        fpath = self._pp + "bm25_results"
        fobj = open(fpath, 'r')

        dlist = list()
        for line in fobj:
            arr = line.split()
            if arr[0] ==  self._query:
                dlist.append(arr[2])

        self._dlist = dlist

    def qrel(self):
        fobj = open(self._qp, 'r')
        dlist = list()
        for line in fobj:
            arr = line.split()
            if arr[0] ==  self._query and arr[3] != "0":
                dlist.append(arr[2])

        self._dlist = dlist
        fobj.close()



    def getmap(self):
        docmap = dict()
        for docid in self._dlist:
            #self._es.search(index='ap_89', doc_type="document", body={"query" :{"match":{"docno": docid }}})
            result = self._es.get('ap_89', docid, doc_type="document")

            if "_source" in result and len(result['_source']['text']) > 0:
                docmap[docid] = result['_source']['text'].lower()

        return docmap

    def getall(self):
        docmap = {}
        result = self._es.search(index='ap_89', doc_type="document", size=100000)
        for doc in result['hits']['hits']:
            docid = doc['_id']
            doc = self._es.get('ap_89', docid, doc_type="document")

            if "_source" in doc and len(doc['_source']['text']) > 0:
                docmap[docid] = doc['_source']['text'].lower()
            print(docid)
        return docmap





class LDA:
    def __init__(self, docmap, maxfeatures, numtopics):
        self._docmap = docmap
        self._maxfeatures = maxfeatures
        self._numtopics = numtopics
        self._numwords = 10


    def train(self):
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2,
                                        max_features=self._maxfeatures, stop_words='english')
        tf = tf_vectorizer.fit_transform(self._docmap.values())

        lda = LatentDirichletAllocation(n_topics=self._numtopics, max_iter=25,
                                learning_method='online', learning_offset=50.,
                                random_state=0)
        lda.fit(tf)
        tf_feature_names = tf_vectorizer.get_feature_names()

        # Get Topic words for each topic
        top_t = self.top_topic(lda, tf_feature_names, self._numwords)

        # Get topic for each doc in sorted order
        doc_t = [row.argsort() for row in lda.transform(tf)]

        self.printstats(top_t, doc_t, tf_feature_names, 3)


    def trainall(self):
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=10,
                                        max_features=self._maxfeatures, stop_words='english')
        tf = tf_vectorizer.fit_transform(self._docmap.values())

        lda = LatentDirichletAllocation(n_topics=self._numtopics, max_iter=15,
                                learning_method='online', learning_offset=50.,
                                random_state=0)
        lda.fit(tf)

        # Get topic for each doc in sorted order
        return lda.transform(tf)


    def kMeansSort(self, mat, nc):
        km = KMeans(n_clusters=nc, precompute_distances=True, max_iter=500, copy_x=True)
        km.fit_predict(mat)
        clusters = km.predict(mat)
        distances = km.transform(mat)

        docids = self._docmap.keys()
        mymap = defaultdict(list)

        for idx, row in enumerate(distances):
            cid = clusters[idx]
            mymap[cid].append((idx, row[cid]))

        for key in mymap:
            unsorted = mymap[key]
            unsorted.sort(key=lambda tup: tup[1])
            pstring = " ".join(docids[tup[0]] for tup in unsorted)
            print("Cluster " + str(key) + " -> " + pstring)


    def KMeans(self, mat, nc):
        km = KMeans(n_clusters=nc, precompute_distances=True, max_iter=500, copy_x=True)
        km.fit_predict(mat)
        clusters = km.predict(mat)
        return dict(zip(self._docmap.keys(), clusters))




    def accCluster(self, cc, doc_cluster):
        sqsc, sqdf, dqsc, dqdc = 0, 0, 0, 0

        for pair in cc._pairlist:
            d1 = pair[0]
            d2 = pair[1]

            c1 = doc_cluster[d1]
            c2 = doc_cluster[d2]

            q1 = cc._dqmap[d1]
            q2 = cc._dqmap[d2]

            if len(q1.intersection(q2)) > 0:
                if c1 == c2:
                    sqsc += 1
                else:
                    sqdf += 1
            else:
                if c1 == c2:
                    dqsc += 1
                else:
                    dqdc += 1


        print("Same Query & Same Cluster -> " + str(sqsc))
        print("Same Query & Different Cluster -> " + str(sqdf))
        print("Different Query & Same Cluster -> " + str(dqsc))
        print("Different Query & Different Cluster -> " + str(dqdc))

        acc = float(sqsc + dqdc) / (sqsc + sqdf + dqsc + dqdc)
        print ("Accuracy is " + str(acc) + "%")




    def printstats(self, top_t, doc_t, vocab, num):
        print("\nTopics in LDA model:")
        for topic in top_t:
            print topic

        print("\nTopics in documents:")

        for idx, docid in enumerate(self._docmap.keys()):
            print ("Document: " + docid)
            print("\n".join([top_t[idx] for idx in doc_t[idx][:-num - 1:-1]]))


        print("".join(["=" for i in range(200)]))



    def top_topic(self, lda, feature_names, words):
        top = list()
        for topic_idx, topic in enumerate(lda.components_):
            topic = "Topic #%d:" % topic_idx + " ----> " + " ".join([feature_names[i]
                            for i in topic.argsort()[:-self._numtopics - 1:-1]])
            top.append(topic)
        return top




def runLDA():
    data = Data("99")
    data.qrel()
    qlist = data._dlist
    data.score()
    blist = data._dlist
    data._dlist = set(blist).union(set(qlist))
    docmap = data.getmap()
    print len(docmap)


    t0 = time()
    lda = LDA(docmap, 1000, 20)
    lda.train()
    print (time() - t0 )

def runCluster():
    data = Data("56")
    #data.all_qrel()
    #docmap = data.getmap()
    t0 = time()


    docmap = parsedocs()
    #print len(docmap)
    lda = LDA(docmap, 20000, 200)
    mat = lda.trainall()
    doc_cluster = lda.KMeans(mat, 25)
    lda.accCluster(ClusterCheck(), doc_cluster)


    print (time() - t0 )



if __name__ == '__main__':
    runLDA()
    #runCluster()




