# Working Agreement

## Subissue identity

- This workflow applies when the requested implementation work is a GitHub subissue of a weekly-goal issue.
- Before creating a branch, confirm the subissue number, its parent weekly-goal issue number, and the V2 layer mapped to that weekly goal. The parent weekly-goal issue and its target layer define the broader outcome; the subissue acceptance criteria define the work for this branch.
- If the subissue, parent relationship, target layer, acceptance criteria, or shared documentation is missing or conflicts with another source, do not invent a resolution or begin implementation. Report the conflict and request clarification.

## Branches

- Treat each requested subissue as an independent implementation task, including subissues belonging to a larger weekly-goal issue.
- Each subissue must be developed in its own feature branch. Do not implement the task directly on `develop`.
- Before creating the feature branch, fetch the latest remote refs and make sure the local `develop` branch is up to date with `origin/develop` (or the repository's configured remote equivalent). Update `develop` from the remote when it is behind, then create the feature branch from that updated `develop` tip. Do not update or switch branches in a way that would overwrite or discard existing user changes; if the working tree or branch state makes a safe update unclear, preserve the changes and ask for direction.
- If the work depends on unmerged work from another branch, do not silently base on, duplicate, or mix in that work; report the dependency and request direction.
- Name feature branches with the `codex/ft-` prefix followed by a short, descriptive kebab-case name. For example: `codex/ft-add-transaction-endpoint`.
- Keep a branch focused on one subissue. Do not mix unrelated fixes or cleanup into it.

## Commits

- Make a small sequence of meaningful, focused commits so the history shows the main implementation steps and is easy to review. Do not put the entire task into one final commit, and do not create a commit for every individual edit or trivial change.
- Create a commit when a coherent, reviewable implementation step is complete. A step should group the changes that belong together and leave the project in a sensible state whenever practical.
- Prefer one concern per commit. Examples include:
  - installing and configuring a required package (combine these when they form one setup step);
  - adding a migration or updating a database table/schema;
  - adding environment variables together with their documentation;
  - implementing a service or other distinct business-logic layer;
  - adding an endpoint or route that uses that service;
  - adding or updating tests alongside the behavior they cover, or as a distinct step when appropriate.
- Split commits at meaningful boundaries in the actual task; these examples are guides, not a required number or fixed sequence of commits.
- Use a clear, imperative commit subject and follow the repository's Conventional Commits convention where applicable, such as `feat(api): add transaction endpoint` or `fix(db): handle duplicate transaction ids`.
- Do not combine generated files, formatting-only changes, refactors, or unrelated bug fixes with a functional change unless they are required for that change.
- Before handing off the work, verify the branch and commit history, and summarize the purpose of each commit.

## Reviewability

- Keep each commit buildable and testable whenever practical.
- Update relevant documentation and environment-variable examples in the same focused step that introduces the behavior they describe.
- If a change cannot be isolated cleanly, explain the dependency in the commit message or handoff notes.

## Subissue Workflow

For every subissue, follow this workflow in order:

1. Locate the subissue in GitHub and read its complete description, parent issue, acceptance criteria, labels, and any linked context before making changes. Confirm that the parent is the weekly-goal issue and identify its mapped V2 layer. Do not rely only on the task prompt.
2. Read the shared product and architecture documentation before implementing anything:
   - `docs/V2/context.md` for product rules, terminology, boundaries, and AI behaviour;
   - `docs/V2/architecture.md` for shared technical decisions and implementation conventions;
   - the layer document corresponding to the parent weekly issue. For example, a Week 1 subissue uses `docs/V2/layers/01-transaction-foundation.md`, a Week 2 subissue uses `docs/V2/layers/02-cashflow-and-reserve.md`, and so on through the numbered files in `docs/V2/layers/`;
   - any dependency layer documents named in the target layer's `Depends on` section.
3. After confirming the issue and documentation, make a best-effort attempt to move the subissue item to the project's `In Progress` column/status using the available GitHub/project tools. Verify the status when possible. If the item is already there, leave it as is. If the project or item cannot be found, the required tools are unavailable, or the update fails, tell the user what prevented the update and continue with the implementation; a status update is not a reason to block or stop the task.
4. Ensure `develop` is current with the remote as described in Branches, then create or switch to a dedicated `codex/ft-...` branch for that subissue. Do not switch away from or overwrite unrelated user work.
5. Implement the work in a meaningful sequence of focused commits using clear Conventional Commit messages, following the guidance in Commits.
6. Run the relevant automated tests. If no suitable test exists, perform an appropriate smoke test and report exactly what was checked. Verify every acceptance criterion before handoff and map each criterion to its test, smoke-test result, or other verification evidence in the pull request.
7. Review the final diff and commit history to confirm that the branch contains only the subissue's work and that the commits clearly show how it was built.
8. Push the feature branch to the remote and set its upstream when needed, for example: `git push -u origin codex/ft-add-transaction-endpoint`.
9. Open a pull request from the feature branch into `develop`.
10. After opening the pull request, make a best-effort attempt to move the corresponding subissue item to the project's `In Review` column/status if GitHub or project automation has not already done so. Verify the status when possible. If it is already in `In Review`, leave it as is. If the project or item cannot be found, the required tools are unavailable, or the update fails, tell the user what prevented the update and continue the remaining handoff steps; a status update is not a reason to block or stop the task.
11. Include a brief pull request summary covering what was implemented, how it was tested or smoke-tested, and any relevant follow-up work.
12. Link the corresponding GitHub subissue in the pull request and include a closing keyword such as `Closes #123`, so that subissue closes automatically when the pull request is merged into `develop`. Do not close the parent weekly-goal issue; reference it separately, for example `Part of #456`.
