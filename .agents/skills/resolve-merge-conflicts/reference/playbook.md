# Conflict-resolution playbook

The `git`/`gh` recipes for the loop in [`../SKILL.md`](../SKILL.md). Read this when
you need the exact commands; the decision rules live in the SKILL.

## 0. Turn on the aids (once, safe to keep global)

```bash
# Show the common ancestor in conflict hunks — the single biggest aid: you see what
# EACH side changed FROM, instead of guessing. zdiff3 (Git ≥ 2.35) also de-dupes
# common lines; fall back to diff3 on older Git.
git config --global merge.conflictStyle zdiff3   # or: diff3 on Git < 2.35 (check `git --version`)

# Reuse Recorded Resolution: remember how you resolved a hunk and auto-apply it if
# the SAME conflict recurs (e.g. replaying many commits in a rebase).
git config --global rerere.enabled true
```

## 1. Understand — what's conflicting and why

```bash
# Is a PR actually conflicting (vs just behind)? `mergeable` is the coarse signal
# (MERGEABLE / CONFLICTING / UNKNOWN); `mergeStateStatus` is finer: DIRTY = conflicts,
# BEHIND = just needs an update (no conflicts). Note: CLEAN is a mergeStateStatus value,
# NOT a mergeable value.
gh pr view <PR> --repo <owner/name> --json mergeable,mergeStateStatus,baseRefName,headRefName

# Bring the base in. Pick ONE of:
git fetch origin
git rebase origin/main      # linear history; you'll force-with-lease after
#   …or…
git merge  origin/main      # one resolution pass; normal push after

# Once stopped at a conflict:
git status                  # lists "both modified", "deleted by us/them", etc.
git diff                    # the conflict hunks (with diff3/zdiff3 context)
git diff --name-only --diff-filter=U   # just the unmerged paths
```

> **Rebase ours/theirs is inverted.** Mid-`rebase`, `--ours` = the branch you're
> replaying onto (e.g. `main`), `--theirs` = *your* commits being replayed. Mid-`merge`
> it's the intuitive way round (`ours` = your branch). The index **stage slots are
> fixed** (`:1` = common ancestor/base, `:2` = "ours", `:3` = "theirs") — but because
> the labels flip, **mid-rebase `:2` holds the upstream/main content and `:3` holds
> YOUR commit.** Inspect a side explicitly before acting on it:
> `git show :1:<file>` (base) · `git show :2:<file>` (ours — = main during a rebase) ·
> `git show :3:<file>` (theirs — = your commit during a rebase).

## 2. Resolve — hunk by hunk

- Open each unmerged file; for every `<<<<<<< / ======= / >>>>>>>` block, write the
  line(s) that preserve **both** intents (use the `|||||||` base block from diff3 to
  see what each side changed). Delete all three markers.
- Mark resolved: `git add <file>`.
- **Wholesale-one-side is allowed ONLY when correct**, not to silence markers:

  ```bash
  git checkout --theirs path/to/regenerated-file && git add path/to/regenerated-file
  ```

### Lockfiles — regenerate, don't hand-merge

```bash
# Take either side to clear the conflict, then rebuild the lock from the (already
# resolved) manifest so it's internally consistent. (Which side --theirs points at
# flips mid-rebase — see the ours/theirs inversion note above — but regeneration
# makes the choice irrelevant for the lock-only modes below.)
git checkout --theirs package-lock.json && npm install --package-lock-only   # npm (lock only)
git checkout --theirs pnpm-lock.yaml   && pnpm install --lockfile-only   # pnpm
git checkout --theirs yarn.lock        && yarn install            # yarn (classic)
git add <the-lockfile>
```

## 3. Verify — before continuing

```bash
git diff --check && git diff --cached --check   # leftover markers + whitespace (working AND staged)
# Belt-and-braces full-tree scan (incl. diff3's |||||||). Scan ALL tracked files —
# do NOT exclude *.md: a real conflict hides in READMEs/docs too.
! git grep -nE '^(<{7}|\|{7}|={7}|>{7})( |$)'
# build + tests here — the ONLY thing that catches a semantic conflict
# (textually clean, logically broken). e.g.: npm run build && npm test
```

## 4. Continue & push

```bash
# Merge:
git commit                           # default message records the resolution
git push

# Rebase:
git rebase --continue                # repeat resolve→add→continue per replayed commit
git range-diff origin/main @{u} HEAD   # sanity (base old new): only YOUR changes remain
                                     #   (@{u} needs an upstream set + a prior push)
git push --force-with-lease          # NEVER plain --force on a shared branch
                                     #   (a background/IDE auto-fetch can defeat the lease)
```

## Abort & recover (the escape hatch)

```bash
git merge  --abort        # back to clean pre-merge state
git rebase --abort        # back to clean pre-rebase state
git cherry-pick --abort
git rebase --skip         # DROPS the current commit entirely — only when it became a no-op (already upstream)

# Recover after a bad finish:
git reflog                # find the pre-op SHA
git reset --hard ORIG_HEAD          # undo the just-completed merge/rebase
git reset --hard <sha-from-reflog>  # or jump to any prior state
```

## Escalation (fork / untrusted PR)

A PR from a fork has an **attacker-controlled checkout** and a **read-only token** —
don't check it out and run its code. You usually can't push the fix to its branch
either (a 403), **unless `maintainerCanModify` is true**. Confirm and hand off:

```bash
gh pr view <PR> --repo <owner/name> --json isCrossRepository,headRepositoryOwner,maintainerCanModify
# isCrossRepository true (or a different headRepositoryOwner) → fork. If maintainerCanModify
# is false you can't push the fix either → ask the contributor to rebase, or resolve
# via the GitHub web conflict editor under a human's account.
```

When handing off any conflict, post the facts and leave a clean tree:

```bash
git merge --abort 2>/dev/null || git rebase --abort 2>/dev/null   # don't leave a half-state
gh pr comment <PR> --repo <owner/name> --body "$(cat <<'EOF'
Conflicts with base in: <files>. Tried <rebase/merge>; <which hunks> need an author
decision (both sides changed <X> deliberately). Stopping here — needs a human call.
EOF
)"
```
