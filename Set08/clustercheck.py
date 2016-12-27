from collections import defaultdict

class ClusterCheck:
    def __init__(self):
        self._path ="../Set01/qrels.adhoc.51-100.AP89.txt"
        self._dqmap = defaultdict(set)
        self._pairlist = list()
        self._reldoc = set()
        self._qset = set()

        self.querygen()
        self.popdata()
        self.genpairs()


    def querygen(self):
        fileloc = "../Set01/AP_DATA/query_desc.51-100.short.txt"
        qfile = open(fileloc)
        for line in qfile:
            self._qset.add(line.split('.')[0])
        qfile.close()


    def popdata(self):
        fobj = open(self._path, 'r')
        for line in fobj:
            arr = line.split()
            if arr[0] in self._qset and arr[3] != "0":
                self._dqmap[arr[2]].add(arr[0])
                self._reldoc.add(arr[2])
        fobj.close()


    def genpairs(self):
        docs = list(self._reldoc)
        for slow in range(len(docs)):
            for fast in range(slow + 1, len(docs)):
                self._pairlist.append((docs[slow], docs[fast]))

        self._qset = None
        self._reldoc = None


        # print(len(docs))
        # print(len(pairlist))
        # print(len(self._qmap))
        for doc in self._dqmap:
            if len(self._dqmap[doc]) > 1:
                print(self._dqmap[doc])






if __name__ == '__main__':
    ck = ClusterCheck()
