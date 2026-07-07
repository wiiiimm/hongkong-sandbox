# Reviewer prompts, CLI recipes & report template

Copy-paste material for [`../SKILL.md`](../SKILL.md). Fill the `{{placeholders}}`.

---

## Reviewer A — Sonnet subagent (general code review)

Spawn a subagent with **model `sonnet`**, read-only intent (it returns findings; it
does **not** edit). Give it the diff plus the changed files for context.

> You are an independent code reviewer. Review **only the change set below** against
> the rest of the repo for context. Do not review unrelated code.
>
> Base: `{{base}}` · Changed files: `{{file list}}`
> Diff:
> ```diff
> {{the scoped diff from SKILL.md §1 — committed: `git diff <base>...HEAD`;
>   uncommitted: `git diff` + `git diff --staged`; all: `git diff $(git merge-base <base> HEAD)`. Use
>   whichever scope you chose, and feed the SAME scope (and `-t` value) to Reviewer B.}}
> ```
>
> Read the full changed files (and immediate callers) as needed for context, but
> **report only on changed lines**. Look for: correctness bugs, security issues,
> broken edge cases, race conditions, resource leaks, error-handling gaps, API
> misuse, and regressions. Skip pure style unless it causes a bug.
>
> Return a JSON array; each item:
> `{ "file": "", "line": 0, "severity": "critical|warning|info", "claim": "what's
> wrong, one sentence", "evidence": "why it's wrong", "fix": "suggested change" }`
> Return `[]` if nothing real. Do not invent issues to seem thorough — a clean diff
> is a valid result.

**Large-diff variant — don't inline a huge diff.** Subagents share the working
directory, so for a big change set, pass the **base ref + scope** and have the subagent
produce the diff itself instead of pasting it into the prompt (keeps the orchestrator
message and the subagent's context lean). Swap the `Diff:` block above for:

> Base: `{{base}}` · Scope: `{{committed|uncommitted|all}}`
> Generate the diff yourself, then review only it:
> - committed: `git diff {{base}}...HEAD`
> - uncommitted: `git diff` **and** `git diff --staged`
> - all: `git diff $(git merge-base {{base}} HEAD)`
>
> Use the SAME scope handed to Reviewer B. Read full changed files for context; report
> only on changed lines. Same JSON output shape as above.

**Optional extra lenses (Reviewer C+)** — same shape, swap the focus line:
- *Security:* "Focus on authn/authz, injection, secrets, SSRF, unsafe deserialization,
  path traversal, and untrusted-input handling."
- *Performance:* "Focus on N+1 queries, unbounded loops/allocations, blocking I/O on
  hot paths, and missing caching/pagination."

---

## Reviewer B — CodeRabbit CLI

This invokes the **CodeRabbit CLI directly** — it does *not* depend on CodeRabbit's
own `code-review` skill being installed, only on the `coderabbit` binary + auth. Run
it inside a subagent (ideally `run_in_background` — reviews can take minutes). Confirm
auth first; if it fails, report "CodeRabbit unavailable" and let the orchestrator
proceed with the other reviewer(s). Report unavailability **distinctly from an empty
result** — an absent Reviewer B must not be counted as a clean pass (that would hide a
reviewer that never ran).

`{{type}}` below **must match the scope Reviewer A got** (§1): `committed`,
`uncommitted`, or `all`. `--base` applies to `committed`/`all`; drop it for a purely
`uncommitted` review.

```bash
# Availability gate. UNAVAILABLE is a distinct outcome from "reviewed, no findings" —
# emit a clear status marker, never an empty `[]` (which the orchestrator would read as
# a clean review), so Reviewer B is counted as absent, not passing. Distinguish
# "binary missing" from "installed but not logged in" — they need different fixes.
if ! command -v coderabbit >/dev/null 2>&1; then
  echo 'STATUS=coderabbit-unavailable reason=not-installed'; exit 0
fi
if ! coderabbit auth status >/dev/null 2>&1; then
  echo 'STATUS=coderabbit-unavailable reason=not-authenticated'; exit 0
fi

# ONE review, scoped to {{type}} (committed|uncommitted|all). --base is included for
# committed/all and omitted for uncommitted. Swap --agent for --plain for text output.
base_flag=""; [ "{{type}}" = uncommitted ] || base_flag="--base {{base}}"
coderabbit review --agent -t {{type}} $base_flag
```

- `-t` — review type: `all` | `committed` | `uncommitted` — **match the diff you scoped.**
- `--base` — branch to compare against (e.g. `main`); omit for `uncommitted`.
- `--agent` — structured JSON for agent/skill integrations; `--plain` — detailed text.
- Flags evolve — run `coderabbit review --help` to confirm the current set before relying on it.

**Alternative — delegate to CodeRabbit's own skill.** If [`coderabbitai/skills`](https://docs.coderabbit.ai/cli/skills)
is installed, the subagent can instead trigger CodeRabbit's `code-review` skill in
natural language ("review the {{type}} changes against {{base}}") and let it drive the
CLI. That's less control over scope/output (so harder to dedupe), but stays current
with CodeRabbit's own flags. The direct CLI call above is the default for this reason.

CodeRabbit groups findings by **Critical / Warning / Info**; map those onto the same
`{file, line, severity, claim, evidence, fix}` shape so they merge cleanly with
Reviewer A's. Return the normalized array to the orchestrator.

---

## Parallel fix-subagent (one per valid, independent issue)

Only after triage. One issue per subagent; **never two fixers on the same file at
once** (partition by file or give each an isolated worktree).

> Apply this single, pre-approved fix. Scope: **one file, one issue.** Do not refactor
> beyond it or touch other files.
>
> File: `{{file}}` · Issue: `{{claim}}` · Approved fix: `{{fix}}`
>
> Make the minimal change in the surrounding code's style. Then verify it (build /
> relevant test / re-read) and report back: `{ "file": "", "applied": true|false,
> "how": "what you changed", "verified": "what you ran/checked" }`. If the fix turns
> out wrong or unsafe, make **no** change and report `applied: false` with why.

---

## Final report template

```markdown
## Dual-agent review — {{base}}...HEAD ({{N}} files)
Reviewers: Sonnet · CodeRabbit{{· extra lenses}}   ({{mark any that were UNAVAILABLE — e.g. "CodeRabbit: unavailable (not authenticated)" — so the reader knows it didn't run}})

### ✅ Fixed ({{count}})
- **{{file}}:{{line}}** — {{claim}} _(flagged by: {{A/B/both}})_
  → {{how it was fixed}}; verified: {{check}}

### ⛔ Ignored / rejected ({{count}})
- **{{file}}:{{line}}** — {{claim}} _(flagged by: {{A/B}})_
  → Rejected: {{one-line reason}}

### ⏸ Deferred / needs human ({{count}})
- **{{file}}:{{line}}** — {{claim}}
  → {{why deferred / what decision is needed}}

### Adjudicated disagreements
- {{reviewer A said X, B said Y → call + why}}

**Tally:** fixed {{n}} · rejected {{m}} · deferred {{k}} · verify: {{pass/fail + what ran}}
```

Keep it honest: only list under **Fixed** what the verify step actually confirmed. A
finding you consciously declined goes under **Ignored / rejected** (with its reason); a
real one you couldn't safely fix goes under **Deferred**. An *unverified* fix is
**Deferred**, never **Fixed**.
