# Set04 — PageRank + TREC Evaluation

This assignment has two independent components: (1) two implementations of PageRank on the link graph collected by the Set03 crawler, and (2) a Python implementation of the TREC evaluation tool.

## Files

### `Page_Rank_iterative.py` — **Core implementation: iterative PageRank**

Implements the standard power-iteration PageRank algorithm.

**Algorithm (`calcpr()`):**
- Damping factor: `d = 0.85`, convergence threshold: `ε = 0.001`
- Initializes all scores to 1
- Each iteration updates: `score(p) = (1 - d) + d * Σ(score(q) / outcount(q))` for all q that link to p
- Removes a page from the active set when `|old_score - new_score| < ε`
- Hard cap at 1,000,000 iterations

**`getoutcount(linkdict)`** — inverts the link graph from `source → [dest]` to `dest → outlink_count_of_source`. This is needed because PageRank distributes a page's score across its *outgoing* links.

**`otherpr(outcount, outlist, oldscore)`** — sums the incoming PageRank contributions from all pages that link to the current page.

**Input format:** A link graph file (passed as `sys.argv[1]`) where each line is `page outlink1 outlink2 ...`.

**Usage:**
```bash
python Page_Rank_iterative.py <LinkGraphFile>
```

### `Page_Rank_eigen.py` — **Core implementation: eigen-vector PageRank**

Implements PageRank using the transition matrix's dominant eigenvector via numpy.

**Algorithm (`calcpr()`):**
- Builds an N×N transition matrix `tranmat` where `tranmat[i][j] = 1/out_degree(i)` if page i links to j, else 0
- Uses the union of all source and destination pages as the node set
- Computes the dominant eigenvector (the stationary distribution of the random walk)

**When to use which:** The iterative version works for large sparse graphs. The eigen version builds a dense N×N matrix, so it's only practical for small graphs (the matrix can be enormous).

### `trec_eval.py` — **Core implementation: evaluation metrics**

A Python reimplementation of the standard `trec_eval` tool. Reads a QREL file and a ranked results file (both in TREC format), computes per-query and aggregate IR metrics.

**Metrics computed:**

| Metric | Implementation |
|---|---|
| Precision@K | `relret / k` at k = 5, 10, 15, 20, 50, 100, 200, 500, 1000 |
| Recall@K | `relret / total_relevant` at same K values |
| F-measure@K | `2*P*R/(P+R)` |
| Average Precision (AP) | Running sum of `relret/docseen` when a relevant doc is hit, divided by total relevant |
| MAP | Mean of AP across all queries |
| R-Precision | Precision at rank = total relevant docs for the query |
| nDCG | `ndcgcalc()`: DCG / ideal-DCG using grade values from QREL (0/1/2) |

**`ndcgcalc(dcglist)`:** Computes DCG as `grade[0] + Σ grade[i]/log2(i+1)` for i≥1, then divides by the ideal DCG (same formula applied to the sorted-descending grade list).

**Usage:**
```bash
python trec_eval.py <qrel_file> <trec_file>          # aggregate stats only
python trec_eval.py -q <qrel_file> <trec_file>       # per-query verbose output
```

The `-q` flag triggers `printstat()` after each query, showing the full P/R/F table.

### `trec_eval.pl`

The original Perl reference implementation. Results from this and `trec_eval.py` should match.

### `Page_Rank_eigen.py` vs `Page_Rank_iterative.py` — summary

| | Iterative | Eigen |
|---|---|---|
| Method | Power iteration | Transition matrix eigenvector |
| Memory | O(N) | O(N²) |
| Input | Link graph file | Same |
| Convergence | ε-based per-node | Matrix algebra |
| Practical limit | Large graphs | Small graphs only |

## Data files

- `outlinks.json` — outlink graph from Set03 crawler, format: `url → [outlink_urls]`
- `inlink.json` — inlink graph from Set03 crawler
- `QREL.txt` / `qrels.adhoc.51-100.AP89.txt` — relevance judgments for AP89 queries 51–100
- `TREC.txt` / `results.txt` — sample ranked result files to evaluate

## Cross-references

- **← Set03**: `outlinks.json` and `inlink.json` are produced by the Set03 crawler. PageRank runs on that link graph.
- **← Set01/Set02**: `trec_eval.py` evaluates the TREC-format result files written by `Set01/models.py` and `Set02/models.py`.
- **→ Set05**: `trec_eval.py` is also used to evaluate the re-ranked output (`TestScore.txt`, `TrainScore.txt`) from the ML model in Set05.
