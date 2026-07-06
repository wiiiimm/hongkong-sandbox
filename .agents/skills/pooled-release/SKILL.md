---
name: pooled-release
description: "Cut fewer, batched releases (a 'release train') instead of one per merge — by triggering semantic-release on demand or on a cadence rather than on every push to main. Use when releasing on every merge is too noisy, when you want one larger readable changelog per release, to add a manual 'cut a release' button (workflow_dispatch) or a scheduled/weekly release, to set up prerelease channels (next/beta → promote to stable), or when deciding whether you need a release branch."
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "1.2.1"
---

# Pooled releases (release trains)

Release on every merge is great for a fast-moving lib, but sometimes you want
**fewer, fatter releases** — one readable changelog per cut, not a version bump per
PR. For the manual and scheduled models it does that **without changing how you
develop** — it only changes the release **trigger** (the prerelease-channel model in
Model 3 does shift where you target work; see there). It builds directly on
[`semantic-release-automation`](../semantic-release-automation/SKILL.md) — same
plugin pipeline, same Conventional Commits; read that first.

## The key idea: decouple *merge* from *release*

Trunk-based development still wants frequent small merges to `main` — that's
unchanged, so **dev velocity and PR flow don't change**. The only thing you move is
**when a release is published**:

| | Trigger | Result |
| --- | --- | --- |
| **Per-merge (default)** | `on: push: [main]` | a release every qualifying merge — many small ones |
| **Pooled (this skill)** | `workflow_dispatch` and/or `schedule` | semantic-release batches **all** commits since the last tag into **one** release |

semantic-release already does the batching — it always releases "everything since the
last tag." Pooling just means you tag **less often**.

A pooled run produces the **same outputs** as a per-merge one (just batched), and
those outputs are independent — CHANGELOG, GitHub Release, and npm publish are each
opt-in. A pooled **app** usually wants CHANGELOG + GitHub Release but not npm; see
[`semantic-release-automation` → Outputs are à la carte](../semantic-release-automation/SKILL.md#outputs-are-à-la-carte--pick-any-subset).
The GitHub Release is also what a deploy gate keys on (below).

> **For a visual, human-readable walkthrough** — trigger diagrams, a merges-to-releases
> timeline, and the "why each config delta" table — see
> [`reference/pooled-vs-unpooled.md`](./reference/pooled-vs-unpooled.md).

## Pick a model

Use [`templates/release-on-demand.yml`](./templates/release-on-demand.yml) for the
first two; it ships with `workflow_dispatch` on and `schedule` commented.

1. **Manual button — `workflow_dispatch`** *(recommended default).* Cut a release
   when you decide it's worth one (Actions tab → Run workflow). Simplest; no surprise
   releases; no release branch.
2. **Cadence — `schedule`.** Uncomment the `cron` for an automatic train (e.g. weekly).
   Good when you want predictable, regular cuts. (Combine with the button if you like.)
3. **Prerelease channels — `next` (and/or `beta`).** A *related* pattern, not strictly
   pooling: push work to a `next` branch for **continuous** `x.y.z-next.N` prereleases,
   then cut a batched **stable** release by promoting `next` → `main` **when you
   choose** (that promotion is the "pooling"). Notes:
   - This model is **push-triggered on the prerelease branch**, so it pairs with the
     parent skill's push-triggered `release.yml` (`on: push: [main, next]`) — **not**
     the on-demand workflow above (which would defeat the "continuous" part). The
     `branches: [main, next]` setting itself lives in the **semantic-release config**,
     not the workflow — see
     [`templates/releaserc.prerelease-channels.json`](./templates/releaserc.prerelease-channels.json).
   - Channels are **independent** — a `next` and a `beta` channel don't flow into each
     other (no auto-promotion between them), so **pick one** unless you genuinely need
     two parallel pre-release lines. The template ships just `next`; add a
     `{ "name": "beta", "prerelease": true }` entry only if you do.
   - Promote with a normal **merge or fast-forward** of `next` into `main` — semantic-
     release cuts the stable release once the commits are reachable from `main`, either way.
   - **Known quirk:** the template runs `@semantic-release/changelog` + `git` on the
     `next` branch too, so each `x.y.z-next.N` prerelease commits its own CHANGELOG
     entries; the stable cut then regenerates notes for the same commits. If the
     duplicated prerelease sections bother you, scope the `changelog`/`git` plugins to
     stable only (e.g. via a per-branch config) or accept the noise on `next`.

## Release branches — usually don't

A long-lived `release/x.y` branch is real trunk-based practice but only pays off when
you must **stabilise/QA a release while trunk keeps moving**, or **support multiple
live versions** at once. It costs you hotfix cherry-picking and snapshot maintenance.
For a single-version app/CLI, **skip it** — pooling via trigger (above) gives you the
batched releases without the branch overhead.

## What changes vs the per-merge setup

Start from `semantic-release-automation`'s `release.yml` and:

- **Replace the trigger** — drop `on: push: [main]`; add `workflow_dispatch` (and/or
  `schedule`).
- **Drop the no-loop guard** — with no `on: push`, the `chore(release): …` commit
  semantic-release pushes can't re-trigger the workflow, so the
  `if: !startsWith(... 'chore(release):')` guard is unnecessary.
- **Everything else is identical** — plugin pipeline, `fetch-depth: 0`,
  `$GITHUB_SERVER_URL` repo URL, tokens, npm publish.

## Gotchas

- **`schedule` only runs once the workflow file is on the default branch** — merge it
  to `main` before expecting cron to fire; `cron` is UTC.
- **The branch guard must special-case `schedule`.** On scheduled runs
  `github.event.repository` is empty, so a bare
  `if: github.ref_name == github.event.repository.default_branch` evaluates to
  `main == ''` → false and **silently skips every cron run**. The template's guard
  short-circuits with `github.event_name == 'schedule' ||` (safe — `schedule` only
  fires on the default branch); keep that clause if you adapt the guard.
- **`fetch-depth: 0` still required** (full history + tags for the batched analysis).
- **`concurrency: { group: release }`** so a manual run and a scheduled run can't
  collide on the tag push.
- **`workflow_dispatch` lets the runner pick any branch** — the Actions UI branch
  dropdown (or `gh workflow run --ref <branch>`) means a manual run could analyze a
  feature/prerelease branch instead of `main`. The template guards this with a
  job-level `if: github.event_name == 'schedule' || github.ref_name == github.event.repository.default_branch`;
  keep it. (`semantic-release-automation`'s push-triggered `release.yml` carries the
  same guard on its `workflow_dispatch` path, so the two templates stay consistent —
  a manual dispatch on either can only cut a release from the default branch.)
- **Big gaps → big changelogs.** That's the point, but communicate the cadence so
  contributors know when their merged work actually ships.
- **Pooling does NOT gate production deploys — wire that separately.** If a platform
  (Vercel/Netlify) auto-deploys `main` on every push, it keeps shipping prod on every
  *merge*, defeating the point of batching. Gate it with
  [`production-release-gating`](../production-release-gating/SKILL.md) so prod ships on
  the **train**, not on merges. The most portable gate is its **Promotion Branch**
  model: `main` → staging on every merge, promote `production` to the released commit
  to ship prod — no platform-specific script.
- **Don't add `on: push` to the on-demand workflow without re-adding the loop guard.**
  With only `workflow_dispatch`/`schedule`, the `chore(release): …` commit can't
  re-trigger it (no guard needed). If you later add `on: push` (e.g. for hotfixes),
  re-add `if: !startsWith(github.event.head_commit.message, 'chore(release):')` or it
  will loop.

## Verify

- `npx semantic-release --dry-run` on `main` prints the **batched** next version and
  the full accumulated release notes — without publishing.
- Manual: Actions tab → the workflow → **Run workflow**. Scheduled: confirm the cron
  in the default-branch copy of the file.

## See also

- [`reference/pooled-vs-unpooled.md`](./reference/pooled-vs-unpooled.md) — visual
  walkthrough (diagrams, timeline, config-delta table) for humans skimming the design.
- [`semantic-release-automation`](../semantic-release-automation/SKILL.md) — the
  pipeline this reuses; pooling only swaps the trigger.
- [`conventional-commits`](../conventional-commits/SKILL.md) — what the batched
  changelog is built from.
- [`production-release-gating`](../production-release-gating/SKILL.md) — deploy on the
  pooled release rather than on every merge.

## Sources

- semantic-release branches/channels config (prerelease `next`/`beta`):
  <https://semantic-release.gitbook.io/semantic-release/usage/configuration#branches>
- Trunk-based development & release strategies: <https://trunkbaseddevelopment.com/>,
  Atlassian's TBD guide, and the semantic-release TBD discussion (#2041). The
  decouple-merge-from-release framing and "release branches only when you must
  stabilise/QA or support multiple live versions" come from those.
