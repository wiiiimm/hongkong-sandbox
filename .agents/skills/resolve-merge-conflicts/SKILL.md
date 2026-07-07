---
name: resolve-merge-conflicts
description: "Resolve git merge/rebase conflicts non-destructively — preserving the intent of BOTH sides — and hand off to a human when a conflict can't be resolved safely. Use when a branch or PR has conflicts with its base ('this branch has conflicts that must be resolved', GitHub mergeable=CONFLICTING / mergeStateStatus=DIRTY), when a rebase / merge / cherry-pick / stash / revert stops with conflict markers (<<<<<<< ======= >>>>>>>), when a PR is behind base and needs updating, when syncing a long-lived branch or back-merging a hotfix, or when deciding rebase vs merge. Covers the safe-resolution rules (no blind -X ours/theirs, hunk-by-hunk with diff3, abort/reflog escape hatches, verify-after), the rebase ours/theirs inversion, lockfile/rename/semantic conflicts, and the escalate-when-stuck criteria."
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "1.1.0"
---

# Resolve merge conflicts (non-destructively)

Resolve git conflicts so that **both sides' intent survives**, verify the result,
and **stop and ask a human** the moment a safe resolution isn't obvious. The git
mechanics are the easy part; the danger is *silently dropping someone's work* — a
blind "take theirs," a clean-looking textual merge that's logically broken, or a
force-push over a teammate's commits.

Command recipes live in [`reference/playbook.md`](./reference/playbook.md) (load on
demand). This body is the decision rules.

## First: rebase or merge?

You update a feature/PR branch against its base one of two ways. Either is fine —
pick by context, not dogma:

| | `git rebase origin/main` | `git merge origin/main` |
| --- | --- | --- |
| History | linear (replays your commits) | adds a merge commit |
| Conflicts | may re-hit the **same** conflict per replayed commit (turn on `rerere`) | resolve **once** |
| Push after | `--force-with-lease` (rewrites your branch) | normal push |
| Best for | your **own** unshared PR branch | a branch **others** also commit to |

In a **squash-merge** repo (see
[`git-trunk-branch-and-pr-automation`](../git-trunk-branch-and-pr-automation/SKILL.md))
the feature branch's history is flattened at merge anyway, so a merge commit on the
branch is harmless — when a rebase keeps re-conflicting, **merge instead** and
resolve once. **Never rebase a branch other people are actively committing to.**

## The non-negotiable safety rules

1. **Never blind-resolve a whole side.** `-X ours` / `-X theirs` (strategy options)
   and `git checkout --ours/--theirs <file>` take one side *wholesale* and throw the
   other away silently. They're only correct for files you will **regenerate** (e.g.
   lockfiles) or a file that genuinely should be one side entirely — never as a
   "make the markers go away" shortcut.
2. **Resolve hunk-by-hunk, preserving both intents.** A conflict means both sides
   changed the same region. The correct result is usually **neither** side verbatim
   but a combination. Turn on **`diff3`/`zdiff3`** so you can see the common ancestor
   and reason about what *each* side changed *from* (recipe in the playbook).
3. **Know the rebase ours/theirs inversion.** During `git merge`, `ours`=your branch,
   `theirs`=incoming. During `git rebase`, it's **flipped**: `ours`=the branch you're
   replaying *onto* (e.g. `main`), `theirs`=*your* commits. Acting on the wrong one
   discards exactly the work you meant to keep.
4. **Keep the escape hatch ready.** `git merge --abort` / `git rebase --abort` /
   `git cherry-pick --abort` returns you to a clean pre-conflict state. If unsure,
   **abort and reassess** rather than push a half-resolved tree. `git reflog` +
   `ORIG_HEAD` recover from a bad finish.
5. **Force-push only `--force-with-lease`, only your own PR branch.** Plain
   `--force` clobbers teammate commits pushed since your last fetch; `--with-lease`
   refuses if the remote moved.
6. **Never commit conflict markers.** Run `git diff --check` **and**
   `git diff --cached --check` (staged markers won't show in the unstaged diff after
   `git add`), plus a grep for `<<<<<<<`, before `--continue`/commit.

## The loop

```text
1. UNDERSTAND  → what's conflicting + why (mergeable status, conflict list, diff3)
2. CLASSIFY    → per file: content · rename/delete · lockfile/generated · binary · semantic
3. RESOLVE     → hunk-by-hunk, both intents; regenerate (don't hand-merge) lockfiles
4. VERIFY      → no markers; build + tests; diff sanity (no unrelated lines vanished)
5. CONTINUE    → git add; --continue / commit; push (--force-with-lease if rebased)
        │
        └─ at ANY step, if a safe resolution isn't clear → ABORT or stop → HAND OFF
```

## Conflict types — and how each is resolved

- **Content** (same lines changed) → the default: merge both intents by hand.
- **Rename/delete & add/add** → decide whether the file should exist and where; don't
  let one side's deletion silently win. (`git status` labels these.)
- **Lockfiles** (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `Cargo.lock`) →
  **do not hand-merge.** Take one side, then **regenerate** from the merged manifest
  (`npm install --package-lock-only` / `pnpm install --lockfile-only` /
  `cargo generate-lockfile` / etc.) so the lock matches its resolved manifest
  (`package.json`, `Cargo.toml`, …). This is the *legitimate* use of "take one side."
- **Generated/build output** → regenerate from source, never merge by hand.
- **Binary** → you can't merge text; pick a side deliberately or escalate.
- **Semantic** → the file merges with **zero markers** but is logically broken (one
  side renamed a function the other side calls). Textual success ≠ correctness —
  **only build + tests catch these.**

## Escalate to a human when…

Hand off (with context) rather than guess when:

- The conflict is a **genuine design clash** — both sides deliberately changed the
  same logic in incompatible ways; only the authors can say which intent wins.
- It's in code whose **intent you can't determine**, or in **migrations / schema /
  data** files where a wrong merge corrupts state.
- A **lockfile regeneration** pulls in unexpected dependency changes.
- The branch is from a **fork / untrusted PR** — you can't safely run its checked-out
  code or push to it (consistent with the fork-safety rule in
  [`autonomous-pr-driver`](../autonomous-pr-driver/SKILL.md)). Validate via API; don't
  resolve locally.
- A rebase keeps re-conflicting across many commits, or the conflict spans many files
  beyond what you can verify.

**How to hand off:** state *what* files conflict, *what* you tried, and *why* you
stopped — then leave the branch in a clean (aborted) state, or push the partial
resolution to a clearly-labelled branch and ask. Same posture as the PR driver's
**never-self-merge**: when in doubt, a human decides.

## Verify (before you call it done)

- `git diff --check` → no leftover conflict markers / whitespace errors.
- **Build + run the tests** — the only thing that catches semantic conflicts.
- **Diff sanity**: compare against both parents; confirm no *unrelated* lines were
  dropped during the resolution (the silent-data-loss failure mode).
- For a rebased PR branch, confirm the final range is what you expect before
  `--force-with-lease` (recipe in the playbook).

## See also

- [`autonomous-pr-driver`](../autonomous-pr-driver/SKILL.md) — drives a PR to
  merge-ready; delegates here when a PR is behind base / `mergeable=CONFLICTING`.
- [`git-trunk-branch-and-pr-automation`](../git-trunk-branch-and-pr-automation/SKILL.md)
  — owns the branch/rebase/squash-merge mechanics this works within.
- [`reference/playbook.md`](./reference/playbook.md) — the `git`/`gh` command recipes.

## Sources

- Git docs: `git-merge` / `git-rebase` (ours vs theirs, `--abort`), `git-rerere`,
  `merge.conflictStyle` (`diff3`/`zdiff3`), `git diff --check`.
  <https://git-scm.com/docs/git-merge>, <https://git-scm.com/docs/git-rerere>
- GitHub PR mergeability fields (`mergeable`, `mergeStateStatus` = `DIRTY` on
  conflict): <https://docs.github.com/en/graphql/reference/enums#mergestatestatus>
