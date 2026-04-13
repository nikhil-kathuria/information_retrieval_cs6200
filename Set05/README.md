# Set05 — Machine Learning on IR (Learning to Rank)

This assignment implements a **learning-to-rank** pipeline using `pyliblinear` (a Python wrapper for LIBLINEAR SVM). The retrieval scores from multiple models (BM25, TF-IDF, etc.) are combined into a feature matrix, and a linear SVM learns to re-rank documents by relevance.

## Files

### `machine_learning_on_ir.py` — **Core implementation**

The complete learning-to-rank pipeline in one file.

**Pipeline overview:**

```
QREL file + model score files
       ↓
  genmatfile()       — build feature matrix, split train/test queries
       ↓
  trainmodel()       — train LIBLINEAR SVM on training matrix
       ↓
  generatescorefile()— predict scores for train & test sets → TREC output files
```

**Step 1 — Feature matrix construction (`genmatfile()`):**

Reads six model result files (must be present in the same directory):

| Feature index | Model file | Source |
|---|---|---|
| 1 | `JLKM.txt` | Jelinek-Mercer LM scores (from Set01 or Set02) |
| 2 | `BM25.txt` | BM25 scores |
| 3 | `TF.txt` | Okapi TF scores |
| 4 | `TFIDF.txt` | TF-IDF scores |
| 5 | `LML.txt` | Laplace LM scores |
| 6 | `PROX.txt` | Proximity search scores |

Queries are split **randomly** into train (45 queries) and test (5 queries) via `randomquery()`.

The feature matrix format is LIBLINEAR's sparse format:
```
<relevance_label>  1:<score1>  2:<score2>  ...  6:<score6>
```
Written to `FeatureMatrix.txt` for training queries, and per-query files `<qno>.txt` for both train and test.

**`fetchqrel()`** — reads `qrels.adhoc.51-100.AP89.txt` and builds:
- `qurydocdict`: `qno → {docno → relevance}` (only docs in the QREL file become training examples)
- `docmapdict`: `docno → int_id`
- `reversedocdict`: `int_id → docno`

**Step 2 — Training (`trainmodel()`):**

Loads `FeatureMatrix.txt` into a `pyliblinear.FeatureMatrix` object and trains a `pyliblinear.Model`. The trained model is saved to `Trained.txt`.

**Step 3 — Scoring (`generatescorefile()`):**

For each query in train/test:
1. Loads the per-query matrix file (`<qno>.txt`)
2. Calls `model.predict()` to get predicted labels/scores per document
3. Sorts documents by predicted score descending
4. Writes TREC-format output: `qno Q0 docno rank score Exp`

Output files: `TestScore.txt` (5 test queries), `TrainScore.txt` (45 training queries).

**Limitation to be aware of:** The relevance label in the feature matrix is the raw QREL grade (0, 1, 2). Documents not present in the QREL file are never included as training examples — only QREL-judged documents appear in the matrix.

## Data files

- `qrels.adhoc.51-100.AP89.txt` — relevance judgments (same as Set01/Set04)
- `query_desc.51-100.short.txt` — query list (same file as Set01/Set04)
- `FeatureMatrix.txt` — generated feature matrix for training queries
- `TrainScore.txt` — re-ranked results for training queries
- `TestScore.txt` — re-ranked results for test queries
- `Trained.txt` — saved LIBLINEAR model

## Cross-references

- **← Set01 / Set02**: The six model score files (`BM25.txt`, `TFIDF.txt`, etc.) are the TREC-format result files produced by `Set01/models.py` or `Set02/models.py`. They must be copied/symlinked into this directory before running.
- **← Set04/trec_eval.py**: Use `trec_eval.py` to evaluate `TestScore.txt` and `TrainScore.txt` against `qrels.adhoc.51-100.AP89.txt` to measure whether learning to rank improves MAP/nDCG over individual models.

## Running

```bash
# Ensure the six model score files are present in Set05/
# (BM25.txt, TFIDF.txt, TF.txt, JLKM.txt, LML.txt, PROX.txt)

python machine_learning_on_ir.py

# Evaluate results
python ../Set04/trec_eval.py qrels.adhoc.51-100.AP89.txt TestScore.txt
```
