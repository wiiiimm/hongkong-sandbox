---
name: code-complexity-stats-pr
description: Add a GitHub Actions workflow that posts code-size and cost statistics — lines of code, per-language breakdown, complexity, and a COCOMO "what would this cost to build" estimate — as a sticky comment on every pull request, using scc. Use when you want a per-PR code-stats or "worth of the codebase" comment, to show LOC / language breakdown or an estimated development cost/effort on PRs, to set up scc (Sloc Cloc and Code) in CI, to post or upsert a single self-updating bot comment from GitHub Actions, or to change the COCOMO salary/currency. Covers fork-PR token limits, runner architecture, version pinning, and comment pagination.
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "1.2.0"
---

# Code complexity / cost stats on every PR

A GitHub Actions workflow that runs [`scc`](https://github.com/boyter/scc)
(Sloc, Cloc and Code) over the repo on each pull request and posts the results —
including a **COCOMO** estimated cost/effort to build the codebase — as a **single
sticky comment** that updates in place on every push. Drop-in workflow:
[`templates/code-complexity.yml`](./templates/code-complexity.yml).

## What you get

`scc` prints a per-language table (files, lines, code, comments, blanks,
complexity) plus, with `--avg-wage`, a **COCOMO** block: estimated person-months,
schedule, people, and a **dollar cost to develop**. The workflow wraps that in a
fenced block and posts it as a PR comment titled *📊 Code Complexity Analysis*.

It reports the **whole codebase at the PR's head**, not the diff — it's a
"what's this project worth / how big it is" signal, not a per-PR delta.

## Install

Copy [`templates/code-complexity.yml`](./templates/code-complexity.yml) to
`.github/workflows/code-complexity.yml`. It works as-is on `ubuntu-latest`; the
only thing you'll likely change is the `AVG_WAGE` / `WAGE_LABEL` workflow env (see Customise).

## How it works (the parts that matter)

- **Trigger:** `pull_request: [opened, synchronize, reopened]` — runs on open and
  every push. Kept as its **own workflow** so it always runs even when other
  workflows honour a `[skip ci]`-style marker; these stats are informational.
- **Permissions:** a PR comment is posted via the *Issues* API, so
  `pull-requests: write` is what actually authorises the create/update;
  `issues: write` is included belt-and-suspenders. (Both are in the template.)
- **Sticky comment:** the body starts with a hidden marker
  `<!-- code-complexity -->`. The script lists existing comments, finds the one
  with that marker, and **updates it** (else creates one) — so a PR keeps exactly
  one stats comment that refreshes instead of stacking new ones each push.
- **Concurrency:** `cancel-in-progress: true` keyed on the **PR number**
  (`github.event.pull_request.number`) — a new push kills the in-flight run so you
  don't race two comment updates. Keyed on the number, not `head_ref`, so two
  forks sharing a branch name can't cancel each other.
- **COCOMO cost:** `scc --avg-wage <annual>` drives the cost figure. The number is
  unitless to scc — it's read in *your* currency. The template defines `AVG_WAGE`
  (`360000`, HKD 30,000/month) and `WAGE_LABEL` once as workflow `env`, so the
  number scc uses and the label in the comment can't drift — change the salary in
  one place.

## Customise

| Want to… | Change |
| --- | --- |
| Use a different currency / salary | the `AVG_WAGE` and `WAGE_LABEL` workflow `env` (one place — the comment label reads `WAGE_LABEL`) |
| Exclude more build/generated dirs | `--exclude-dir` list (comma-separated). scc honours `.gitignore` by default; this is for output that isn't ignored |
| Pin / upgrade scc | `SCC_VERSION` in the install step |
| Run on ARM runners | swap the tarball to `scc_Linux_arm64.tar.gz` and use an ARM runner (e.g. `ubuntu-24.04-arm`) |
| Count only part of a monorepo | add a path arg to `scc` (e.g. `scc apps/web`) |

## Gotchas

- **Fork PRs can't post the comment.** For PRs from forks, `pull_request` runs
  with a **read-only** token and no repo secrets, so the comment API call would
  403. Declaring `pull-requests: write` does **not** override this — GitHub
  enforces read-only on the token itself for fork-triggered runs. The template
  guards the **whole job** with
  `if: github.event.pull_request.head.repo.full_name == github.repository`, so on
  fork PRs the job **skips cleanly** (green check) instead of failing red — and no
  compute is wasted running scc for a comment that can't post. Options:
  (a) accept that stats only post for same-repo branches (fine for solo/team
  repos — the common case; this is the template default); or (b) split into two
  workflows — compute on `pull_request` (no secrets,
  untrusted code), upload `scc-output.txt` as an artifact, then comment from a
  separate `workflow_run` job that has write access. **Do not** just switch this
  workflow to `pull_request_target`: that runs with a write token in the *base*
  repo context, and checking out + running fork code there is a token-exfiltration
  footgun.
- **Long output is truncated, not failed.** GitHub caps a comment body at 65,536
  characters. Default scc output (a per-language table) is tiny, but `--by-file`
  on a big repo could blow past it, which *would* 422 the step — so the template
  trims to ~64k with a "truncated" note and the comment still posts.
- **Pin scc; don't track `latest`.** A `latest` download can change scc's output
  format and silently reshape every PR comment. The template pins `SCC_VERSION`
  **and** verifies the tarball against a pinned `SCC_SHA256` (`sha256sum -c`)
  before running it, so a swapped/compromised release asset fails the run instead
  of executing in CI. When you bump the version — or switch to the arm64 asset —
  update the checksum from that release's `checksums.txt`.
- **Match the tarball to the runner arch.** The release asset is arch-specific
  (`scc_Linux_x86_64.tar.gz` vs `_arm64`). The wrong one fails to run.
- **Paginate when finding the sticky comment.** A busy PR can have more comments
  than one API page; without pagination, the marker comment on a later page is
  missed, and you get duplicates. The template uses `github.paginate(...)` and
  matches the marker with `startsWith` (not `includes`) so a human comment that
  merely quotes the marker isn't mistaken for the bot's and overwritten.
- **Token: `GH_TOKEN || github.token`.** The template prefers a `GH_TOKEN` secret
  (a PAT/bot you already use) and falls back to **`github.token`** — the canonical
  reference to the built-in `GITHUB_TOKEN`. Prefer `github.token` over
  `secrets.GITHUB_TOKEN`; the built-in token is enough for same-repo comments
  given the permissions above.
- **COCOMO is illustrative.** It's the basic COCOMO model (COCOMO I, Organic mode)
  on LOC — a fun, *relative* signal of size/effort, not a real valuation. Don't
  quote it as the literal worth of the code.

## Provenance

Generalised from the working `code-complexity.yml` used in production repos
(a production app, a production monorepo): same scc + COCOMO + sticky-comment approach, hardened
here with version pinning + checksum verification, `persist-credentials: false`,
comment pagination, a portable `ubuntu-latest` runner, and the fork-PR security
note.
