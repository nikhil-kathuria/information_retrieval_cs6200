# Set02 — Custom Inverted Index + Retrieval Models

This assignment builds a full inverted index from the AP89 collection from scratch (no Elasticsearch), then runs the same five retrieval models as Set01 against it. It also adds a sixth model: **proximity-based search**.

## Files

### `IndexGen.py` — **Core implementation: index builder**

Builds the inverted index using a **Sort-Based Indexing (SPIMI-style merge)** approach — accumulates an in-memory partial index, then merges it to disk when memory hits a threshold (1000 docs), repeating until all documents are processed.

**Key data structures produced:**

| File | Content |
|---|---|
| `Index.txt` | Flat inverted index; each line is a term's posting list as `docid:pos1 pos2 ...|docid:pos1 ...` |
| `catalog.json` | `term → (start_byte, end_byte)` offsets into `Index.txt` |
| `doclen.json` | `int_id → doc_length` (number of tokens after stop/stem) |
| `docid.json` | `int_id → AP89_docno` (reverse mapping) |
| `statistics.json` | `{sum_ttf, vocab_size}` corpus-level stats |

**Index entry format:** Each posting block is `docid:pos1 pos2 pos3` with blocks separated by `|`. Term positions are stored, enabling proximity search.

**Pipeline in `processor()`:**
1. `filenamedoccount()` — count docs per AP89 file to decide when to flush
2. `parsedocs()` — SGML parser (same logic as Set01), applies `textmod()` for cleaning
3. `stopandstem()` — removes stopwords (`stopwords.txt`) and applies Porter stemmer
4. `mergewrite()` — merges in-memory `invidx` into `Index.txt` on disk, updating `catalog.json`

**Merge strategy:** `firstmerge()` writes directly; subsequent merges do a three-way merge:
- `equalwrite()` — term in both old index and new partial index: concatenate postings
- `bigwrite()` — term only in old index: copy through unchanged
- `smallwrite()` — term only in new partial index: append as new entry

### `models.py` — **Core implementation: retrieval models**

Implements the same five models as Set01, plus proximity search. The key difference from Set01 is that all statistics are read directly from `Index.txt` via byte-offset seeks using `catalog.json`, instead of querying Elasticsearch.

**Models implemented:**

| Function | Model |
|---|---|
| `okapitfcalc()` | Okapi TF |
| `tfidfcalc()` | TF-IDF |
| `okapibm25calc()` | **BM25** — k1=1.2, k2=250, b=0.75 (identical parameters to Set01) |
| `lmlaplacecalc()` | LM with Laplace smoothing — vocab size read from `statistics.json` (not hardcoded) |
| `jelinekmecercalc()` | LM with Jelinek-Mercer smoothing — λ=0.4 |
| `proximsrch()` | **Proximity search** — scores based on minimum span between consecutive query terms in a document |

**How term frequency is computed here vs Set01:**  
In Set01, `trmfreq()` called `elasrch.termvector()`. Here, `trmfreq()` seeks to `catdict[term][0]` in `Index.txt`, reads the posting list, finds the matching docid block, and counts the space-separated positions: `len(blkary[1].split(" "))`.

**Proximity search (`proximsrch()`, lines 365–433):**  
For each adjacent query term pair, finds documents containing both terms, then computes the **minimum span** between their occurrence positions using a two-pointer merge. Score = `(1500 - min_span) * (freq_t1 + freq_t2)`. This model only works because term positions are stored in the index.

**Key difference from Set01:** `avgdoclength()` is computed from `statistics.json` (sum_ttf / num_docs) rather than live ES stats. Vocabulary size comes from `statistics.json` rather than being hardcoded.

**`textmod()`** — text normalization applied during both indexing and query parsing:
- Remove apostrophe + following letter
- Remove non-alphanumeric chars (except `.`)
- Collapse `...` to `.`
- Remove trailing dots
- Remove single-letter tokens
- Lowercase

## BM25 Formula Comparison: Set01 vs Set02

Both use k1=1.2, k2=250, b=0.75 and the same formula. The difference is only where `tf`, `df`, `dl`, `avgdl` come from:

| Statistic | Set01 source | Set02 source |
|---|---|---|
| `tf` | `elasrch.termvector()` | count positions in `Index.txt` posting block |
| `df` | `elasrch.termvector()` | count `|`-separated blocks in posting list |
| `dl` | Elasticsearch facet query | `doclen.json` |
| `avgdl` | ES field_statistics | `statistics.json` sum_ttf / N |
| `N` (corpus size) | ES field_statistics | `len(dlendict)` |

## Running

```bash
# Step 1: Build the index (writes Index.txt, catalog.json, doclen.json, docid.json, statistics.json)
python IndexGen.py

# Step 2: Run retrieval (uncomment desired modelgen call in main())
python models.py
```

## Cross-references

- **← Set01**: Same five retrieval model formulas. Set01 uses Elasticsearch; this set is the self-contained from-scratch implementation. Compare `okapibm25calc()` in both files line by line to see the formula is identical.
- **→ Set04/trec_eval.py**: Evaluates the TREC-format output files written by `modelgen()` here.
- **→ Set05**: The result files written here (e.g., `OkapiBM25.txt`, `TdfId.txt`) are used as feature columns in the ML ranking model.
