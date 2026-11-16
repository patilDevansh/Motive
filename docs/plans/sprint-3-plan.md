# Sprint 3 Plan — Motive

**Status: PROPOSED for team review. Nothing below is a team decision until the team accepts it.**

| | |
| --- | --- |
| Product | Motive |
| Team | Motive (team name as registered with the course: not confirmed) |
| Sprint | 3 |
| Sprint completion date | **TBD — not found in any material available** |
| Revision | 0 (draft) |
| Revision date | November 15, 2026 |
| Prepared from | Repository at `main` `d61236b`, Scrum board, course handout and help page. See `docs/reports/sprint-2-audit.md` |

The Sprint 1 and Sprint 2 plan documents and the release plan were not available when this was written. Section order follows what `docs/reports/sprint-1.md` cites from the Sprint 1 plan (goal, completion date, hours and points, roles, initial assignment). Story names, story points and wording must be reconciled with those documents.

Markers used below: **(C)** confirmed from the repository or board, **(P)** proposed here and open to change.

## 1. Sprint goal

**(P)** A store owner can upload their catalog and shopper events in the browser, see how each product performed over a chosen date range, and get recommendations drawn from that same imported data.

This is the Sprint 2 extended goal quoted in the S2-05 task file ("an owner can upload store data, inspect product performance, and request recommendations from that same imported dataset"). Sprint 2 delivered its server half: import, storage and counts. The browser half and the recommendation half remain.

## 2. Starting point

- **(C)** Done and merged: S2-03 catalog import, S2-04 event import, S2-07 per-product counts, S2-08 date-range filter. 44 tests pass on `main`.
- **(C)** Unfinished from Sprint 2: S2-01, S2-02, S2-05 (spec only), S2-06, S2-09, S2-10.
- **(C)** Sprint 2 result: 4 of 10 tasks merged, 23 of the estimated hours that are recorded. Estimates for the other six tasks were never recorded, so a planned total for Sprint 2 cannot be stated.
- **(C)** Three integration gaps block the goal: the upload format mismatch, the missing dev proxy to the store service, and no owner authentication. Details are in the audit.

## 3. User stories, tasks and estimates

Priority order is top to bottom. Hours are ideal hours. All story points are **(P)**.

### Story 1 — Store-data-import (priority 1, 5 points)
As a store owner, I want to upload my product catalog and shopper events from the browser, so that Motive works from my own store's data.

Acceptance criteria:
1. Choosing a valid catalog CSV and pressing upload shows how many products were added and updated.
2. Choosing a valid events CSV shows how many events were added and skipped.
3. A file with bad rows shows each row's line, field and message, and nothing from that file is stored.
4. Uploading the same file twice does not duplicate products or events.

| Task | Title | Owner | Est. h | State |
| --- | --- | --- | --- | --- |
| S3-03 | Accept CSV file uploads on the catalog and event import endpoints | Devansh Patil **(P)** | 4 | Spec, code and tests prepared on local branch `task/S3-03`; not pushed |
| S2-05 | Show import results after a store owner uploads a catalog CSV | Aditya Bashyam **(C)** | 5 **(C)** | Spec pushed November 5; no implementation |
| S3-06 | Show import results after a store owner uploads an events CSV (was S2-06) | TBD | 4 **(P)** | Not started |

Story total: 13 h.

### Story 2 — Product-numbers (priority 2, 8 points)
As a store owner, I want to see how each of my products is performing, so that I can decide what to promote or fix.

Acceptance criteria:
1. A dashboard lists every catalog product with its views, carts and purchases.
2. Choosing a start and end date changes the counts to that window.
3. Products with no activity are listed with zeros.
4. The owner can browse the imported catalog page by page.

| Task | Title | Owner | Est. h | State |
| --- | --- | --- | --- | --- |
| S3-10 | Show per-product counts with a date range on a dashboard screen (was S2-10) | TBD | 6 **(P)** | Not started |
| S3-09 | Browse the imported catalog page by page (was S2-09) | TBD | 5 **(P)** | Not started |
| S3-07 | Add view-to-cart and view-to-purchase rates to product stats | Jaisree David Ravikumar **(P)** | 4 **(P)** | Candidate only. S2-07 lists conversion rates as out of scope and the Sprint 1 card is titled "Product counts and conversion rates" |
| S3-08 | Sort product stats by a chosen count | Jaisree David Ravikumar **(P)** | 4 **(P)** | Candidate only |

Story total: 19 h. S3-07 and S3-08 are suggestions so that Jaisree has two Sprint 3 tasks in her story; she should replace them with her own.

### Story 3 — Store-recommendations (priority 3, 8 points)
As a store owner, I want recommendations that come from my own imported products and events, so that the results are about my store and not the Retailrocket demo data.

Acceptance criteria:
1. For a store with imported events, a request returns that store's most popular available products.
2. For a shopper with imported history, a request returns products related to that history.
3. Products and events from other stores never appear.

| Task | Title | Owner | Est. h | State |
| --- | --- | --- | --- | --- |
| S3-01 | Return a store's most popular available products from imported events (was S2-01) | TBD | 5 **(P)** | Not started |
| S3-02 | Return products related to a shopper's imported history (was S2-02) | TBD | 7 **(P)** | Not started. Stretch: see risks |

Story total: 12 h.

### Story 4 — Store-owner-access (priority 4, 3 points)
As a store owner, I want my store's data to be reachable only with my store's key, so that nobody else can read or overwrite it.

Acceptance criteria:
1. With authentication enabled, a request without the store's key is refused.
2. One store's key cannot read or change another store.
3. Creating a new key stops the old one working.

| Task | Title | Owner | Est. h | State |
| --- | --- | --- | --- | --- |
| S3-04 | Require a store API key on store endpoints when authentication is enabled | Devansh Patil **(P)** | 5 | Spec, code and tests prepared on local branch `task/S3-04`; not pushed |

Story total: 5 h. "Store-owner-access" is a new story name **(P)**; it needs a place in the product backlog.

### Totals

| | Tasks | Hours | Points (P) |
| --- | --- | --- | --- |
| Story 1 Store-data-import | 3 | 13 | 5 |
| Story 2 Product-numbers | 4 | 19 | 8 |
| Story 3 Store-recommendations | 2 | 12 | 8 |
| Story 4 Store-owner-access | 1 | 5 | 3 |
| **Sprint 3** | **10** | **49** | **24** |

## 4. Capacity and scope

- The course requires two tasks per student per sprint, so ten tasks is the minimum for a five-person team. Team size is inferred, not confirmed: four people have commits, and Sprint 2 had ten tasks.
- Hours each member can give this sprint are **not known**. No capacity figure is assumed here.
- The only velocity evidence is Sprint 2: 4 tasks and 23 estimated hours merged, by two members. Against that, 49 hours and 10 tasks is a stretch for the team as a whole.
- Because of that, the order of work matters more than the total. If only part of the sprint lands, this order still produces something demonstrable:
  1. S3-03, then S2-05: upload a catalog in the browser.
  2. S3-06: upload events.
  3. S3-10: the dashboard over data that was just uploaded.
  4. S3-01: popular products for the store.
  5. S3-09, S3-07, S3-08, S3-04.
  6. S3-02 last.

## 5. Dependencies

| Task | Depends on | Note |
| --- | --- | --- |
| S2-05, S3-06 | S3-03 | The screens send `multipart/form-data` with a `file` field. `main` accepts only raw `text/csv` until S3-03 merges |
| S2-05 | Response field name | The spec expects `imported`; the service returns `inserted`. The spec already confines this to `frontend/src/services/importApi.js` |
| S2-05, S3-06, S3-09, S3-10 | Dev proxy | `frontend/vite.config.js` must proxy `/stores` to the store service, and the store service needs a port other than 8000 while `api.main` runs. Unowned; smallest fix is inside the first UI task's PR |
| S3-06 | S2-05 | Reuses `useCsvUpload.js` from S2-05 |
| S3-09 | S2-05 | S2-05 links to `#catalog`; uses `GET /stores/{id}/products` (exists) |
| S3-10 | none new | Uses `GET /stores/{id}/products/stats` with `start` and `end` (exists) |
| S3-07, S3-08 | none new | Extend `src/product_event_stats.py` |
| S3-01 | none new | Reads the `products` and `events` tables; needs no model artifacts |
| S3-02 | Model artifacts | `artifacts/*` are Git LFS files. Recommender tests cannot run from a clone without them, and `docs/SPRINT_WORKFLOW.md` says they are not yet on `origin` |
| S3-04 | none | Off by default, so it does not block the screens. Touches `api/store.py`, as S3-03 does; a trial merge of both was clean |
| All Sprint 3 tests | CI change | The workflow selects `tests/test_S2_*.py` only. The planning branch widens it to `tests/test_S[0-9]*_*.py` |

## 6. Risks

1. **Overcommitment.** Six tasks carried from Sprint 2 had no branch after the sprint. Mitigation: the work order in section 4.
2. **Unknown owners.** Five carried tasks have no recorded owner. Mitigation: assign them at sprint planning before any spec is written.
3. **Task IDs.** A task file's `sprint:` and folder must match the sprint it is submitted in, and an ID can be used once. Carried tasks therefore need new `S3-` IDs and new task files written by their owners. S2-05 already has a pushed `sprint: 2` file and base tag; see decision 4.
4. **S3-02 may not be testable** until the LFS artifacts are available to every member and to CI.
5. **Unseen course documents.** This plan may miss a required section or use different story names from the release plan.

## 7. Team roles

| Role | Member | Source |
| --- | --- | --- |
| Scrum Master | Devansh Patil | Sprint 1 role per `docs/reports/sprint-1.md`. Sprint 3 role not confirmed |
| Product Owner | TBD | Not recorded |
| Developers | Devansh Patil, Jaisree David Ravikumar, Aditya Bashyam, Krrish Mujoo, and a fifth member if there is one | Git history |

## 8. Initial task assignment

| Member | First task | Second task | Basis |
| --- | --- | --- | --- |
| Devansh Patil | S3-03 | S3-04 | **(P)** Continues his Sprint 2 import service |
| Jaisree David Ravikumar | S3-07 | S3-08 | **(P)** Continues her Sprint 2 stats work; her choice |
| Aditya Bashyam | S2-05 (carried) | S3-06 | S2-05 **(C)** from its task file; S3-06 **(P)** because it reuses his upload hook |
| TBD | S3-01 | S3-02 | Owner of S2-01/S2-02 not recorded |
| TBD | S3-09 | S3-10 | Owner of S2-09/S2-10 not recorded |

## 9. Initial Scrum board

Proposed state at the start of Sprint 3. The live board could not be edited from here.

| To do | In progress | Done |
| --- | --- | --- |
| S3-01 Store popularity recommendations | — | — |
| S3-02 Personalized imported-data retrieval | | |
| S3-03 CSV file uploads on import endpoints | | |
| S3-04 Store API key | | |
| S2-05 Catalog upload and results screen | | |
| S3-06 Event upload and results screen | | |
| S3-07 Conversion rates in product stats | | |
| S3-08 Sort product stats | | |
| S3-09 Imported catalog browser | | |
| S3-10 Product-performance dashboard | | |

S3-03 and S3-04 stay in To do until their branches are pushed: local work is not sprint progress.

Corrections the existing board needs first:

| Card | Shows | Should show | Evidence |
| --- | --- | --- | --- |
| S2-03 | In Progress | Done | PR #3 merged, `5ce7699` |
| S2-04 | In Progress | Done | PR #4 merged, `7a4beb4` |
| S2-07 | Todo | Done | PR #5 merged, `d61236b` |
| S2-08 | Todo | Done | On `main` through PR #5 |
| S2-01, S2-02, S2-06, S2-09, S2-10 | Todo | Closed as carried to S3-01, S3-02, S3-06, S3-09, S3-10 | No work exists under the S2 IDs |
| S2-05 | Todo | Per decision 4 | Spec only |

Every Sprint 3 card should carry owner, sprint, estimate and acceptance criteria (`docs/SPRINT_WORKFLOW.md`, step 1). To create the cards with the GitHub CLI, signed in as the board owner:

```bash
for t in \
  "S3-01: Store popularity recommendations" \
  "S3-02: Personalized imported-data retrieval" \
  "S3-03: CSV file uploads on import endpoints" \
  "S3-04: Store API key on store endpoints" \
  "S3-06: Event upload and results screen" \
  "S3-07: Conversion rates in product stats" \
  "S3-08: Sort product stats" \
  "S3-09: Imported catalog browser" \
  "S3-10: Product-performance dashboard"; do
  gh project item-create 3 --owner patilDevansh --title "$t"
done
```

## 10. Initial burnup chart

| | Value |
| --- | --- |
| Total scope | 49 hours, 10 tasks |
| Completed at sprint start | 0 hours, 0 tasks |
| Sprint days | TBD (needs the sprint start and completion dates) |

The chart starts with the scope line at 49 hours and the completed line at 0. The ideal line runs from 0 on the first day to 49 on the completion date. No daily values are filled in, because none exist yet. A task counts as completed on the day its PR merges.

## 11. Scrum times

Not recorded in any material available. To be filled in by the team: days, time, place or channel, and TA meeting time.

## 12. Decisions needed from the team

1. Sprint 3 start and completion dates.
2. The roster, and who owns S3-01/S3-02 and S3-09/S3-10.
3. Whether the task IDs S3-01 to S3-10 are accepted. IDs name the git tags, so this must be settled before anyone pushes a base tag.
4. S2-05: finish it under its existing ID for Sprint 2 if that sprint is still open, or write a new Sprint 3 task. Ask the TA whether a task specified in Sprint 2 and finished in Sprint 3 can be submitted for Sprint 3.
5. Whether S3-04 (owner access) belongs in this sprint, or whether Devansh should take S3-01 instead if nobody owns the recommendation tasks.
6. Jaisree's two tasks.
7. Story points per story, and hours each member can commit.
