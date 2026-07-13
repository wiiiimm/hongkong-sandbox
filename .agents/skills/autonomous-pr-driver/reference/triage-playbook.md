# Triage playbook

Decision rules and command recipes for the resolve-reviews loop. Read this when you
need the exact `gh` calls or the finer judgment rules; the lifecycle overview is in
[`../SKILL.md`](../SKILL.md).

## Fetch the review surface

```bash
PR=123 ; REPO=owner/name
export HEAD=$(gh pr view $PR --repo $REPO --json headRefOid --jq .headRefOid)

# (a) Which reviewers have reported on THE CURRENT HEAD? (a convergence gate — work on
# an older commit doesn't count.) Count BOTH submitted reviews AND inline review
# comments anchored to HEAD: some bots leave only inline comments, no review record, so
# reviews alone would never register them. --paginate walks all pages (reviews come
# oldest-first, so HEAD's are on the LAST page). (jq/gojq read env.HEAD — export it.)
# CAVEAT: GitHub bumps a non-outdated inline comment's commit_id forward to the new head
# on each push, so this can count a reviewer who last commented on an EARLIER push as
# "on HEAD" — don't treat it as sufficient alone. Pair with the bot's check completing
# on HEAD (convergence gate 1) before accepting a reviewer as having weighed in.
{ gh api repos/$REPO/pulls/$PR/reviews  --paginate --jq '.[]|select(.commit_id==env.HEAD)|.user.login'
  gh api repos/$REPO/pulls/$PR/comments --paginate --jq '.[]|select(.commit_id==env.HEAD)|.user.login'
; } | sort -u   # the set of reviewers that have weighed in on the current HEAD

# (b) OPEN FINDINGS = every UNRESOLVED review thread — regardless of which commit it
# was anchored to or when it was posted. THIS is the source of truth for "what's left
# to triage", NOT a commit/time-filtered comment list. `isOutdated` = the thread's
# code changed (a HINT it may be stale — still verify in the file, don't auto-skip).
# --paginate + pageInfo/$endCursor walks ALL pages — `first:100` alone silently drops
# threads past page 1 (the same drop-bug this recipe exists to avoid). Output carries
# the stable id (from the comment body, for Dedup) and falls back line→originalLine for
# outdated/re-anchored threads.
gh api graphql --paginate -f query='
  query($owner:String!,$repo:String!,$pr:Int!,$endCursor:String){
    repository(owner:$owner,name:$repo){ pullRequest(number:$pr){
      reviewThreads(first:100, after:$endCursor){
        pageInfo{ hasNextPage endCursor }
        nodes{ isResolved isOutdated path line originalLine
          comments(first:1){ nodes{ author{login} body url } } } } } } }' \
  -f owner=${REPO%/*} -f repo=${REPO#*/} -F pr=$PR \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved==false)
        | "\(.comments.nodes[0].author.login) | \(.path):\(.line // .originalLine // "file") | outdated=\(.isOutdated) | "
          + ( (.comments.nodes[0].body|capture("BUGBOT_BUG_ID: (?<id>[a-f0-9-]+)")?|.id)    # Cursor
            // (.comments.nodes[0].body|capture("cr-comment:v1:(?<id>[A-Za-z0-9]+)")?|.id)  # CodeRabbit
            // (.path + "#" + (.comments.nodes[0].body|ltrimstr("\n")|split("\n")[0])[0:80]) )'  # stable fallback (no marker): file + first line, so unmarked comments don't look new each pass

# (c) Top-level (issue) comments — some bots post findings/summaries here; these have
# NO thread/resolve state, so dedup them by stable id (next section), not by time.
# FILTER OUT non-findings so they don't re-enter triage forever: your OWN rejection/
# status replies (set ME to the account this loop posts as) and bot summary/linkback
# comments (no actionable finding). Emit id (or first-line fallback) + body preview.
export ME=your-bot-or-username   # <-- the login this loop comments as; skip its own posts
# NOISE is a repo-specific regex of non-finding boilerplate to drop (bot summaries,
# linkbacks). The values below are EXAMPLES from one repo's tooling — replace them with
# your repo's own noise markers (or set to a pattern that never matches to disable). # <-- tune this
export NOISE='linear-linkback|auto-generated comment: summarize'
gh api repos/$REPO/issues/$PR/comments --paginate --jq \
  '.[] | select(.user.login != env.ME)
       | select(.body | test(env.NOISE; "i") | not)
       | "\(.user.login) | "
       + ( (.body|capture("BUGBOT_BUG_ID: (?<id>[a-f0-9-]+)")?|.id)
         // (.body|capture("cr-comment:v1:(?<id>[A-Za-z0-9]+)")?|.id)
         // (.body|ltrimstr("\n")|split("\n")[0])[0:80] )
       + " | " + (.body[0:200])'

# (d) Check rollup + mergeability.
gh pr checks $PR --repo $REPO
gh pr view  $PR --repo $REPO --json mergeable,mergeStateStatus,state,reviewDecision
```

> **Never scope OPEN findings by timestamp or by `commit_id == HEAD`.** Both silently
> drop a finding anchored to an *earlier* commit (or posted just before your poll
> window) whose thread is still **unresolved** — the exact way a real review gets
> missed and the PR is called green with an open issue. Enumerate **all unresolved
> threads** (query b); decide stale-vs-valid by **stable id + verifying the current
> file**, never by when or which commit the comment sits on.

> Big comment bodies can exceed tool output limits — pipe through `jq` slices
> (`.body[0:400]`) or strip HTML `<details>` blocks before reading.

## Poll until checks settle

Don't triage mid-run. Treat as settled when nothing is pending **except** a
human-gated approver. Run this in the background and act when it returns:

```bash
settled=0
for i in $(seq 1 50); do
  # Structured output (don't grep text); FAIL CLOSED — an errored/empty result is
  # treated as "not settled" so a transient gh/network failure can't look settled.
  # gh pr checks exits non-zero while checks are pending/failing but STILL prints the
  # JSON (pending → exit 8, documented; failing → exit 1 per gh source) — so `|| true`
  # keeps the captured stdout (don't clobber it to ""). Only a genuinely empty result
  # (a real gh/network failure) is treated as "not settled".
  checks=$(gh pr checks $PR --repo $REPO --json name,bucket 2>/dev/null) || true
  if [ -n "$checks" ]; then
    # Count REAL (non-human-gate) checks: how many registered, how many still pending.
    # Replace "Approval Agent" with YOUR repo's human-gate check name(s). # <-- tune this
    real=$(printf '%s' "$checks" | jq '[.[] | select(.name|test("Approval Agent")|not)] | length')
    blocking=$(printf '%s' "$checks" |
      jq '[.[] | select(.bucket=="pending" and (.name|test("Approval Agent")|not))] | length')
    # Settle when no REAL (non-gate) check is pending, AND either a real check has
    # registered OR a grace period (~iters*20s) has elapsed. The grace window avoids
    # settling in the startup race (CI not registered yet) while still letting a
    # gate-only / no-CI repo settle (so a passed-gate-only PR isn't stuck until timeout).
    if [ "${blocking:-1}" -eq 0 ] && { [ "${real:-0}" -gt 0 ] || [ "$i" -ge 3 ]; }; then
      echo "settled"; gh pr checks $PR --repo $REPO; settled=1; break
    fi
  fi
  sleep 20
done
# Don't treat "ran out of budget" as success — surface the timeout so the loop can
# decide (a check may be stuck/queued; investigate rather than triage blindly).
[ "$settled" -eq 1 ] || { echo "TIMED OUT — checks never settled"; exit 1; }
```

`bucket` is one of `pass | fail | pending | skipping | cancel`. "Settled" = nothing
**pending** (failed checks *have* finished — you triage those next). Tune the
`test("Approval Agent")` exclusion to whatever human-gated checks your repo has (an
approver that only passes on human review) so they don't spin the loop forever.

## Dedup by finding ID, never by line number

Bots re-anchor the **same** finding to new line numbers on every push, so matching
on `path:line` makes everything look "new." Match on the stable id instead. The
per-bot marker formats below (and the same regexes embedded in queries b/c above) are
canonically tracked in [`known-bots.md`](./known-bots.md) — update all in sync if a
marker format changes:

- **Cursor Bugbot:** `BUGBOT_BUG_ID: <uuid>` in the comment body.
- **CodeRabbit:** `cr-comment:v1:<hash>` — the per-comment id (use this). A
  `fingerprinting:…` marker also appears but is a coarse *category* repeated across
  comments, **not** a per-comment id — don't dedup on it (it would merge distinct findings).
- Others: hash the (rule + file) or the first sentence of the body.

Keep a set of seen/resolved ids across rounds. A finding whose id you've already
resolved is **stale** — but still **verify it's fixed in the current file** (grep the
code) before skipping, in case a later commit regressed it.

## Verify-before-trust

Confirm a claim with a real check rather than trusting the bot *or* your own first
read. Cheap verifications that repeatedly paid off:

- **Shell/regex claims** → write the snippet to a file and run it (inline shell tests
  get mangled by quoting): `printf '%s' "$msg" | grep -E '<pattern>'`, or a tiny
  `bash test.sh`.
- **Code logic** → a 5-line `node`/`python` harness exercising the edge cases.
- **Version / "X is unpublished" claims** → check the tag exists:
  `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` (404 = doesn't exist). Prefer this
  over `releases/latest`, which 404s for repos that tag without publishing a Release
  (common for GitHub Actions).
- **"Does the tool actually do Y"** → check the upstream docs/source, not memory.

If verification contradicts the bot → it's an **invalid** finding (reject). If it
contradicts *you* → fix it.

## Reject criteria

Reject (don't fix) when the finding is:

1. **Factually wrong / hallucinated** (verification disproves it).
2. **Against a documented house rule** (`AGENTS.md`, `CONTRIBUTING`) — cite the rule.
3. **An opinion, not a defect** — style/consistency preference with no correctness
   impact, especially if it conflicts with the repo's conventions.
4. **A suggested fix that's worse** than the current code (e.g. would re-introduce a
   security issue, or override deliberate author intent).
5. **Contradicted by another reviewer** — see below.

## Adjudicating conflicting bots

When two reviewers demand opposite things, pick on **correctness/safety**, not
consensus, and write the reasoning in the reject comment. Worked example: one bot
wanted fork-PR titles validated case-*insensitively* (consistency with the
auto-fixing same-repo path); another wanted them kept **strict**. Strict won —
a fork title can't be auto-corrected and a mis-cased `Feat:` doesn't match
semantic-release's release rules, so lenient would silently under-release.

## Posting comments / @-mentions

```bash
# A standalone PR comment (rejections, status summaries, @-mention nudges).
gh pr comment $PR --repo $REPO --body "$(cat <<'EOF'
Rejecting <finding>: <one-line reason>.
EOF
)"
# Append "@coderabbitai — resolved on HEAD, please re-scan" to the body ONLY to teach a
# learner with a genuine insight (two-axes rule below) — not on every reject.
```

- Tag per the two-axes decision in `SKILL.md` (values in
  [`known-bots.md`](./known-bots.md)): **teach** only learners (e.g. `@coderabbitai`
  re-scans and records Learnings), and only with a real insight to give; **re-trigger**
  only on-demand-cadence reviewers (`@handle review`) when you need their pass on a new
  HEAD — per-push bots re-review themselves.
- Don't tag bots that have re-posted resolved findings repeatedly — it's noise; and if
  a bot you've engaged keeps treating replies as fresh work, stop tagging it entirely.
- If a `gh` write 401s but `gh api` reads work, the token is read-restricted/expired
  (`gh pr create`/`gh pr comment` use GraphQL). REST fallbacks:
  - **open a PR:** `gh api repos/$REPO/pulls -X POST -f title=… -f head=… -f base=… -f body=…`
  - **post a comment:** `gh api repos/$REPO/issues/$PR/comments -X POST -f body=…`
  - If REST also 401s, the token itself is bad → ask the human to `gh auth login`
    (or, for opening a PR, surface a compare URL they can click).

## Auth & transport gotchas

- Git **push** over SSH can succeed while the **`gh` API token** is invalid — check
  `gh auth status` if API writes fail but pushes don't.
- A release/commit made with the built-in `GITHUB_TOKEN` won't trigger downstream
  `push` / `pull_request` / `release` `on:` workflows (a PAT/bot token does) —
  relevant when a deploy/check only fires on a bot action. *(Exception:
  `workflow_dispatch` / `repository_dispatch` can still be fired with `GITHUB_TOKEN`.)*

## Convergence — the honest definition

Hand off only when **all three** hold, all keyed on the **current HEAD SHA**, never
on wall-clock:

1. **Every expected reviewer has weighed in on the current HEAD.** The **expected set
   is the per-push automated reviewers** — the bots that re-review every commit (those
   posting a check on the PR, or that re-reviewed a prior push) — **plus any on-demand
   reviewer whose sign-off you still need**: on-demand bots don't re-review a new
   commit on their own, so re-trigger them (`@handle review` — cadence per
   [`known-bots.md`](./known-bots.md)) and wait for the fresh pass; don't silently
   drop them from the set (if you decide a bot's sign-off isn't required, say so in
   the summary). It is **not** every login that ever commented. The reliable per-bot
   signal is its **check completing on HEAD** (the settle-poll already waits for that)
   and/or a review or inline comment attached to HEAD. A top-level **issue comment counts only when it explicitly names the current HEAD SHA** (issue comments aren't commit-attached — a stale one must not satisfy this gate); otherwise treat it as a finding input, not reviewer-completion evidence. **Do not block
   handoff on one-shot or human reviewers** who won't re-post on each push — their
   input is captured as open findings in gate 2, which you address regardless. A green
   check alone can precede the comments, so it's never sufficient on its own — pair it
   with gate 2.
2. **No open finding remains untriaged on HEAD** — covering **both** sources: every
   **unresolved review thread** (query b) *and* every finding posted as a **top-level
   issue comment** (query c — these have no thread/resolve state, so track them by
   stable id **when available, else by rule+file identity** — see `known-bots.md`).
   Enumerate in full (no time/commit slice); each must reach a **terminal
   verdict** — fixed, rejected-with-reason, confirmed stale by checking the file, or
   kept-with-reason. A **`Deferred`** finding is *not* terminal: it blocks hand-off
   unless it's tracked in a follow-up issue/PR *and* the human has accepted the
   deferral (see the status-table verdicts in `SKILL.md`).
3. **All required checks green.**

Non-deterministic LLM reviewers keep emitting marginal/duplicate comments, so "zero
open findings" isn't always reachable — but every finding (thread **or** issue comment)
must be *accounted for* (fixed / rejected / stale / kept-with-reason, or an
accepted-and-tracked `Deferred`), never skipped because of when or which commit it sits
on. Document rejected/stale/kept items and any accepted deferral, then hand off.
