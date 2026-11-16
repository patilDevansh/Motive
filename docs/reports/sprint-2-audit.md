# Motive — Sprint 2 status audit and outstanding work

Prepared November 15, 2026 for team review. This is an audit of repository evidence, not a record of meetings, hours or decisions.

## What was inspected

| Source | Access | Notes |
| --- | --- | --- |
| `patilDevansh/Motive` on GitHub | Read (fresh clone, `main` at `d61236b`) | Branches, tags, task files, tests |
| Scrum board, GitHub Project 3 | Read only | 15 cards, read November 15 |
| Submission app help page (`tasks.grepthink2.com/cse115a/help`) | Read | Submission rules and FAQ |
| Course handout "Sprint Task Specifications" (linked from `docs/reports/sprint-1.md`) | Read | Task rules, workflow, 10-point rubric |
| Local folder `CSE 115A 2` | Read | Holds only a `Motive` checkout on `codex/S2-04`, 7 commits behind `origin/main` |
| Course Google Drive folder | **Not readable** | Sprint 1 and Sprint 2 plans, release plan and any instructor templates were not seen |
| Submission dashboard | **Not readable** (needs UCSC sign-in) | Deadlines, submitted tasks, check results and grades were not seen |
| GitHub pull-request pages | Not readable in detail | PR authors, titles and reviews were not verified; merges are known from git history |

## Confirmed from evidence

### Course requirements
- This term the app accepts Sprint 2, Sprint 3 and Sprint 4. Each sprint is two merged pull requests per student.
- Each student owns at least two tasks per sprint. Each task: sole assignee, estimate of 2 hours or more, a different slice from the other task, an ID used once in the repository, finishable in 2–3 days including review.
- Task file at `docs/tasks/sprint-N/<id>.md` with front matter `id`, `story`, `sprint`, `assignee`, `estimate_hours`, a title, and the sections Description, Specs, Requirements, Acceptance criteria. A Tests section is optional.
- The task file is the first commit on the branch, alone, tagged `<id>-base` and pushed before any code. The branch name and the PR title contain the task ID. The PR is opened from the owner's GitHub account, reviewed by a teammate, and changes exactly one file under `docs/tasks/`.
- `<id>-done` is pushed on the merge commit on the default branch before the PR is added in the app.
- Each task has a card on the team Scrum board. The app cannot see the board; the student confirms it with a checkbox.
- Canvas takes one paragraph per sprint: what the task implemented, two metrics chosen from the task's View results page, their values, and a comparison.
- Grading per task (10 points): Scope 1, Specs 2, Acceptance criteria 2, Test quality 2, Tests pass 2, Process 1. The sprint score is the average of the two tasks; a missing task scores 0.

### Sprint 2 task status

| Task | Board title | Owner (from task file) | Est. h | Repository state | Board status | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| S2-01 | Store popularity recommendations | not recorded | — | No task file, branch or tag | Todo | Not started |
| S2-02 | Personalized imported-data retrieval | not recorded | — | No task file, branch or tag | Todo | Not started |
| S2-03 | Catalog CSV validation and persistence | Devansh Patil | 7 | Merged, PR #3, merge commit `5ce7699`; `S2-03-base` on a spec-only commit | In Progress | **`S2-03-done` tag missing.** Board stale |
| S2-04 | Event CSV validation and persistence | Devansh Patil | 7 | Merged, PR #4, merge commit `7a4beb4`; `S2-04-base` on a spec-only commit | In Progress | **`S2-04-done` tag missing.** Board stale. See risk below |
| S2-05 | Catalog upload and results screen | Aditya Bashyam | 5 | Spec-only commit `6d17809` pushed November 5 with `S2-05-base`; no implementation | Todo | Not implemented |
| S2-06 | Event upload and results screen | not recorded | — | No task file, branch or tag | Todo | Not started |
| S2-07 | Product event-count API | Jaisree David Ravikumar | 5 | Merged, PR #5, `S2-07-done` on merge commit `d61236b` | Todo | Complete. Board stale |
| S2-08 | Analytics date-range filtering | Jaisree David Ravikumar | 4 | Merged through PR #6 **into `task/S2-07`**, then to `main` inside PR #5; `S2-08-done` on `61e6dc6` | Todo | **`S2-08-done` is not a merge commit on `main`.** Board stale |
| S2-09 | Imported catalog browser | not recorded | — | No task file, branch or tag | Todo | Not started |
| S2-10 | Product-performance dashboard | not recorded | — | No task file, branch or tag | Todo | Not started |

Four of ten Sprint 2 tasks are merged (23 estimated hours: 7 + 7 + 5 + 4). Six are unfinished.

### Tests on `main` at `d61236b` (run November 15, Python 3.13, fresh clone)
- CI selection (`tests/test_S2_*.py tests/test_product_stats.py`): **44 passed**.
- Recommender tests: 7 files fail at collection and 8 tests fail, all because `artifacts/*` are Git LFS pointer files in this clone. The clone skipped LFS downloads, so this does not show whether the LFS objects exist on `origin`; `docs/SPRINT_WORKFLOW.md` says they still have to be pushed there.
- The CI workflow only selects `tests/test_S2_*.py`, so Sprint 3 task tests would not run in CI as written.

### Board
- Fifteen cards exist: five Sprint 1 cards and S2-01 to S2-10. No card shows an assignee, sprint or estimate, although `docs/SPRINT_WORKFLOW.md` step 1 calls for owner, sprint, estimate and acceptance criteria.
- All five Sprint 1 cards are in Todo. Status of that work was not established here.
- There are no Sprint 3 cards.

### Integration gaps found in the code
1. **Upload contract mismatch.** The S2-05 spec sends `multipart/form-data` with a `file` field and expects `{"imported": N, "updated": M}`. The service on `main` reads a raw `text/csv` body and returns `{"inserted": N, "updated": M}`.
2. **The React app cannot reach the store service.** `frontend/vite.config.js` proxies only `/recommend` and `/health` to port 8000. The store endpoints live in a separate app (`api.store:app`). `api.main:app` and `api.store:app` both default to port 8000.
3. **No owner authentication.** `docs/STORE_IMPORTS.md` and the S2-03/S2-04 specs say the store service must stay on localhost until it exists. No card covers it.

## Not confirmed (assumptions and gaps)
- **Deadlines.** No Sprint 2 or Sprint 3 date was found. Whether Sprint 2 is still open in the app is unknown.
- **Team roster.** Commits show four people: Devansh Patil, Jaisree David Ravikumar, Aditya Bashyam, Krrish Mujoo. Ten Sprint 2 tasks at two per student suggests five members; a fifth member, if any, is not identified.
- **Owners of S2-01, S2-02, S2-06, S2-09, S2-10.** Not recorded anywhere inspected.
- **Whether Sprint 2 was submitted** in the app by anyone, and any check results or grades.
- **PR details.** Who opened PRs #3–#6, their titles and reviews. Git shows PRs #3 and #4 were merged by the account `Jaisree25`.
- **Other required artifacts.** A Sprint 2 report, review, retrospective, burnup chart or revised release plan may be required by documents in the Drive folder. None is in the repository; `docs/reports/sprint-1.md` is the only report.
- **Scrum meetings, attendance, hours worked.** No record was found. None is stated here.

## Actions before Sprint 2 can be submitted

For Devansh (S2-03, S2-04):
```bash
git fetch origin
git tag S2-03-done 5ce7699ea43eaadb6b966e9e1f1ad616ed117875
git tag S2-04-done 7a4beb4741fc50a35fb2e57400c2d9e8a6a7ee5c
git push origin S2-03-done S2-04-done
```
Then move both cards to Done, add each merged PR in the app, read the checks, and write the Canvas paragraph from the View results page. No metric values exist yet, so no paragraph has been drafted.

Risk on S2-04: the branch `codex/S2-04` was started on top of the S2-03 branch, so its history begins with the S2-03 commits. If the app reports that the task file was not committed first, the handout's rule for merged PRs applies: submit anyway and lose the Process point, and do not rewrite history.

For Jaisree (S2-08): the handout defines `-done` as the merge commit on the default branch, and S2-08 has no merge commit of its own on `main`. Ask the TA before moving the tag.

For Aditya (S2-05): one spec exists and no second task. If Sprint 2 is closed, see the ID decision in `docs/plans/sprint-3-plan.md`.

For the team: correct the board statuses listed above, and confirm with the TA how unfinished Sprint 2 tasks should be carried.
