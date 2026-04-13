# Set08 — LDA Topic Modeling + Document Clustering

This assignment applies **Latent Dirichlet Allocation (LDA)** and **K-Means clustering** to AP89 documents to discover latent topics and evaluate whether documents relevant to the same query cluster together.

## Files

### `runlda.py` — **Core implementation: LDA and clustering pipeline**

The main entry point. Contains three classes and two driver functions.

---

#### `Data` class — document loader

Fetches documents from Elasticsearch (`localhost:9200`, index `ap_89`) and produces a `docid → text` map.

| Method | Purpose |
|---|---|
| `qrel()` | Loads docs relevant to a single query from `qrels.adhoc.51-100.AP89.txt` |
| `score()` | Loads top-ranked docs for a single query from a BM25 results file |
| `all_qrel()` | Loads all relevant docs across all queries |
| `getmap()` | Fetches doc text from Elasticsearch for each docid in `self._dlist` |
| `getall()` | Fetches all 84,678 AP89 docs from Elasticsearch |

Hardcoded paths in `__init__`: `self._pp` points to `Set08/scores/` for BM25 results, `self._qp` points to `Set04/qrels.adhoc.51-100.AP89.txt`.

---

#### `LDA` class — topic modeling and clustering

Takes a `docid → text` dict and runs sklearn's `LatentDirichletAllocation`.

**`train()`** — fits LDA on a subset of docs (e.g., docs relevant to one query):
- `CountVectorizer` with `max_df=0.95`, `min_df=2`, up to `maxfeatures` terms
- `LatentDirichletAllocation` with `n_topics` topics, 25 online iterations
- Prints top `numwords` (10) words per topic
- Prints the top 3 topic assignments per document

**`trainall()`** — fits LDA on the full doc set and returns the document-topic matrix (used as input to K-Means). Looser min_df=10 to handle the full corpus.

**`KMeans(mat, nc)`** — runs K-Means on the document-topic matrix:
- Returns `docid → cluster_id` dict
- Used to cluster all relevant AP89 docs into `nc=25` clusters

**`kMeansSort(mat, nc)`** — same as `KMeans` but additionally prints cluster membership sorted by distance to centroid.

**`accCluster(cc, doc_cluster)`** — evaluates clustering quality:
- Uses all pairwise combinations of relevant documents from `ClusterCheck`
- Classifies each pair as: same query + same cluster (TP), same query + different cluster (FN), different query + same cluster (FP), different query + different cluster (TN)
- Accuracy = `(TP + TN) / total_pairs`

**`top_topic(lda, feature_names, words)`** — formats top-N words per LDA topic as a string.

---

#### Driver functions

**`runLDA()`** — runs topic modeling on documents relevant to query "99":
1. Loads QREL-relevant docs for query 99
2. Loads BM25-ranked docs for query 99
3. Takes the union, fetches text from ES
4. Trains LDA with 1000 features, 20 topics

**`runCluster()`** — runs clustering on the full AP89 corpus:
1. Calls `parseap89.parsedocs()` to load all AP89 docs from disk (bypasses ES)
2. Trains LDA with 20000 features, 200 topics, returns document-topic matrix
3. Runs K-Means into 25 clusters
4. Evaluates cluster purity via `ClusterCheck`

The `if __name__ == '__main__'` block runs `runLDA()` by default; `runCluster()` is commented out.

---

### `parseap89.py` — AP89 SGML parser

Re-implements the same `parsedocs()` function as `Set01/models.py`, but reads from `../Set01/AP_DATA/ap89_collection/` directly from disk (no Elasticsearch). Returns a `docid → raw_text` dict.

This is the third copy of this parser in the repo (Set01, Set02/IndexGen.py, Set08). Used by `runCluster()` to avoid ES overhead when processing all ~84k docs.

### `clustercheck.py` — clustering evaluator

**`ClusterCheck` class:**
- Reads query list from `../Set01/AP_DATA/query_desc.51-100.short.txt`
- Reads `../Set01/qrels.adhoc.51-100.AP89.txt`
- Builds `_dqmap`: `docid → set of query IDs` for all relevant docs
- Generates `_pairlist`: all `(doc1, doc2)` pairs from the relevant doc set (O(N²) pairs)

Used by `LDA.accCluster()` to evaluate whether documents relevant to the same query end up in the same cluster.

Note: hardcoded to look in `../Set01/` for data files.

### `lda.py` — standalone LDA demo

A standalone script adapted from the sklearn documentation (authors: Grisel, Buitinck, Yau). Demonstrates NMF and LDA on the **20 Newsgroups** dataset (not AP89). Useful as a reference for understanding the sklearn LDA API but not part of the AP89 pipeline.

### `steps.txt`

Notes/scratch pad with implementation steps or experiment log.

## Cross-references

- **← Set01**: `parseap89.py` reads from `../Set01/AP_DATA/` and `clustercheck.py` reads qrel/query files from `../Set01/`. The `Data` class uses the same Elasticsearch index `ap_89` built in Set01.
- **← Set04**: `Data.__init__` hardcodes `self._qp` pointing to `Set04/qrels.adhoc.51-100.AP89.txt`. The BM25 results loaded by `Data.score()` are produced by Set01 or Set02.
- **← Set05**: The BM25 result files in `Set08/scores/` are the same TREC-format files produced by the retrieval models in Set01/Set02.

## Running

```bash
# Ensure Elasticsearch is running with the ap_89 index populated (see Set01)
# Run LDA on query 99's relevant docs
python runlda.py

# To run clustering on the full corpus, edit runlda.py:
#   comment out runLDA(), uncomment runCluster()
python runlda.py
```
