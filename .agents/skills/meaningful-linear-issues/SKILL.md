---
name: meaningful-linear-issues
description: "Create complete, analytics-ready Linear issues in ONE pass — resolve the right project (never guess it), and proactively fill the metadata that's technically optional but matters for planning/analytics: priority, estimate, labels (a Type + an Area from the team's existing taxonomy), milestone, assignee, cycle, and relations. Use when asked to 'create/file/open a Linear issue', 'log a ticket', 'add this to Linear', 'make an issue for X', or before any Linear `save_issue` that **creates** an issue or **backfills** missing metadata on a bare one — so the user doesn't have to come back and ask for the labels/estimate/project a second time, and so an issue doesn't land in the wrong project. NOT for routine field edits (status changes, reassignments) — those are also `save_issue` but don't need this."
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "1.1.0"
---

# Meaningful Linear issues

A good issue is **not** just a good description — that's the easy half. The half
agents skip is the **metadata** that makes Linear actually work as a planning tool:
estimates feed cycle velocity, labels feed breakdowns, milestones feed roadmaps, the
project feeds everything. Those fields are *optional in the API*, so agents leave them
blank and the user has to come back and ask again.

**Flip the default: metadata is opt-OUT, not opt-in.** Resolve and fill it **before**
calling `save_issue`, in one pass — propose concrete values, don't omit.

## Cardinal rule: never guess the project

The single worst failure is dropping an issue into the **wrong/random project**.
Resolve the project in this order — **stop at the first that's certain**:

1. **Context** — the issue's repo/area maps to a known project; the user named it; a
   sibling issue you're relating to has one.
2. **Confirm** — call [`list_projects`](#discover-valid-values) and match by name; if
   one clearly fits, state which and proceed.
3. **Ask** — if it's still ambiguous, **ask the user which project** rather than
   picking one. A missing project is recoverable; a wrong one quietly pollutes the
   wrong roadmap.

Never pass a `project` you inferred from vibes. Team is required too — usually
unambiguous from the project, but resolve it the same way.

## The one-pass workflow

1. **Discover** what's available (only what you don't already know): projects, the
   team's label taxonomy, milestones, the current cycle, assignable users.
2. **Draft** the issue with **every applicable field filled** (checklist below).
3. **Create** with one `save_issue` call. If anything was genuinely a judgment call
   (estimate, priority), **state the values you chose** so the user can correct one —
   that's still one pass, not "I left them blank, ask me again."

## Create vs. backfill — mind the `id`

Same checklist, two `save_issue` modes — **don't conflate them**:

- **Create** (new issue): `save_issue` with **no `id`**. Fill everything below.
- **Backfill** (existing bare issue): `save_issue` **WITH its `id`** — *update*, don't
  create. Omitting the `id` here would **make a duplicate**. `get_issue` first if you
  need to see what's already set, then pass only the fields you're adding. **`labels`
  replaces the whole set** — include existing labels alongside the new ones. Relations
  (`blocks` / `blockedBy` / `relatedTo`) are **append-only** — adding one won't drop
  existing links (use `removeBlocks` / `removeBlockedBy` / `removeRelatedTo` to remove).
  Other fields you don't pass are left untouched.

## Metadata checklist — fill before `save_issue`

| Field | How to set it well |
| --- | --- |
| **team** *(required)* | From the project. `list_teams` / `get_team` if unknown. |
| **project** | **Resolve, never guess** (above). |
| **title** | Imperative, specific, scannable. Lead with the verb + the object. |
| **description** | The implementation detail (see [template](#description-template)). |
| **priority** | `1` Urgent · `2` High · `3` Medium · `4` Low · `0` None. Infer from impact/urgency; default `3` for normal work, ask if it's clearly load-bearing. |
| **estimate** | Set a real value; Linear **snaps it to the team's scale**, so you don't need the scale up front — but **read back and surface the stored value** (it may change: `3` on an *exponential* team `0,1,2,4,8,16` returns `4`; Fibonacci `0,1,2,3,5,8` keeps `3`). `get_team` doesn't expose the scale (as of this MCP version) — infer it from existing issues' estimates (`list_issues`) only if you need exact pointing. Some teams **disable** estimates — if `save_issue` rejects it, drop the field. |
| **labels** | Pick from the **existing taxonomy** (`list_issue_labels` for the team) — **don't invent labels**. Typically one **`Type`** (Feature / Bug / Improvement / Chore / Docs / Refactor / Security / Performance / Test / …) **and** one **`Area`** (the relevant module/domain). Match the team's grouped labels rather than guessing names. |
| **assignee** | `"me"`, the named owner, or the project/issue's usual owner (`list_users` to resolve a name/email). Don't leave unassigned if an owner is obvious. |
| **milestone** | `list_milestones` for the project; attach if one fits the work. (None exist? skip — don't fabricate.) |
| **cycle** | **Set the current cycle** (`list_cycles` → `current`) for active work unless the user opts out — **don't rely on auto-add**, which some teams disable, leaving the issue out of every cycle (and out of velocity). Skip only for backlog/future work that isn't for the current cycle. |
| **relations** | `parentId` for sub-work; `blocks` / `blockedBy` for ordering; `relatedTo` for siblings. Link issues you reference in the description — it's cheap and powers dependency views. |
| **dueDate** | ISO date (`YYYY-MM-DD`). Set only when there's a real deadline — a launch, a dependency, a commitment. Don't fabricate one; most issues have none. |

If a field genuinely doesn't apply (e.g. no milestones exist), skip it **knowingly** —
the goal is "nothing useful left blank," not "every field stuffed."

## Discover valid values

Only the values you don't already have in context. These are the Linear MCP tools:

- `list_projects` (filter by name/team) — resolve the project.
- `list_issue_labels` (by `team`) — the label taxonomy; reuse, don't invent.
- `list_milestones` (by `project`) — fitting milestone, if any.
- `list_cycles` (by `teamId`, `type: current`) — to set the current cycle (don't rely on auto-add).
- `list_users` (by name/email, or `"me"`) — resolve an assignee.
- `list_teams` / `get_team` — when the team isn't obvious from the project.

Then create with `save_issue` (omit `id` to create). `labels` and `assignee` accept
**names or IDs**; `priority` is the `0–4` int.

## Description template

Keep what makes implementation unambiguous; drop ceremony:

```markdown
<one-line summary of the outcome>

## Context / problem
<why this exists; the symptom or goal; link related issues/PRs>

## Scope
<what's in; explicitly what's out>

## Acceptance
<how we'll know it's done — checkable bullets>
```

Use **real newlines and markdown**, not escaped `\n`. Mention related issues by ID so
Linear links them (and add them to `relatedTo`).

## Gotchas

- **Don't guess the project** — the one unrecoverable mistake. Ask if unsure.
- **Estimate snaps to the team's scale** (a passed `3` stores as `4` on an exponential
  team) — **read back and surface the stored value** so the snap isn't silent; and some
  teams disable estimates entirely — drop the field if it's rejected.
- **Labels must already exist** — pull them from `list_issue_labels` and pass the
  exact names; creating ad-hoc labels pollutes the taxonomy. Prefer one Type + one Area.
- **Milestone belongs to a project, cycle belongs to a team** — don't cross them; a
  milestone from another project will be rejected.
- **Don't rely on cycle auto-add** — some teams disable it, leaving the issue out of
  every cycle. Set the current cycle explicitly; skip only for backlog/future work.
- **One pass, not two** — if you're unsure of priority/estimate, pick a sensible value
  and *say so*; don't ship a bare issue and wait to be asked for the rest.

## Pre-flight checklist (before `save_issue`)

- [ ] **Project resolved** (from context/confirmed/asked) — **not** guessed.
- [ ] Team set; title imperative + specific; description has context + scope + acceptance.
- [ ] Priority set; estimate set (or knowingly skipped if the team disables it).
- [ ] Labels: a **Type** (always) + an **Area** *if one fits* — from the existing taxonomy, not invented.
- [ ] Assignee set (or deliberately left for triage); milestone attached if one fits.
- [ ] Relations linked for any issues/PRs referenced.
- [ ] Anything you judged (priority/estimate) stated back to the user in your reply.

## See also

- [`conventional-commits`](../conventional-commits/SKILL.md) — the matching discipline
  for commit/PR titles, so the issue → branch → PR → release chain stays clean.

## Sources

- Linear MCP tool surface (`save_issue`, `list_projects`, `list_issue_labels`,
  `list_milestones`, `list_cycles`, `list_users`, `get_team`) and observed behaviour:
  estimates snap to the team's scale, new issues auto-join the active cycle *when the
  team enables auto-add* (don't rely on it), labels are a grouped Type/Area taxonomy
  that must pre-exist.
