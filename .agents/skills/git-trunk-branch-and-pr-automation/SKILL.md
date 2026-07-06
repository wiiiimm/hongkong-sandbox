---
name: git-trunk-branch-and-pr-automation
description: "Trunk-based Git workflow with enforced branch naming and squash-merge PR titles. Use when setting up or standardising a branch/PR workflow, naming branches (feature/ fix/ hotfix/ and AI-agent prefixes claude/ cursor/ codex/ copilot/ codegen-bot/ dependabot/), configuring squash-only merges where the PR title becomes the commit and the body is the concatenated commits, making the PR title a valid Conventional Commit, adding GitHub Actions that validate branch names or auto-normalise PR titles, fixing a PR-title bot that loops, or deciding trunk vs release branches. Covers the GitHub repo settings, the validation/normalisation workflows, and how it feeds semantic-release."
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "1.2.0"
---

# Trunk-based branches + squash-PR automation

A trunk-based workflow where every change is a short-lived branch off `main`,
merged via **squash** with a **Conventional Commit PR title**. That title becomes
the single commit on `main` that [semantic-release](../semantic-release-automation/SKILL.md)
reads — so naming and title hygiene aren't cosmetic, they drive the release.

Templates: [`templates/`](./templates) — branch-name validation, the PR-title
normaliser workflow, and the shared `normalize-pr-title.js`.

## The model

- **Trunk-based:** branch off `main`, keep PRs small, merge frequently; `main`
  stays releasable. Don't use long-lived `develop`/release branches unless you must
  stabilise a release while trunk moves on, or support multiple live versions.
- **Branch naming:** `feature/<desc>`, `fix/<desc>`, `hotfix/<desc>` — plus
  **AI-agent prefixes** `claude/ cursor/ codex/ copilot/ codegen-bot/ dependabot/`
  for agent- and bot-authored branches. Validated by
  [`branch-name-check.yml`](./templates/branch-name-check.yml).

## Squash merge: the PR title *is* the commit

Configure the repo so a merge collapses to one clean, semantic commit:

- **GitHub → Settings → General → Pull Requests:** enable **Squash merging only**
  (turn off merge commits and rebase). Set **"Default commit message" →
  "Pull request title and commit details"** — GitHub then uses the **PR title as the
  squash subject** (it appends `(#<PR-number>)`, which doesn't affect Conventional
  Commit parsing) and **concatenates the PR's commit messages into the body**.
- So: the **title** must be a valid Conventional Commit (it's what semantic-release
  analyses → version + changelog); the **body** (the concatenated commits) preserves
  the detailed history.
- Keep a PR to **one logical change** (in a monorepo, one package) so the single
  squashed commit maps cleanly to one type+scope. See
  [`conventional-commits`](../conventional-commits/SKILL.md).

## PR-title automation

[`pr-title-manager.yml`](./templates/pr-title-manager.yml) +
[`normalize-pr-title.js`](./templates/normalize-pr-title.js) keep the title valid:

- On open/reopen/synchronize it normalises the title to Conventional Commits
  (lowercasing the type, or synthesising `<type>: <subject>` from the PR's commits
  / branch prefix when the title isn't conventional).
- A correct title is left untouched; the **`skip-title-automation` label** opts out of
  the auto-rewrite for the rare edge case (still validated — see
  [Opting out](#opting-out-of-the-auto-rewrite) below).
- It posts a **sticky comment** explaining the squash convention.
- Install the script at `.github/scripts/normalize-pr-title.js`; the workflow
  `sparse-checkout`s the `.github/scripts` directory to load it.

Pair it with `branch-name-check.yml`, and in **branch protection** require both
checks (plus your release/CI checks) before a PR can merge.

### Opting out of the auto-rewrite

There are two cases — and the **first covers almost everyone**:

1. **Just write a valid Conventional Commit title.** The normaliser only rewrites a
   title that *isn't* already conventional; a correct title (`feat: add x`,
   `fix(api): …`) is left **completely untouched**. There's nothing to "skip" — this
   is the intended path.
2. **Add the `skip-title-automation` label** (create it once in the repo) only for the
   rare case where the title isn't conventional *yet* and you don't want the bot
   auto-editing it / posting its comment while you sort it out (e.g. mid-review). The
   label suppresses the **auto-rewrite + sticky comment** — but **not validation**: the
   required check still **fails** until the title is a valid Conventional Commit (or a
   `type!:` breaking commit is reflected by a `!`). So the label changes *who* fixes
   the title (you, not the bot), never *whether* it must be valid before merge.

The opt-out is a **label, not a string in the title**, on purpose: the PR title becomes
the squash commit semantic-release reads, so any marker left in the title would land in
the release commit and silently produce **no release**. The label is also ignored on
the fork/bot validate path (it never edits there, so there's nothing to suppress).

## Gotchas

- **Three modes — and don't loop on your own edits.** The template classifies each
  PR: `skip` only for **`github-actions[bot]`** (its *own* title edits — the workflow
  listens for `edited` to re-validate human changes, and skipping its own identity
  stops the loop). With the **default `GITHUB_TOKEN` this is belt-and-braces** —
  GitHub deliberately doesn't retrigger workflows on events its own token caused, so
  the bot's edit wouldn't re-fire anyway; the skip only *matters* if you swap in a PAT
  or GitHub App token (whose edits **do** retrigger), so keep it. `validate` for
  **forks and other bots like dependabot**
  (read-only/untrusted → title is checked but never auto-edited); `normalize` for
  same-repo human PRs (run the script + fix the title). Don't blanket-skip all bots —
  a non-self bot with a non-conventional title would otherwise merge unchecked.
- **Agent/bot branch prefixes don't infer a type.** `claude/ cursor/ codex/ …`
  are valid branch names, but the normaliser derives the type from the PR's
  **commits** (which should be conventional), not the prefix — falling back to
  `chore` only if neither title nor commits are conventional. Keep agent commits
  conventional so the bump is right.
- **Fork / bot PRs are validate-only.** `pull_request` from a fork gets a
  **read-only** token *and* an attacker-controlled checkout, so the template never
  checks out or runs the (PR-modifiable) script for them — it validates the title
  inline via the API (read-only) and **fails** if it isn't a valid Conventional
  Commit (any type, including non-releasing `docs:`/`chore:`), or if a `type!:`-style
  breaking commit isn't reflected by a `!` in the title. Same-repo human branches
  (the norm for this trunk-based workflow) are the only ones auto-edited. Configure
  dependabot with a conventional `commit-message.prefix` so its titles pass.
- **Squash settings are per-repo and easy to miss** — if "Default commit message"
  is left as "Default" (the first commit's message) instead of **"Pull request
  title and commit details"**, your carefully-named PR title is ignored at merge.
- **The opt-out suppresses the rewrite, not the validation.** The
  `skip-title-automation` label stops the auto-edit + sticky comment but the title is
  **still checked** (the required check fails until it's a valid Conventional Commit) —
  full details in [Opting out](#opting-out-of-the-auto-rewrite) above. A green check
  always means a releasable title; the label can't bypass that.

## See also

- [`conventional-commits`](../conventional-commits/SKILL.md) — the format the title
  must follow.
- [`semantic-release-automation`](../semantic-release-automation/SKILL.md) — consumes
  the squashed commit to cut the release.
- [`production-release-gating`](../production-release-gating/SKILL.md) — deploys only
  the resulting release.
- [`resolve-merge-conflicts`](../resolve-merge-conflicts/SKILL.md) — resolving the
  conflicts/behind-base updates a branch hits before it can squash-merge.

## Sources

- Generalised from a production app's `branch-name-check.yml` (the
  `feature|fix|hotfix|codegen-bot|copilot|codex|cursor|claude|dependabot` prefix
  set) and `pr-title-manager.yml` + `normalize-pr-title.js` (title normalisation,
  the `skip-title-automation` label opt-out, bot-cascade guard, sticky comment).
- GitHub squash-merge commit-message options:
  <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests>
