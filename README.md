# Motive

**An explainable, intent-aware e-commerce recommender that shows the evidence behind every result.**

Most recommendation systems return a ranked list and stop there. You see what was recommended, but not why, and you have no way to check whether a request like "something different this time" actually changed anything.

Motive keeps the evidence. For each recommendation, it records which item from the shopper's history led to it, how similar the two items are in catalog properties, whether shoppers tend to view them in the same sessions, how popular the item is, where the learned model ranked it, and whether a natural-language request moved it. It combines retrieval, a learned reranker, structured intent parsing, and recorded provenance into one pipeline served through FastAPI and a React interface.

Motive is built on the anonymized Retailrocket dataset, and that shaped the whole design. The data does not contain real product names, brands, or prices, so Motive is careful never to pretend it does. When a request asks for something the data cannot verify, the system says so.

---

## Table of Contents

- [What It Does](#what-it-does)
- [Architecture](#architecture)
- [Dataset and Cold Start](#dataset-and-cold-start)
- [Candidate Generation](#candidate-generation)
- [Learned Reranking](#learned-reranking)
- [Natural-Language Intent](#natural-language-intent)
- [Explainability and Provenance](#explainability-and-provenance)
- [Frontend](#frontend)
- [Evaluation](#evaluation)
- [Performance Engineering](#performance-engineering)
- [Technology Stack](#technology-stack)
- [Testing](#testing)
- [Engineering Lessons](#engineering-lessons)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Project Status](#project-status)

---

## What It Does

Given a shopper ID and an optional request in plain English, Motive returns a ranked list of products along with the evidence for each one.

A known shopper's recommendations come from two retrieval signals, catalog-property similarity and behavioral co-visitation, which are then reranked by a trained gradient-boosted tree model. A new shopper with no history gets weighted popularity instead. If the shopper types a request, Claude converts it into a structured intent object, and Motive applies the supported parts of that intent as a small, bounded adjustment to the learned ranking.

Every result carries its provenance: the source history item, similarity and co-visitation scores, support counts, popularity, base rank, final rank, and any part of the request that could not be verified. Explanations are generated from that evidence rather than from generic templates.

The project includes a Python recommendation backend, a FastAPI service, a React and Vite frontend, 37 automated tests, and a 158-check product regression suite.

---

## Architecture

Each part of Motive has one job. The learned model ranks. Python code retrieves candidates and calculates scores. Claude interprets the request. Recorded evidence explains the result.

Claude never chooses recommendation items. It only turns a sentence into structured fields. All retrieval and ranking happen in the local recommendation system.

```
                     Natural-language request (optional)
                                  │
                                  ▼
                        Claude intent parser
                  (returns structured UserIntent only)
                                  │
Shopper ID ──► User routing       │
                 │                │
       ┌─────────┴─────────┐      │
       ▼                   ▼      │
   New user            Known user │
       │                   │      │
       ▼                   ▼      │
  Weighted          Candidate generation
  popularity        (content + co-visitation,
       │             provenance recorded)
       │                   │      │
       │                   ▼      │
       │           Tree reranker  │
       │                   │      │
       │                   ▼      ▼
       │        Intent blend (85% learned, 15% intent)
       │                   │
       └─────────┬─────────┘
                 ▼
     Evidence and grounded explanations
                 │
                 ▼
         FastAPI ──► React UI
```

| Component | Handled by | Role |
|---|---|---|
| User routing | Deterministic Python | Sends each shopper to cold-start or personalized logic |
| Candidate retrieval | Python, NumPy, SciPy | Content neighbors and co-visitation neighbors |
| Ranking | scikit-learn model | Orders candidates by predicted relevance |
| Intent parsing | Claude | Converts free text into a structured `UserIntent` |
| Intent blending | Deterministic Python | Applies supported preferences as a bounded adjustment |
| Explanations | Deterministic Python | Built only from recorded evidence |

---

## Dataset and Cold Start

### The Retailrocket Dataset

| | Approximate size |
|---|---|
| Interaction rows | 2.75 million |
| Event types | view, add-to-cart, transaction |
| Visitors | 1.4 million |
| Products in interaction data | 235,000 |
| Products with catalog metadata | 400,000+ |
| Time span | May to September 2015 |

The dataset is anonymized. Products are numeric IDs, and most catalog properties are hashed. Real product names, brands, prices, specifications, retailer links, and product meaning are not reliably available.

This matters for anything the system says. If a shopper asks for "Sony headphones under $300 for travel," Motive can parse that into `requested_brand = Sony`, `max_price = 300`, and `use_case = travel`. It then marks all three as unverifiable. It will not claim that any result is a Sony product, costs under $300, or is suited to travel.

For the same reason, the colored marks on recommendation cards are generated from item IDs. They are not product images.

### User Routing

| Segment | Historical items | Strategy |
|---|---|---|
| New | 0 | Weighted catalog popularity |
| Low-history | 1 to 2 | Personalized retrieval and reranking |
| Established | 3 or more | Personalized retrieval and reranking |

The data is very sparse. Around 90% of September users have no history in the earlier training period, so cold start is the common case, not an edge case.

### Cold Start

New shoppers have no behavioral evidence to work from, so they receive popularity-based recommendations. Popularity is weighted by how strong each interaction is:

| Event | Weight |
|---|---|
| View | 1 |
| Add-to-cart | 3 |
| Transaction | 5 |

A new shopper's request is still parsed, but it does not currently change the popularity ordering. The UI tells the shopper this directly rather than letting them assume their request had an effect.

---

## Candidate Generation

Reranking can only reorder what retrieval finds, so candidate generation gets a lot of attention in Motive. Known shoppers get candidates from two independent sources.

### Content Similarity

Each product's catalog metadata is turned into tokens that keep track of which property each value belongs to. This matters because two products sharing the value "5" means nothing unless it is the same property. The tokens form a sparse item-feature matrix:

| | Approximate size |
|---|---|
| Products | 417,053 |
| Retained features | 161,379 |
| Non-zero entries | 22.5 million |

Rows are normalized, so the similarity between two items is a cosine-style score. For example, item 460429's close neighbor is item 100656, with a similarity of about 0.92. This is an internal score over catalog properties, not a percentage of real-world similarity.

### Behavioral Co-visitation

Items that the same shopper viewed within a single session are linked. A session ends after 30 minutes of inactivity. The May to July build produced:

| | Approximate count |
|---|---|
| Sessions | 1.19 million |
| Usable multi-item sessions | 183,446 |
| Directed item pairs | 1.41 million |
| Items with behavioral neighbors | 96,460 |

### Why the Two Signals Stay Separate

It would be simpler to merge them into one similarity score. Before deciding, I checked how much they overlap. Across 100 sampled items, the top-50 content neighbors and top-50 co-visitation neighbors shared a mean of about 1.92 items (median 1), with a mean Jaccard overlap of about 0.031.

In other words, the two signals almost never agree. Catalog similarity captures what a product is. Co-visitation captures what shoppers actually browse together. Keeping them separate lets the reranker learn how much to trust each one, and lets explanations say which kind of evidence produced a result.

### Final Configuration

For each known shopper, Motive takes up to 20 of their strongest history items, pulls 50 content neighbors and 50 co-visitation neighbors for each, and removes items the shopper has already seen. This yields roughly 200 candidates before reranking. The exact history item that produced each candidate is recorded at this stage.

Popularity is used as a ranking feature for known shoppers, but not as an extra candidate source in the final configuration.

---

## Learned Reranking

Each candidate gets a feature vector built from its retrieval evidence:

| Feature group | Features |
|---|---|
| Content | content score, maximum content similarity, history support count, average content support, multiple-history support |
| Co-visitation | co-visitation score, log co-visitation score, maximum co-visitation score, co-visitation support count, average co-visitation support, multiple co-visitation support |
| Popularity | popularity score, log popularity |
| Shopper | user history count, established-user flag |

A logistic regression reranker was tested first. The final model is scikit-learn's `HistGradientBoostingClassifier`, which handles non-linear interactions between these features, such as a candidate being supported by several history items through both signals at once.

```
HistGradientBoostingClassifier(
    learning_rate=0.08,
    max_iter=200,
    max_leaf_nodes=31,
    min_samples_leaf=20,
    l2_regularization=1.0,
    random_state=42,
)
```

---

## Natural-Language Intent

Claude converts a free-text request into a structured `UserIntent` object. It does not see the catalog and does not choose, add, or remove recommendations.

Four ranking directions are supported and can affect ranking:

| Direction | Meaning |
|---|---|
| familiar | Closer to what the shopper has already interacted with |
| exploratory | Further from the shopper's usual items |
| popular | Favors widely engaged items |
| niche | Favors less common items |

Other fields can be parsed but not verified against anonymized data: brand, minimum price, maximum price, use case, priority features, and features to avoid. These are returned as unverifiable constraints and shown to the shopper.

### How Intent Affects Ranking

The learned reranker stays in charge. Supported intent is applied afterward as a limited adjustment:

```
final_score = 0.85 * normalized_reranker_score
            + 0.15 * normalized_intent_score
```

The 85/15 split is hand-selected. It was not learned, calibrated, or tuned as an optimal setting. It reflects a product decision that the shopper's request should nudge the ranking without overriding what the model learned from behavior.

### The Blending Bug

The first version of this blend did not behave as intended. Raw tree probabilities were very small numbers, while intent scores sat roughly in a 0 to 1 range. So even though the weights said 85/15 on paper, intent was effectively deciding the ranking.

I found this during explainability testing. Once explanations started reporting base rank and final rank side by side, the rank movements were clearly too large for a 15% adjustment. The fix was to normalize the reranker score and the intent score independently before blending.

After the fix, intent nudges results instead of replacing them. In one test, item 323403 moved from rank 5 to rank 4, item 186360 moved from rank 4 to rank 5, and the top three learned results stayed in the top three.

---

## Explainability and Provenance

Early versions produced explanations like "This item is similar to products from your history." That sentence is true for nearly every recommendation and tells the shopper nothing.

Reconstructing better explanations after ranking would have meant guessing at what caused each result. Instead, candidate generation was changed to record provenance as candidates are created, so the evidence travels with each item through reranking and intent blending.

Each recommendation can carry:

- the exact source history item and its interaction weight
- content similarity and its weighted contribution
- the co-visitation source item and score
- support counts for both signals
- the popularity signal
- base score, base rank, final score, and final rank
- the intent adjustment
- any unverifiable constraints from the request

Explanations are built only from these fields. A real example:

> Item 323403 is most similar to item 72028 from your history with a catalog-property similarity of 0.70. It also has a session-based relationship with item 72028 with a co-visitation score of 2.00. Its popularity signal was 114. After applying the user's supported preferences, it moved from rank 5 to rank 4.

The 0.70 here is an internal catalog-property similarity score. It does not mean the two products are "70% similar."

---

## Frontend

The frontend is built with React and Vite and has four sections: Discover, System, Intent, and Trust.

Discover is the main view. The shopper enters an ID, an optional request, and a result count, or picks a quick intent shortcut or a recent request. The page shows the shopper's segment, how the request was interpreted, and any constraints that could not be verified.

Each recommendation card shows its ranking score and a grounded explanation. An evidence drawer opens the full record: the source history item, session support, popularity signal, intent adjustment, and base-to-final rank movement. A top-result comparison shows how the leading results differ.

---

## Evaluation

Each result below applies to a specific population. The numbers in different tables are not directly comparable, and none of them is a single "accuracy" figure for the whole system.

### Candidate Retrieval

**Population:** a prototype sample of validation users.
**Metric:** candidate hit rate, the share of users whose candidate pool contained at least one item they interacted with in the future period. This measures whether retrieval found anything relevant, not the quality of the final recommendations.

| Retrieval setup | Overall | Established | Low-history |
|---|---|---|---|
| Basic content | ~8% | ~9% | ~7% |
| Deeper content | ~10% | ~12% | ~8% |
| Content + co-visitation | ~13% | ~15% | ~11% |

Adding co-visitation gave the largest gain, which is why it stayed in the final system. Even so, most users' candidate pools contain no future positive item. Retrieval is the main bottleneck in Motive.

### Reranking

**Population:** only the 54 validation users whose candidate pool already contained at least one future positive item.
**What it measures:** how well the reranker orders candidates once retrieval has succeeded. These are conditional metrics, not full-system metrics.

| Metric | Baseline | Tree reranker |
|---|---|---|
| Precision@10 | 0.0481 | 0.0685 |
| Recall@10 | 0.2350 | 0.2988 |
| HitRate@10 | 0.3704 | 0.4444 |
| MRR | 0.1674 | 0.2116 |
| NDCG | 0.1658 | 0.2025 |
| ROC-AUC | | 0.7785 |

A HitRate@10 of 0.4444 means that for 44.44% of these 54 users, a future positive appeared in the top 10. It does not mean Motive finds a relevant item for 44.44% of all users. For most users, retrieval never surfaced a positive item, so the reranker had nothing to promote.

### Intent Parsing

**Population:** a frozen holdout of 26 natural-language requests.
**Baseline:** a deterministic rule-based parser.

| Parser | Correct | Accuracy |
|---|---|---|
| Rule-based baseline | 12 / 26 | 46.15% |
| Claude (Anthropic API) | 25 / 26 | 96.15% |

All outputs passed schema validation. The one miss was "Keep choices pretty conventional," which was expected to map to a popularity preference, but Claude returned no popularity preference.

With only 26 cases, this shows the parser handles the kinds of requests tested. It is not an estimate of real-world accuracy across all possible requests.

---

## Performance Engineering

Evaluation for established shoppers became very slow at one point. Each of those shoppers could have up to 20 history items, and finding content neighbors for each one meant computing similarity against a catalog of over 400,000 products. Across many users, the same large scans were repeated again and again.

The fixes were straightforward once the cause was clear:

| Fix | Why it helped |
|---|---|
| Normalize the sparse item matrix once | Similarity becomes a single sparse dot product with no per-query normalization |
| Dictionary item lookup | Item ID to row index becomes constant time |
| `np.argpartition` | Finds the top neighbors without sorting the whole score array |
| Content neighbor cache | Each item's neighbors are computed once and reused |
| Cache pre-warming | Common items are loaded before evaluation starts |

One evaluation run went from more than 14 minutes to roughly 5 seconds after these changes and cache warm-up. This was measured in my local project environment. It is not a formal production latency benchmark.

---

## Technology Stack

| Area | Technologies |
|---|---|
| Backend and ML | Python, NumPy, Pandas, SciPy, scikit-learn, FastAPI, Pydantic, Uvicorn |
| AI | Anthropic Claude for structured `UserIntent` parsing |
| Frontend | React, Vite |
| Testing and tooling | Pytest, Git, Git LFS |

---

## Testing

Motive has two layers of automated checks.

Unit and integration tests:

```
pytest -q
```

Current result: 37 passed.

Product regression suite:

```
python -m scripts.regression_suite
```

Current result: 158 / 158 checks passed.

The unit tests check that individual pieces work. The regression suite checks that the product behaves correctly end to end:

| Area | Covered cases |
|---|---|
| Routing | cold-start, low-history, and established users |
| Ranking | no-intent ranking, deterministic output, result counts, duplicate prevention |
| Intent | familiar + popular, exploratory + niche, intent movement bounds, rank movement |
| Unsupported constraints | brand, price, use case, and multiple constraints together |
| Evidence | provenance, co-visitation evidence, grounded explanations |

---

## Engineering Lessons

**Sparse data changes what a metric means.** With around 90% of September users being cold-start, a single headline number would hide most of the story. Every metric in this project needed a stated population before it could be read correctly.

**Retrieval matters more than reranking.** A better reranker improved ordering for the 54 users where retrieval succeeded, but it cannot help anyone whose candidate pool has no relevant item. The largest remaining gains are in retrieval, not in the model.

**Two similarity signals are not automatically redundant.** I expected content and co-visitation neighbors to overlap heavily. Measuring it showed they barely overlap at all, which changed the design from one merged score to two separate sources.

**Score blending needs matching scales.** An 85/15 weighting means nothing if the two inputs live on different numeric ranges. Normalizing each score before blending was a small fix for a bug that silently changed the whole ranking.

**Explanation testing catches ranking bugs.** The blending bug was not found by metrics. It was found because the explanations reported rank movement, and the movement looked wrong. Making the system explain itself also made it easier to check.

**Provenance should be recorded, not reconstructed.** Trying to explain a result after ranking means guessing. Recording the source history item and scores at candidate generation made accurate explanations simple.

**Anonymized data sets hard limits on explanations.** The system can only describe what the data supports. That is why explanations talk about item IDs and internal scores, and why brand and price requests are flagged instead of applied.

**The LLM should interpret, not decide.** Keeping Claude limited to producing a validated `UserIntent` object means its output can be tested on its own, and the ranking stays reproducible and explainable.

**Tests should cover product behavior.** Unit tests passing did not guarantee that, for example, an unsupported price request was flagged correctly. The regression suite exists to check those behaviors directly.

**Large artifacts and secrets need a plan from the start.** Git LFS keeps model and matrix files out of normal Git history, and keeping the API key in an environment variable means it never has to touch the repository.

---

## Current Limitations

1. Products are anonymized.
2. Brands, product names, prices, specifications, and retailer links cannot be verified.
3. Content metadata comes from the available snapshot, so content features are not perfectly time-separated from the evaluation period.
4. Reranker metrics are conditional on successful candidate retrieval and do not describe the full system.
5. Candidate recall is the main bottleneck.
6. The 85/15 intent weighting is hand-selected, not learned or calibrated.
7. Intent from new shoppers is parsed but does not currently change popularity ordering.
8. The intent parser holdout contains only 26 examples.
9. The full integrated system has not yet been rerun on the untouched September benchmark since the latest ranking, provenance, and intent changes.
10. There is no live retailer integration.
11. There is no live price retrieval.
12. There is no semantic product search.
13. The evaluation does not claim research-grade temporal purity.

---

## Future Improvements

- Stronger candidate retrieval, since it limits everything downstream.
- Sequential recommendation models that use the order of a shopper's actions.
- Richer behavioral modeling beyond session co-visitation.
- Learned intent weighting to replace the hand-selected 85/15 split.
- Richer, verified product metadata so constraints like brand and price can actually be checked.
- Stronger cold-start personalization, including letting intent affect new shoppers' results.
- A final evaluation of the integrated system on the untouched September data.

None of these are implemented yet.

---

## Getting Started

Motive currently runs locally. There is no public deployment.

### Prerequisites

- Python 3
- Node.js and npm
- Git LFS
- An Anthropic API key

### 1. Clone the Repository

Runtime artifacts are stored with Git LFS, so pull them after cloning:

```
git lfs install
git clone <repository-url>
cd Motive
git lfs pull
```

### 2. Set Up the Backend

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

### 3. Set the Anthropic API Key

```
export ANTHROPIC_API_KEY="your-key-here"
```

The key is read on the server from the `ANTHROPIC_API_KEY` environment variable. The frontend never has access to it, and it is not included in API responses.

### 4. Start the Backend

From the project root:

```
python -m uvicorn api.main:app --reload
```

### 5. Start the Frontend

In a second terminal:

```
cd frontend
npm install
npm run dev
```

Vite prints the local URL to open in your browser.

### Runtime Artifacts

The runtime artifacts pulled through Git LFS are enough to run the application:

| Artifact | Contents |
|---|---|
| `content_neighbors.pkl` | Cached content neighbors |
| `item_ids.npy` | Item IDs |
| `item_to_index.pkl` | Item ID to matrix row mapping |
| `normalized_item_matrix.npz` | Normalized sparse item-feature matrix |
| `reranker_covisitation.pkl` | Co-visitation neighbors |
| `reranker_tree.pkl` | Final tree reranker |
| `user_history_count.pkl` | History counts per user |
| `user_item_strength.pkl` | Weighted user-item interaction strength |
| `weighted_popularity.pkl` | Weighted popularity scores |

The raw Retailrocket CSV files are not included in Git. They are only needed to rebuild artifacts or retrain the reranker. The training dataset (`reranker_training_data.pkl`) and the unused logistic reranker are also excluded.

### Secrets and Repository Hygiene

Git ignores `.env`, the virtual environment, `node_modules`, the frontend build output, raw CSV datasets, and training-only artifacts. Local `.env` files are ignored so secrets are not committed. A scan of the staged repository before release found no `sk-ant-` key.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/recommend/{user_id}` | Recommendations for a shopper without a request |
| POST | `/recommend/intelligent` | Recommendations with a natural-language request |

Interactive Swagger docs are available at `/docs` on the local backend while it is running.

---

## Project Structure

```
Motive/
├── api/                # FastAPI app and endpoints
├── artifacts/          # Runtime artifacts (Git LFS)
├── frontend/           # React and Vite frontend
├── notebooks/          # Exploration and analysis
├── scripts/            # Artifact building, training, evaluation, regression suite
├── src/                # Recommendation pipeline, intent, evidence, explanations
├── tests/              # Unit and integration tests
├── README.md
├── requirements.txt
├── pytest.ini
├── .gitignore
└── .gitattributes
```

---

## Project Status

Motive runs end to end locally, and the code is on GitHub. At the time of writing:

- 37 / 37 pytest tests pass
- 158 / 158 regression checks pass
- the frontend production build succeeds
- the familiar + popular flow has been tested
- the exploratory + niche flow has been tested
- the evidence UI has been manually inspected

The next major milestone is a final integrated evaluation on the untouched September data.