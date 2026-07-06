---
name: semantic-release-automation
description: "Automate versioning, changelog, tags, GitHub Releases, and npm publishing from Conventional Commits with semantic-release. Use when setting up or debugging automated releases, wiring a `.releaserc` / `release` config and the plugin pipeline (commit-analyzer, release-notes-generator, changelog, npm, git, github), making `main` cut a version on merge, generating CHANGELOG.md, publishing to npm or creating a GitHub Release per release, doing per-package releases in a monorepo (per-package tags + paths-filter matrix), pooling commits into a less-frequent release, or fixing a release that didn't fire / a CI loop from the release commit. Covers the single-package and monorepo flavors and the GitHub Actions workflow."
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "1.3.1"
---

# semantic-release automation

[semantic-release](https://github.com/semantic-release/semantic-release) reads
[Conventional Commits](../conventional-commits/SKILL.md), computes the next semver
version, writes the changelog, tags, and **registers a GitHub Release** (and
optionally publishes to npm) — all in CI, no manual version bumps. This skill is
the tooling that consumes the commit format; read `conventional-commits` first for
how the bump is decided.

Copy-paste configs: [`templates/`](./templates) — a single-package config, a
monorepo per-package config, and the GitHub Actions workflow.

## How a release happens

1. You merge a PR to `main` (squash; the **PR title** is the Conventional Commit).
2. The workflow runs `semantic-release`, which:
   - **commit-analyzer** → reads commits since the last tag, decides major/minor/patch (or no release).
   - **release-notes-generator** → builds the notes from those commits.
   - **changelog** → writes/updates `CHANGELOG.md`.
   - **npm** *(optional)* → bumps `package.json` and publishes to npm.
   - **git** → commits `CHANGELOG.md`/`package.json` back as `chore(release): X.Y.Z` (the version **tag** itself is created by semantic-release core, not this plugin).
   - **github** → creates the **GitHub Release** (the canonical record of what shipped).

If no commit since the last release warrants a bump (only `chore`/`docs`/…), it
does nothing — correct, not a failure.

### Outputs are à la carte — pick any subset

Those six steps read like one bundle, but the **outputs are independent**: keep only
the plugins for what you actually want. `commit-analyzer` + `release-notes-generator`
are the **baseline** (they compute the version and notes) — keep them; everything below
is opt-in.

| Output | Plugin(s) | Needs |
| --- | --- | --- |
| **git tag** | *(semantic-release **core** — no plugin)* | — (created on every release) |
| **GitHub Release** | `@semantic-release/github` | workflow grants write `permissions` — the template sets `contents` + `issues` + `pull-requests` (the plugin's default success **and failure** issue/PR comments need the latter two; see the plugin docs before trimming them); default `GITHUB_TOKEN` then suffices — a PAT/bot token only if the Release must trigger a downstream `on: release` workflow |
| **`CHANGELOG.md` committed to the repo** | `@semantic-release/changelog` + `@semantic-release/git` | release bot can commit to `main` (bypass branch protection) |
| **`package.json` version bump** (no publish) | `@semantic-release/npm` (`"npmPublish": false`) **+ `@semantic-release/git`** to commit it back | without `@semantic-release/git` the bump is made in CI then **discarded** — `package.json` in the repo stays unchanged |
| **npm publish** | `@semantic-release/npm` | `NPM_TOKEN`; libraries only |

The **git tag always happens** (core); each other output appears only if its plugin is
present — drop `@semantic-release/npm` and `package.json` is never bumped; drop
`@semantic-release/git` and there's no in-repo `CHANGELOG.md`/version commit (tag-only).

- A **deployed app** typically wants **`CHANGELOG.md` + GitHub Release** but **not** npm
  publish — drop `@semantic-release/npm` (or `"npmPublish": false` to still bump
  `package.json`). A **library** adds npm publish on top.
- If your deploy gate fires on the **published GitHub Release** — both the
  **release-event-driven deploy** and the **Promotion Branch** gate do (`on: release`
  with `types: [published]`, see [`production-release-gating`](../production-release-gating/SKILL.md)) —
  then `@semantic-release/github` is **required**: no Release, no deploy. (Only Vercel's
  build-skip `ignoreCommand` gate needs no Release — but it matches on the
  `chore(release): X.Y.Z` **commit**, so it requires `@semantic-release/git` instead; a
  tag-only config leaves it nothing to detect.)

## Where config lives

Either a **`.releaserc.json`** at the repo/package root, or a **`"release"`** key
in `package.json`. Both are equivalent; pick one. Plugin **order matters** — it's
the execution pipeline, and `npm` must run before `git` so the bumped
`package.json` is what gets committed.

## Flavor 1 — single package (npm or app)

Use [`templates/releaserc.single-package.json`](./templates/releaserc.single-package.json).
- Publishing to **npm**: keep `@semantic-release/npm`.
- **Not** publishing (a deployed app, or a private package): **drop**
  `@semantic-release/npm` (or set `["@semantic-release/npm", { "npmPublish": false }]`
  to still bump `package.json` without publishing).

## Flavor 2 — monorepo, per-package releases

Each package gets its **own** `.releaserc.json` with a package-scoped
**`tagFormat`** (`my-app-v${version}`) so versions/tags don't collide — see
[`templates/releaserc.monorepo-package.json`](./templates/releaserc.monorepo-package.json).
The workflow detects **which packages changed** with `dorny/paths-filter` and runs
`semantic-release` once per changed package (a matrix), `max-parallel: 1` with a
`git pull --rebase` retry so concurrent tag pushes don't collide.

- **Replace `my-app`** in both `tagFormat` and the git commit `message` with the
  real package name — otherwise every package shares one tag and the deploy gate
  can't match the scope. The template's `exec` step bumps `package.json` **inline**
  (no external script to create); swap in a script only if you need extra prepare
  steps. (It reserialises `package.json` with 2-space indent — if your repo uses
  other formatting, use a script or a targeted replace to avoid a noisy diff.)
- **The shipped [`templates/release.yml`](./templates/release.yml) is
  single-package.** For a monorepo, wrap that same `semantic-release` call in a
  `dorny/paths-filter` → matrix job (`max-parallel: 1` + a `git pull --rebase` retry
  so concurrent tag pushes don't collide):

  ```yaml
  jobs:
    detect: # which packages changed?
      runs-on: ubuntu-latest
      outputs:
        changed: ${{ steps.f.outputs.changes }}
      steps:
        - uses: actions/checkout@v7
        - id: f
          uses: dorny/paths-filter@v4
          with:
            filters: | # name each key after the package's directory
              apps/web: ['apps/web/**']
              packages/lib: ['packages/lib/**']
    release:
      needs: detect
      if: ${{ needs.detect.outputs.changed != '[]' }}
      strategy:
        max-parallel: 1
        fail-fast: false
        matrix:
          pkg: ${{ fromJson(needs.detect.outputs.changed) }}
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v7
          with: { fetch-depth: 0 } # add persist-credentials: false to use GH_TOKEN below (private repos then need it wired into the git pull, e.g. a URL with the token)
        - uses: actions/setup-node@v6
          with: { node-version: lts/*, cache: npm }
        - run: npm ci
        - working-directory: ${{ matrix.pkg }} # filter key == package dir
          env: { GITHUB_TOKEN: '${{ secrets.GH_TOKEN || github.token }}' }
          # An earlier matrix job may have pushed its release commit; rebase + retry
          # so this job isn't behind main when it pushes its own tag.
          # --repository-url (as in the single-package template) guards against an
          # org/repo rename desyncing package.json's repository field (EMISMATCHGITHUBURL).
          run: |
            R="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}.git"
            # checkout defaults to detached HEAD on push — land on the branch so the
            # rebase-retry has a branch to rebase onto (and to push the tag from).
            git checkout "$GITHUB_REF_NAME"
            git pull --rebase origin "$GITHUB_REF_NAME" || true
            npx semantic-release --repository-url "$R" || { git pull --rebase origin "$GITHUB_REF_NAME"; npx semantic-release --repository-url "$R"; }
  ```

  `dorny/paths-filter` emits `changes` as a JSON array of the matched filter keys;
  naming each key after the package dir lets `working-directory: ${{ matrix.pkg }}`
  resolve. Each package uses its own `.releaserc` (above).
- **Which package releases** comes from changed **file paths** (paths-filter), and
  the bump from the commit/PR-title **type**. Keep a PR to **one package** so the
  squash commit maps cleanly. For strict per-package *commit attribution*, add
  [`semantic-release-monorepo`](https://github.com/pmowrer/semantic-release-monorepo)
  (it filters commits to those touching the package); plain semantic-release reads
  repo-wide history.
- The monorepo template's git message carries `[skip ci]` and uses a `[skip ci]`-
  aware deploy gate — see [`production-release-gating`](../production-release-gating/SKILL.md).

## The GitHub Actions workflow

Use [`templates/release.yml`](./templates/release.yml). Non-negotiables:

- **`fetch-depth: 0`** — semantic-release needs full history + tags.
- **Don't loop:** the `chore(release): …` commit it pushes would re-trigger the
  workflow. Guard with `if: ${{ !startsWith(github.event.head_commit.message, 'chore(release):') }}`
  (this template — the `${{ }}` wrapper is **required**; a bare leading `!` is invalid
  YAML) **or** put `[skip ci]` in the release commit message (the
  monorepo template) if your CI honours it. The template's guard also restricts the
  `workflow_dispatch` (manual / pooled) path to the **default branch**, so a manual
  run can't accidentally cut a release from a feature branch.
- **Token:** the built-in `GITHUB_TOKEN` works for tags/Releases, but commits it
  makes **won't trigger other workflows**. If a release must kick off a downstream
  deploy via `on: push`/`on: release`, use a **PAT/bot `GH_TOKEN`**. (See
  `production-release-gating` for the `on: release` (`types: [published]`) pattern, which sidesteps this.)

## Pool commits into fewer releases

Don't want a release on every merge? Keep merging to `main` continuously (trunk),
but **change the trigger**: drop `on: push` and run the release on
`workflow_dispatch` (a manual "cut a release" button) and/or a `schedule:`.
semantic-release batches every commit since the last tag into one larger release —
no release branch needed. For continuous prereleases, add a `next`/`beta` branch to
`branches` (channel releases) and fast-forward to `main` for the stable cut.

This is the short version. For the **full treatment** — the manual / scheduled /
prerelease-channel models, when a release branch is (rarely) worth it, the gotchas,
and copy-paste workflow + channel-config templates — use the dedicated
[`pooled-release`](../pooled-release/SKILL.md) skill (it reuses this exact pipeline;
only the trigger changes).

## Gotchas

- **Plugin order is the pipeline.** `commit-analyzer` → `notes` → `changelog` →
  `npm` → `git` → `github`. `changelog`, `npm`, and (in the monorepo flavor) the
  `exec` bump must all come **before** `git` — `git` commits the files they
  produce/bump, so a wrong order commits a stale `CHANGELOG.md`/`package.json`.
- **`EMISMATCHGITHUBURL` after an org/repo rename** — `package.json`'s `repository`
  field desyncs from the live URL. Pass
  `--repository-url "${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}.git"` (the template
  does — `GITHUB_SERVER_URL` rather than a hard-coded `github.com` keeps it working
  on GitHub Enterprise Server).
- **Nothing published?** Check: was the merged commit/PR-title a *releasable* type
  (`feat`/`fix`/breaking, not `chore`)? Is `fetch-depth: 0` set? Is the branch in
  `branches`? A non-conventional title silently yields no release.
- **`NPM_TOKEN`** needs publish rights (and 2FA set to "automation"/auth-token, not
  OTP) for `@semantic-release/npm`.
- **Don't hand-write `chore(release):` commits** — they're the bot's output.
- **The `git` plugin pushes the release commit straight to `main`.** That's by
  design — release automation is the one sanctioned committer to `main` (it bypasses
  the feature-branch + PR rule that applies to humans). If `main` has branch
  protection requiring PRs/reviews, give the release token (a bot/PAT) **bypass**
  permission, or drop `@semantic-release/git` and run **tag-only** (no
  changelog/version commit back — you lose the in-repo `CHANGELOG.md` bump).

## Verify

`npx semantic-release --dry-run` prints the next version and release notes
**without** publishing — the fastest way to confirm your config and that the
commits produce the bump you expect. Run it on a **branch listed in `branches`**
(e.g. `main`); on any other branch semantic-release logs "skipping" and prints no
version — pass `--branches "$(git branch --show-current)"` to force it on a feature
branch.

## See also

- [`conventional-commits`](../conventional-commits/SKILL.md) — the input format
  that decides the version bump.
- [`pooled-release`](../pooled-release/SKILL.md) — want fewer, batched releases
  instead of one per merge? The "release train" variant — same pipeline, the trigger
  changes (on-demand / scheduled / prerelease channels).
- [`production-release-gating`](../production-release-gating/SKILL.md) — deploy only
  on a real release (the GitHub Release / `chore(release):` commit this produces).
- [`git-trunk-branch-and-pr-automation`](../git-trunk-branch-and-pr-automation/SKILL.md)
  — squash + semantic PR title that becomes the commit analysed here.

## Sources

- semantic-release docs & plugin pipeline: <https://semantic-release.gitbook.io/semantic-release/>
- Default release rules (`angular` preset): <https://github.com/semantic-release/commit-analyzer/blob/master/lib/default-release-rules.js>
- Patterns generalised from production repos: a published npm CLI (single-package, npm
  publish, `config in package.json`, no-loop `if` guard, `--repository-url` fix) and
  a production monorepo (per-package `.releaserc` + `tagFormat`, `dorny/paths-filter`
  matrix, `@semantic-release/exec` prepare step, `[skip ci]` release commit).
