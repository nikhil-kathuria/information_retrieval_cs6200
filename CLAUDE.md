# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a graduate Information Retrieval (CS6200) course project repository. Each `Set` directory corresponds to a homework/assignment covering different IR topics. The primary dataset used throughout is the **AP89 collection** (Associated Press 1989 newswire), indexed into Elasticsearch.

## Repository Structure by Assignment

| Directory | Topic |
|-----------|-------|
| `Set01` | Elasticsearch indexing + retrieval models (TF-IDF, BM25, language models) |
| `Set02` | Custom inverted index + retrieval models (no Elasticsearch) |
| `Set03` | Web crawler with BFS/priority-queue frontier, robots.txt compliance |
| `Set04` | PageRank (iterative and eigen-vector approaches) + TREC evaluation |
| `Set05` | Machine learning on IR (feature matrix, train/test with liblinear) |
| `Set08` | LDA topic modeling + document clustering (KMeans) |

## Key Dependencies

- **Python 2** (most sets use Python 2 syntax: `print` statements, `xrange`, `from sets import Set`)
- `elasticsearch` — Elasticsearch Python client (connects to `localhost:9200`)
- `stemming` — Porter stemmer (`from stemming.porter import stem`)
- `beautifulsoup4` — HTML parsing in the crawler
- `sklearn` — Scikit-learn for LDA/NMF/KMeans (Set05, Set08)
- `pyliblinear` — Linear SVM classifier (Set05)
- `numpy` — Matrix operations for PageRank eigen-vector method (Set04)

## Running Scripts

Most scripts are run directly with Python 2:

```bash
# Run a retrieval model
python models.py

# Run TREC evaluation (custom Python implementation)
python trec_eval.py <qrel_file> <trec_file>
python trec_eval.py -q <qrel_file> <trec_file>   # verbose per-query output

# Or use the Perl reference implementation
perl trec_eval.pl <qrel_file> <trec_file>

# Run PageRank
python Page_Rank_iterative.py
python Page_Rank_eigen.py

# Run ML on IR
python machine_learning_on_ir.py

# Run LDA
python runlda.py
```

## Elasticsearch Setup

Sets 01 and 08 require Elasticsearch running locally:
- Default connection: `localhost:9200`
- Index name: `ap_89`, doc_type: `document`
- `Set01/indxNmap.py` — creates the index with custom English analyzer
- `Set01/models.py` — parses the AP89 collection and bulk-indexes documents
- AP89 data is expected at `./AP_DATA/ap89_collection/ap*`

## Data Files

- `AP_DATA/ap89_collection/` — raw AP89 newswire files (SGML format)
- `AP_DATA/query_desc.51-100.short.txt` — queries 51–100 (format: `queryno.desc.narrative`)
- `qrels.adhoc.51-100.AP89.txt` — relevance judgments (qno, 0, docno, relevance)
- `Set03/seedfile.txt` — seed URLs for the web crawler
- `Set05/FeatureMatrix.txt`, `TrainScore.txt`, `TestScore.txt` — precomputed feature/score files

## TREC Output Format

Retrieval results must be written in standard TREC format:
```
<query_id> Q0 <doc_id> <rank> <score> <run_name>
```
This is required by both `trec_eval.py` and `trec_eval.pl`.

## Retrieval Models (Set01, Set02)

`models.py` in each set implements multiple retrieval models against the same query/document set:
- **TF-IDF** variants (tf-idf, sublinear tf)
- **BM25** (Okapi BM25, k1/k2/b parameters)
- **Language Models** (Jelinek-Mercer smoothing, Dirichlet prior, Laplace/Lidstone smoothing)
- **Proximity-based** models (Set01 uses Elasticsearch proximity queries via `proximquery.json`)

Set01 delegates to Elasticsearch for term statistics; Set02 builds a custom inverted index from scratch (`termindex.py`).
