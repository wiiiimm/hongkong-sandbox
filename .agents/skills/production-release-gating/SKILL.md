---
name: production-release-gating
description: "Stop every push/merge to main from shipping to production — deploy only on a real release. Use when a merge to main unexpectedly deploys to prod, when you want production to deploy only on a semantic-release version (not every commit), when setting up preview-on-feature-branch but gated-prod-on-main, wiring a Vercel Ignored Build Step / `ignoreCommand`, promoting to a staging/`production` branch, or triggering a deploy from a published GitHub Release (GKE, self-hosted, dispatchable targets). Covers three named patterns — Release-Triggered Deploy (`on: release`, `types: [published]`), Promotion Branch (staging/`production`, most portable), and Build-Skip Gate (the Vercel `ignoreCommand` script) — when to use which, works with both per-merge and pooled releases, branch-aware previews, and monorepo dependency-release handling."
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "1.4.0"
---

# Gating production deploys to real releases

By default, a push/merge to `main` deploys to production. With
[semantic-release](../semantic-release-automation/SKILL.md) you usually want the
opposite: **previews on feature branches, but production only on an actual
release** (a versioned `chore(release):` commit / a published GitHub Release).

There are three ways to enforce that. They have **names, not letters**, so you can
pick one by name and record it (see "pick the flow" below):

| | **Release-Triggered Deploy** | **Promotion Branch** | **Build-Skip Gate** |
| --- | --- | --- | --- |
| One-liner | CI runs the deploy when a Release publishes | a release fast-forwards a `production` branch the platform watches | a script cancels non-release builds on the platform |
| Who deploys | a workflow **you** control (GKE, self-hosted, dispatchable, or a platform CLI) | the platform's **native git integration**, but only off `production` | the **platform** auto-builds every push; the script vetoes |
| The gate | a **published Release** triggers the deploy; plain pushes deploy nothing | `production` only **advances on a published Release**; `main` = staging | the script **skips** the build unless it's a release commit |
| Portability | any dispatchable target (must disable native push-deploy — see below) | **any host with a configurable production branch** (Vercel, Netlify, CF Pages) — most portable | **Vercel/Netlify only** (platform-specific script) |
| Template | [`release-production.yml`](./templates/release-production.yml) | [`promote-to-production.yml`](./templates/promote-to-production.yml) | [`vercel-ignore.sh`](./templates/vercel-ignore.sh) |

**Decision rule:**
- Want to keep the platform's **native git deploys** with **zero platform-specific
  scripting**? → **Promotion Branch** (set the production branch, promote on release).
  Most portable; the recommended default for Vercel/Netlify/CF Pages.
- **You** own the deploy (GKE/self-hosted/any dispatchable target, or you *want* CI to
  drive a platform CLI)? → **Release-Triggered Deploy**.
- Locked into a platform's push-deploy and **can't** add a branch/promotion? →
  **Build-Skip Gate** (the ignore script) as the fallback.

## Works with both per-merge and pooled releases — pick the flow, then record it

All three gates are **orthogonal to release cadence**: they key on the
`chore(release):` commit + tag + published GitHub Release, which is produced
identically whether you release on **every merge**
([`semantic-release-automation`](../semantic-release-automation/SKILL.md)) or in
**batches** ([`pooled-release`](../pooled-release/SKILL.md)). So the same gate works
under either workflow — you don't re-pick it if you later switch cadence.

Because the gate is a **lasting repo convention** (and double-gating is a real
footgun — see Gotchas), when wiring this up for a project:

1. **Confirm the flow with the user — don't assume.** Which pattern (Release-Triggered
   Deploy / Promotion Branch / Build-Skip Gate)? Which branch is production? Which
   platform? Per-merge or pooled release trigger?
2. **Record the decision so it's durable and visible.** Write a short line in the
   repo's `AGENTS.md` (and/or the deploy workflow header), e.g.
   *"Prod gating: Promotion Branch — production branch `production`, platform Vercel,
   pooled release."* Future agents and humans then follow the same flow instead of
   re-deriving — or silently contradicting — it.

## Release-Triggered Deploy — deploy on a published Release

semantic-release creates a GitHub Release; this workflow fires on `on: release`
with `types: [published]` and rolls out `github.event.release.tag_name`, then
writes the deploy status back onto the Release body. Plain pushes to `main` deploy
nothing.

- **The deploy step is whatever command you control** — that's the point of "you
  deploy." The template shows a GKE/`kubectl` rollout, but the same job can call a
  **platform CLI** (`vercel deploy --prod --prebuilt`, `netlify deploy --prod`), hit
  a **deploy hook** (`curl "$DEPLOY_HOOK_URL"`), `wrangler deploy`, `flyctl deploy`,
  etc. The gate (fire only on the published Release) is identical; only the rollout
  command differs.
- **vs the platform's own git deploy:** use this when you want CI to *own* the prod
  deploy. If you'd rather keep the platform's **native** git integration and just gate
  which branch it watches, use **Promotion Branch** instead.
- **⚠️ If the platform has native git auto-deploy (Vercel/Netlify), DISABLE its
  default-branch prod deploy — or you double-ship.** This CI deploy is in *addition*
  to the platform's automatic push deploy, so without this the platform still ships
  prod on every merge to `main`. Two ways:
  - **Vercel** — `vercel.json`:
    `{ "git": { "deploymentEnabled": { "main": false } } }` stops Vercel deploying
    `main` (other branches still get previews; CI's `--prebuilt --prod` is unaffected).
    Or Project → Settings → Git → turn off the production branch's auto-deploy.
  - **Netlify** — `netlify.toml` `[context.production] command = "exit 0"` (or "Stop
    auto publishing" / lock the production deploy) so pushes to the prod branch don't
    auto-build; CLI deploys still publish.
  - **Or reuse the Build-Skip Gate inverted:** point [`vercel-ignore.sh`](./templates/vercel-ignore.sh)
    at this app but make `main` **always skip** (CI owns prod) while feature branches
    still build previews — the same script, the opposite verdict on `main`.
- **Token caveat:** a Release created with the built-in `GITHUB_TOKEN` will **not**
  trigger `on: release`. Have semantic-release run with a **PAT/bot `GH_TOKEN`** so
  its Release fires this workflow. (See `semantic-release-automation` → token notes.)
- **Pre-releases don't deploy:** the deploy job is guarded with
  `if: ${{ !github.event.release.prerelease }}`, so semantic-release `next`/`beta`
  channel releases (published with `prerelease: true`) are skipped — only a **stable**
  Release ships to prod.
- **Tag shape is validated:** the deploy step refuses a `tag_name` that isn't SemVer
  (`v?MAJOR.MINOR.PATCH`), so a stray/mis-shaped tag can't roll out. Adjust the regex
  to your scheme.
- **Ancestry is enforced (parity with Promotion Branch):** before deploying, the step
  fetches the default branch and runs `git merge-base --is-ancestor "$SHA"
  origin/<default>`, refusing a tag whose commit isn't on the default branch — so a tag
  published on off-main/unrelated code (anyone with `contents: write` can push
  `v9.9.9`) can't roll that code out to prod. The branch is auto-resolved from
  `github.event.repository.default_branch`; override `DEFAULT_BRANCH` only if you cut
  releases from a branch other than the repo default.
- `concurrency` uses **two global groups, not per-tag**: stable releases share
  `prod-release` and prereleases get a **separate** `prod-release-prerelease` group,
  both with `cancel-in-progress: false`, so deploys never run concurrently and an
  in-progress rollout is never half-killed. The split matters because concurrency is
  joined **before** the job-level `prerelease` `if` — a shared group would let a
  skipped prerelease run evict a queued **stable** deploy from the single pending slot.
  **Caveat:** GitHub keeps only one *pending* run per group, so even among stable
  releases a newer one can evict an older **queued** one — if every tag must deploy,
  add an external queue/lock rather than relying on concurrency alone.

## Promotion Branch — staging `main`, fast-forward `production`

The most **portable** gate: keep the platform's native git deploys, but point its
**Production Branch at a dedicated `production` branch** instead of `main`. Now `main`
is a preview/staging branch (deploys on every merge, but not to prod), and prod ships
only when `production` advances. [`templates/promote-to-production.yml`](./templates/promote-to-production.yml)
fires on the published Release and **fast-forwards `production` to the released
commit**; the platform's webhook then deploys it. No platform CLI, no ignore script —
just a branch update, so it works on Vercel, Netlify, Cloudflare Pages, anything with
a configurable production branch.

- **Setup is one-time:** create `production` off `main`, set it as the platform's
  Production Branch, and run semantic-release with a **PAT/bot `GH_TOKEN`** (same
  token caveat as Release-Triggered Deploy — the built-in token's Release won't fire
  `on: release`).
- **`production` only ever fast-forwards** from `main`, so it stays an ancestor of the
  release commit and the promotion push is always a clean fast-forward. A rejected
  (non-fast-forward) push is a real divergence to inspect — **never `--force` past it.**
- **Ancestry is enforced, not assumed:** before pushing, the workflow fetches the
  default branch and runs `git merge-base --is-ancestor "$SHA" origin/<default>`,
  refusing to promote a tag whose commit isn't on the default branch. This stops an
  off-main or unrelated tag from shipping arbitrary code to prod. It fetches into the
  **same ref it validates** (`origin <branch>:refs/remotes/origin/<branch>`). The branch
  is auto-resolved from `github.event.repository.default_branch`, so a non-`main`
  default needs no edit — override `DEFAULT_BRANCH` only if you cut releases from a
  branch *other* than the repo default.
- **Pairs naturally with [`pooled-release`](../pooled-release/SKILL.md):**
  semantic-release runs on `main` (button/cron) and tags; this promotes the tag to
  prod. Merges to `main` keep shipping staging; prod ships on the train.

## Build-Skip Gate — Vercel Ignored Build Step

Vercel runs an **Ignored Build Step** before building; its exit code decides:
**`exit 1` = build, `exit 0` = skip** (note the inversion). Wire
[`templates/vercel-ignore.sh`](./templates/vercel-ignore.sh) via `vercel.json`
(`"ignoreCommand": "bash ../../scripts/vercel-ignore.sh"`) or Project Settings →
Git → Ignored Build Step. Logic:

- **Feature branch →** build (preview deployment). This is the whole point of
  previews; don't gate them.
- **`main`, release commit** (`chore(release): …` / `chore(scope): release …`) **or
  `[deploy]` marker →** build (production).
- **`main`, anything else →** skip.
- **`[skip-deploy]`** on any branch → skip.

The release regexes **require a stable SemVer version anchored on the right**
(`X.Y.Z` at end-of-string or before whitespace), so a **prerelease** commit like
`chore(release): 1.2.3-next.1` (semantic-release `next`/`beta` channels cut from
`main`) does **not** match and does **not** ship to prod — matching the
`prerelease`-guarded Release-Triggered/Promotion gates. The script also **fails
closed**: if `git` can't read the message, an empty message falls through to the
`main` skip rather than erroring (a non-zero exit reads as *build* on Vercel).

**Monorepo:** Vercel's "Skipping Unaffected Projects" is layer 1 (Turborepo graph);
this script is layer 2. A per-app script also builds when a **dependency package**
releases — add a clause like
`^chore\((shared-lib|design-system)\):\ release\ v?[0-9]+\.[0-9]+\.[0-9]+` (shown
commented in the template, with the same anchored-version requirement so non-release
`chore(shared-lib): …` commits don't build) so an app redeploys when its shared lib
version bumps.

## Gotchas

- **Exit codes are inverted** in the Build-Skip Gate / Vercel ignore step (0 = skip).
  The single most common mistake.
- **Preview vs prod:** keep feature-branch previews ungated; only `main` is strict.
  Gating previews defeats the workflow.
- **Release-Triggered Deploy needs a non-default token** on the release side, or the
  Release won't trigger the deploy (silent no-op).
- **Release-Triggered Deploy on Vercel/Netlify double-deploys unless you disable native
  prod auto-deploy.** The platform ships `main` on every merge *and* CI ships on the
  Release. Turn off the platform's default-branch deploy (Vercel
  `git.deploymentEnabled.main: false`; Netlify stop auto-publishing) so only CI ships
  prod. (Not an issue on GKE/self-hosted — nothing auto-deploys there.)
- **Don't gate in two places at once.** Pick **one** pattern per app; doubling up
  (e.g. a `production` branch *and* an ignore script) makes "why didn't it deploy?"
  much harder to debug.
- **Promotion Branch: don't leave `main` as the platform's production branch.** The
  whole gate is moving the Production Branch to `production`; forget that step and
  every merge to `main` still ships to prod.
- **`[skip ci]` in the release commit** (the monorepo semantic-release flavor) means
  push-triggered workflows won't see it — which is exactly why Release-Triggered Deploy
  keys on the *Release event*, not the push.
- **Pre-releases must not reach prod.** Both the deploy and promote jobs gate on
  `if: ${{ !github.event.release.prerelease }}`; without it, a `next`/`beta` Release
  would ship to production. Keep the guard if you adapt these. The **Build-Skip Gate**
  has no release event to read `prerelease` from, so it enforces the same rule via its
  regex — the version is anchored on the right (`X.Y.Z` at end/whitespace) so a
  `chore(release): 1.2.3-next.1` prerelease commit doesn't match; don't loosen that
  anchor or prereleases start shipping prod.
- **Supply chain — pin actions to commit SHAs for a hardened posture.** These
  workflows run with `contents: write`, and `@v7`/`@v9` are **mutable tags** — even
  first-party `actions/*` tags can be re-pointed — so for strict supply-chain safety
  pin **every** `uses:` (including `actions/checkout`/`actions/github-script`, not just
  third-party like `pnpm/action-setup`) to a full commit SHA with a `# vX.Y.Z` comment,
  and let Dependabot bump them. The templates ship readable major tags as the
  convenient default; tighten to SHAs where the risk warrants.

## See also

- [`semantic-release-automation`](../semantic-release-automation/SKILL.md) — produces
  the release commit / GitHub Release this gate keys on.
- [`pooled-release`](../pooled-release/SKILL.md) — batched releases; the same gate
  ships prod on the train, not on merges.
- [`conventional-commits`](../conventional-commits/SKILL.md) — why the release commit
  looks like `chore(release): …`.

## Sources

- Generalised from production repos: a production app (Release-Triggered Deploy — `on: release` /
  `types: [published]` dispatches a GKE deploy and annotates the Release with status)
  and a production monorepo
  (Build-Skip Gate — per-app `vercel.json` `ignoreCommand` → `vercel-ignore-<app>.sh`
  with branch/release/dependency-aware exit codes).
- Vercel Ignored Build Step: <https://vercel.com/docs/projects/overview#ignored-build-step>
- Promotion Branch builds on each platform's configurable **production branch**
  primitive: Vercel (Project → Settings → Git → Production Branch) and Netlify (Site
  configuration → Build & deploy → Branches → Production branch). Promoting via a
  fast-forward of `production` is a generalisation of that native feature, so the gate
  stays platform-agnostic.
