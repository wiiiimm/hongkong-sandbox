---
name: conventional-commits
description: "The Conventional Commits format — also called \"semantic commits\" / semantic commit messages — a `type(scope): description` header (`feat`, `fix`, …) plus an optional `BREAKING CHANGE` footer, and how it makes history machine-readable to drive automated version bumps and changelogs. Use when writing a commit message or PR title, deciding the type/scope/bump for a change, setting up or fixing a repo's commit convention, making commits parseable by semantic-release / changelog tooling, validating PR titles, or when a release didn't bump or the changelog came out blank because a commit wasn't conventional. Covers the type→semver mapping, breaking changes, scopes, monorepo scopes, and squash-merge PR titles."
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "1.1.0"
---

# Conventional Commits (a.k.a. semantic commit messages)

A commit convention that makes history **machine-readable**: a parser reads each
message, decides the next semver version, and builds the changelog from it. "Semantic
commits" is the common nickname for the same thing. It's the foundation the release
automation stands on — [`semantic-release-automation`](../semantic-release-automation/SKILL.md)
covers the tooling that consumes these messages.

## The format

```text
<type>[(<scope>)][!]: <description>

<optional body — the "why", wrapped>

<optional footer(s) — BREAKING CHANGE:, Closes #123, Refs: ABC-12>
```

- `type` / `scope`: lowercase **by convention** — the spec is case-*insensitive*,
  except `BREAKING CHANGE`, which MUST be uppercase. `scope` is an optional noun in
  parens for the area touched.
- `!` before the colon **or** a `BREAKING CHANGE:` footer marks a breaking change
  (`BREAKING-CHANGE:` with a hyphen is an accepted synonym).
- **description**: concise; **by convention** imperative mood, lowercase, **no
  trailing period** (Angular/commitlint style — the spec itself mandates none of
  these).
- Blank line before any body/footer.

```text
feat(auth): add passkey sign-in
fix(parser): handle empty input without throwing
feat(api)!: drop the v1 token endpoint
docs: fix typo in install steps
```

## Types → meaning → version bump

These are the **semantic-release defaults** (the `angular` preset plus
commit-analyzer's built-in release rules). They're configurable via `releaseRules`,
but treat them as the contract.

| Type | Use for | Default release |
| --- | --- | --- |
| `feat` | a new feature | **minor** (`x.Y.0`) |
| `fix` | a bug fix | **patch** (`x.y.Z`) |
| `perf` | performance improvement | patch |
| `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore` | maintenance, no user-facing behaviour change | **no release** on their own |
| `revert` | revert a previous commit | **patch** (the change is being undone) |
| any type with `!` / `BREAKING CHANGE:` | incompatible change | **major** (`X.0.0`) |

The "no release" types still belong in history — the tooling just won't cut a
version for them alone. A release containing only `chore`/`docs` commits produces
**no new version**, which is usually correct.

## Breaking changes

Either form triggers a **major** bump and a highlighted changelog section:

```text
feat(api)!: require auth on all routes
```

…or via a footer (works on any type, and lets you explain the migration):

```text
refactor(db): rename users.email column

BREAKING CHANGE: `users.email` is now `users.email_address`; update queries.
```

## Scopes

Optional, but meaningful: a noun naming the area (`fix(toggle): …`). **In a
monorepo the scope is how releases/changelogs are routed per package** — repos
often *require* it (e.g. `feat(web-app): …`, `feat(react-typed-form-kit): …`).
Keep a scope vocabulary documented so it stays consistent.

## Squash merges: the PR title *is* the commit

With squash merging (the common modern setup), **the PR title becomes the single
commit message on `main`** — so the **PR title must be a valid Conventional
Commit**, or the release/changelog step sees a non-conventional message and skips
it. Put the individual semantic commits in the squash **body** for detail.
[`git-trunk-branch-and-pr-automation`](../git-trunk-branch-and-pr-automation/SKILL.md)
covers the CI that enforces this.

> **Caveat:** the title only becomes the commit when the repo's squash setting is
> **"Default to pull request title"**. With GitHub's out-of-the-box **"Default
> message"**, a *single-commit* PR reuses that commit's message instead of the
> title — so a non-conventional lone commit still skips the release even though the
> PR title looks fine. Set the repo to default to the PR title, or keep the single
> commit conventional too.

- **Single-package repo:** the title's scope is optional.
- **Monorepo:** scope the title to the package, and keep a PR to **one package**
  where practical — a squash collapses everything to one type+scope, so a
  multi-package PR applies the same bump to all and muddies per-package changelogs.

## Writing good ones

- **Imperative mood:** "add", not "added"/"adds" (it completes "this commit will…").
- Keep the subject short: the spec sets no limit; commitlint defaults to 100 chars
  and Git display favours ~72 — match the project's commitlint config. The body
  explains **why**, not what.
- **One logical change per commit.** If a change is genuinely both a feature and a
  fix, split it; if you can't, the type reflects the **highest-impact** change
  (a `feat` that also fixes something is `feat`).
- Reference issues in the **footer**: `Closes #123`, `Refs: ABC-12`.

## Gotchas

- **Non-conventional → silently no release.** A typo'd type or a prose subject is
  *ignored* by the analyzer: no bump, no changelog entry. This is the #1 "why
  didn't it release / why is the changelog blank?" cause — check the merge commit /
  PR title first.
- **Don't hand-write `chore(release): …` commits.** Those are produced *by* the
  release bot; writing one yourself can confuse tooling (and such commits are often
  CI-skipped deliberately).
- **Issue IDs in the subject can misbehave.** A Linear/Jira key like `ABC-123` in
  the subject may auto-transition the ticket or render oddly in changelog links;
  some setups keep IDs in the footer or de-link them (`ABC-123` → `ABC - 123`) in
  the generated changelog.
- **Revert format:** a header `revert: <subject of the reverted commit>` plus a
  **body line** `This reverts commit <sha>.` — that body line is what the parser
  keys on. The semantic-release parser is case-insensitive and also matches git's
  default `Revert "<subject>"` header, so an untouched `git revert` commit *is*
  recognised — but **commitlint / PR-title validators reject `Revert` as a type**,
  so lowercase the header to `revert:` to pass those. Reverts default to a **patch**
  release.

## Verify

- Lint locally or in CI with **commitlint** (`@commitlint/config-conventional`), or
  validate PR titles with a PR-title action (see
  [`git-trunk-branch-and-pr-automation`](../git-trunk-branch-and-pr-automation/SKILL.md)).
- Confirm the intended bump with a semantic-release **dry run**
  (`npx semantic-release --dry-run`) — it prints the next version and release notes
  without publishing.

## See also

Companion skills in this set:

- [`semantic-release-automation`](../semantic-release-automation/SKILL.md) — turns
  these commits into versions, a changelog, and GitHub releases.
- [`git-trunk-branch-and-pr-automation`](../git-trunk-branch-and-pr-automation/SKILL.md)
  — branch naming + squash + the PR-title
  validation that enforces this format.

## Sources

- **Conventional Commits 1.0.0** — grammar, the `!` / `BREAKING CHANGE` rules, the
  `BREAKING-CHANGE` hyphen synonym, and case-insensitivity (except `BREAKING CHANGE`,
  which must be uppercase): <https://www.conventionalcommits.org/en/v1.0.0/>
- **semantic-release `commit-analyzer` default release rules** (`angular` preset) —
  `feat`→minor, `fix`/`perf`→patch, breaking→major, **`revert`→patch**, every other
  type → no release:
  <https://github.com/semantic-release/commit-analyzer/blob/master/lib/default-release-rules.js>
- The type list and per-package scope rules also match conventions enforced in
  production repos (a production app's PR-title validator allows
  `feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`; a production monorepo
  requires per-package scopes).
