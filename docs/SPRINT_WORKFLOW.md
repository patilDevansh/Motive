# Sprint workflow and integration

Team Scrum board: https://github.com/users/patilDevansh/projects/3
Submission app: https://tasks.grepthink2.com/cse115a/dashboard
Current help: https://tasks.grepthink2.com/cse115a/help

Krrish's main branch is merged with history preserved. Jaisree's product_stats.py and its tests remain. The upstream README's test totals are historical claims, not fresh validation of this integration.

## Each new task
1. Add a board card with owner, sprint, estimate and acceptance criteria.
2. Branch from current main with the task ID in the branch name.
3. Commit only docs/tasks/sprint-N/ID.md, tag ID-base and push both before implementation.
4. Implement and test every criterion. Open one PR per task from the task owner's GitHub account.
5. Have a teammate review; merge after tests pass. Do not substitute AI review for teammate review.
6. Tag the actual merge commit ID-done and push it. Add the merged PR to the matching sprint.
7. Re-check, inspect results and submit only the two eligible tasks. Record actual metrics for the separate Canvas paragraph.

## Course app
Sign in with UCSC Google; join with the instructor code; connect your GitHub identity. Repository owner installs AIAugmentedSWE for Only select repositories → patilDevansh/Motive. Every submitter needs repository write access. The live app accepts Sprints 2–4; obtain TA guidance for Sprint 1.

## Runtime artifacts
The imported artifacts are upstream Git LFS pointers. Install Git LFS, fetch upstream LFS objects and push them to origin before treating the integrated recommender as runnable. Never load untrusted pickle files. Code integration alone does not verify model runtime.
