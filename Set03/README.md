# Set03 — Web Crawler

This assignment implements a multi-wave focused web crawler with a priority-queue frontier, robots.txt compliance, politeness (per-domain rate limiting), and structured document dumping in AP89-compatible format.

## Files

### `crawler.py` — **Core implementation: crawl logic**

Implements the full crawl loop. The entry point is `frontiercall()`, which runs an infinite loop of `crawlwave()` → `preparefrontier()`.

**Architecture — two-phase per wave:**

1. **`crawlwave(inlink, current, timedict, urlparsed)`** — processes the current priority-queue frontier:
   - Pops URLs from the min-heap `current`
   - Skips already-visited URLs (`urlparsed` set)
   - Enforces robots.txt via `robotblock()` (from `fetchurl.py`)
   - Enforces content-type/language filter via `getresponse()` — accepts only `text/*` or `message/*` in English
   - Enforces per-domain politeness: sleeps if the same domain was hit less than 1 second ago (`timedict`)
   - Extracts outgoing URLs via `nexturls()` (from `fetchurl.py`)
   - Tracks inlinks: for each discovered URL, if it was already visited, records the back-link
   - Calls `dumpall()` every 100 URLs, or when the frontier drops below 30% capacity
   - Exits after 12,000 URLs crawled

2. **`preparefrontier(future, inlink)`** — converts the set of discovered URLs into a scored priority queue:
   - Computes domain rarity: `occurrences_of_domain / total_urls_in_frontier`
   - Priority score = `rarity / inlink_count` (rare domains + many inlinks = highest priority = lowest heap score)
   - Converts to a `heapq` min-heap

**Document output format (`dumpall()`):**  
Writes batches of crawled pages to `./web-data/N.txt` in a pseudo-AP89 SGML format with tags: `<DOC>`, `<DOCNO>`, `<HEAD>`, `<HTTP-HEADER>`, `<TEXT>`, `<RAW-HTML>`, `<OUTLINKS>`.

**`gettext()`** — extracts visible text from `<b>` and `<p>` tags only using BeautifulSoup's `findAll(text=True)` filtered by `filtertag()`.

### `fetchurl.py` — **Core implementation: URL utilities**

Provides the two functions imported by `crawler.py`.

**`canonicalize(pdomain, pscheme, childurl)`** — normalizes URLs:
- Lowercases scheme and hostname
- Drops default ports (80, 443)
- Resolves relative paths via `refinepath()`
- Skips fragment-only links (`#...`)
- Handles both absolute URLs (have `netloc`) and relative paths (inherit parent domain/scheme)

**`refinepath(path)`** — cleans path:
- `../` → `/`
- Collapses `//+` → `/`
- Ensures path starts with `/`

**`nexturls(url, response, domain, scheme)`** — parses HTML with BeautifulSoup, extracts all `<a href>` links, calls `canonicalize()` on each, returns a set of valid absolute URLs.

### `seedfile.txt`

List of seed URLs (one per line). Loaded by `getinitialseed()`, which canonicalizes each and assigns an initial priority score (sequential integers — i.e., seed order is the initial priority).

## Crawl strategy summary

```
seed URLs → heapq frontier
    ↓
crawlwave: pop URL → fetch → robots check → content check → politeness delay
    → extract outlinks → track inlinks → dump every 100 docs
    ↓
preparefrontier: score by (domain_rarity / inlink_count) → new heapq
    ↓
repeat
```

The crawler stops when `len(urlparsed) > 12000` or runs indefinitely.

## Cross-references

- **→ Set04**: The link graph (outlinks/inlinks) collected by this crawler feeds directly into `Page_Rank_iterative.py` and `Page_Rank_eigen.py`. `Set04/outlinks.json` and `Set04/inlink.json` are products of this crawl.
- The document dump format (`<DOC>/<DOCNO>/<TEXT>`) mirrors the AP89 collection format used in Set01/Set02, so the same parsers could theoretically index crawled pages into Elasticsearch.
