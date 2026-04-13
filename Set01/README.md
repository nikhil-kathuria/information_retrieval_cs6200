# Set01 — Retrieval Models via Elasticsearch

This assignment implements five retrieval models against the AP89 document collection, using Elasticsearch as the backend for term statistics (term frequency, document frequency, corpus frequency, document length). All models score queries 51–100 from `AP_DATA/query_desc.51-100.short.txt` and write ranked results in TREC format.

## Files

### `models.py` — **Core implementation** (primary file)

Contains every retrieval model. The `modelgen()` dispatcher calls the correct scoring function per query and writes TREC output.

**Retrieval models implemented:**

| Function | Model |
|---|---|
| `okapitfcalc()` | Okapi TF — BM25 without IDF; scores `tf / (tf + 0.5 + 1.5*(dl/avgdl))` |
| `tfidfcalc()` | TF-IDF — Okapi TF component multiplied by `log(N/df)` |
| `okapibm25calc()` | **BM25** — full Okapi BM25 with k1=1.2, k2=250, b=0.75; IDF × TF × query-freq components |
| `lmlaplacecalc()` | Language Model with Laplace smoothing — `(tf+1)/(dl+V)`, vocab size hardcoded to 178050 |
| `jelinekmecercalc()` | Language Model with Jelinek-Mercer smoothing — λ=0.4 mixture of foreground and background ML estimates |

**Helper functions for Elasticsearch stat retrieval:**

- `trmfreq()` — term frequency for a term in a specific doc, via ES termvector API
- `docfreq()` — document frequency of a term
- `corpusfreq()` — collection frequency (TTF) of a term
- `avgdoclength()` / `totaldoc()` — corpus-level statistics from a fixed anchor doc `AP891011-0104`
- `search()` — retrieves all docIDs containing a term (up to 100k results)

**Key design note:** All corpus statistics are fetched live from Elasticsearch per term per query. The `main()` function shows that the script was later changed to load precomputed stats from `docindex.json` instead, to avoid repeated ES calls.

**BM25 formula (line 326–344):**
```
IDF = log(1 + (N+0.5)/(df+0.5))
TF  = (tf*(1+k1)) / (tf + k1*((1-b) + b*(dl/avgdl)))
QF  = (qf*(1+k2)) / (qf + k2)
score = IDF * TF * QF
```

### `indxNmap.py` — Elasticsearch index setup

- `createindex()` — creates `ap_89` index with custom English analyzer and a single shard
- `putmapping()` — sets field mapping for `docno` (stored string) and `text` (analyzed)

Run once before indexing. The index name used throughout is `ap_89`.

### `EsApi_load.py` — Git repository indexer (reference/demo)

Sample code for bulk-indexing a git repository into Elasticsearch using the `git` Python library. Not directly related to AP89 retrieval; appears to be a template/reference borrowed from the Elasticsearch examples.

### `EsApi_Query.py` — Query helper (reference/demo)

Companion to `EsApi_load.py`. Provides `print_hits()` for displaying search results and a facet-based query example. Again a reference template, not part of the AP89 pipeline.

### `termindex.py`

A standalone term-lookup utility that queries ES termvectors for a specific docid and term. Likely used for manual debugging/inspection of term statistics during development.

### `scriptaccess.py`

Exploratory script for testing Elasticsearch scripted queries (Groovy scripts for doc length calculation). Used for ad-hoc investigation of ES scripting API.

### `trec_eval.pl`

The standard Perl TREC evaluation script. Used to score ranked result files (TREC format) against `qrels.adhoc.51-100.AP89.txt`.

## Cross-references

- **→ Set02**: `Set02/models.py` re-implements all five of these same models from scratch without Elasticsearch, reading directly from a custom inverted index built by `Set02/IndexGen.py`. The function signatures and formula logic are identical — the only difference is the data source (ES termvector API here vs. byte-offset reads from `Index.txt` in Set02).
- **→ Set04**: `Set04/trec_eval.py` is a Python reimplementation of `trec_eval.pl` found here. Both score the same TREC-format output files this assignment produces.
- **→ Set05**: `Set05/machine_learning_on_ir.py` loads BM25 and TF-IDF result files (among others) produced by this assignment's `modelgen()` as feature columns for learning-to-rank.
- **→ Set08**: `Set08/parseap89.py` re-implements `parsedocs()` from this file (same SGML parsing logic), and `Set08/clustercheck.py` reads `qrels.adhoc.51-100.AP89.txt` from `../Set01/`.

## Running

```bash
# 1. Ensure Elasticsearch is running at localhost:9200
# 2. Index the AP89 collection (run once)
python -c "from models import parsedocs, elasrch; parsedocs(elasrch)"

# 3. Run a specific model (edit main() to uncomment the desired modelgen call)
python models.py
```
