---
name: skill-publishing
description: How to author and publish agent skills for the skills.sh / `npx skills` ecosystem — the SKILL.md format, why the frontmatter description is the trigger, multi-skill repo layout, the `skills` CLI (init/add/list/find/update/remove with flags), publishing to GitHub with SEO metadata, and public vs private repos (it git-clones, so private works with auth). Use when asked to "create/write/author a skill", "publish a skill", "set up a skills repo", "make a skill installable/discoverable", "use npx skills", or "can I use a private skills repo".
metadata:
  author: stealth-engine
  co-author: wiiiimm
  version: "1.1.0"
---

# skill-publishing

How to write a good agent skill and publish it so others (and your other
machines) can install it with `npx skills`.

## What a skill is

Reusable, **on-demand context** for an AI coding agent. One skill = one folder
with a `SKILL.md`:

```markdown
---
name: my-skill            # kebab-case, matches the folder
description: <one line>    # the TRIGGER — see below; most important field
metadata:
  author: you
  version: "1.0.0"        # semver; bump on meaningful change
---

# Title

<the body the agent loads only when this skill fires>
```

**Context economy:** only the `description` of every installed skill stays in the
agent's context. The body loads **only when the description matches** the task.
That's the whole design — so the description does the heavy lifting.

## The `description` is the trigger (get this right)

Write it as **concrete triggers**: what it does, then "Use when …" listing
symptoms, situations, and phrases a user might actually say.

- Good: `…Use when an iPhone page shows black bars, content is cut off at the bar
  edge, a cropped shadow, or the page jumps after the keyboard closes.`
- Bad: `Helps with iOS Safari styling.`

If the agent won't *match* it to the right moment, the skill is dead weight.

## The body

- Write for the **agent**, not end users: actionable facts, steps, rules.
- **Scannable**: headings, short sections, tables, code blocks.
- **Progressive disclosure**: keep `SKILL.md` focused; put heavy reference docs or
  scripts in sibling files and link them so they load only when needed.
- Prefer **facts + case-dependent guidance** over one rigid recipe, so it stays
  useful across situations.
- Note **provenance** for non-obvious claims (how it was verified) to earn trust.
- One concern per skill — split rather than overload.

## Bundling files in a skill (progressive disclosure)

A skill is a **directory**, not just one file. `SKILL.md` is the entry point; you
can ship reference docs, scripts, templates, and assets next to it:

```text
skills/my-skill/
  SKILL.md                 # entry: frontmatter + concise body
  reference/
    api.md                 # deep detail / long tables — read on demand
  scripts/
    init.sh                # a runnable helper the skill invokes
  templates/
    config.example.json    # boilerplate the skill copies
```

Only `SKILL.md`'s body loads when the skill fires; **everything else loads,
reads, or runs only when `SKILL.md` tells the agent to**, referenced by relative
path. Keep `SKILL.md` short and high-signal; push heavy material into siblings:

```markdown
For the full option list, read `reference/api.md`.
Scaffold with `scripts/init.sh <name>`.
```

The CLI installs the **whole directory** (symlink or `--copy`), so relative links
keep working. Split only when a skill gets large or needs runnable helpers — a
small skill is perfectly fine as a single `SKILL.md`.

## Repo layout (bundling many skills)

```text
skills/<skill-name>/SKILL.md            # flat (preferred)
skills/<category>/<skill-name>/SKILL.md # categorised (only if you have enough)
SKILL.md                                # a single skill at repo root also works
```

- **No manifest required** — the CLI auto-discovers those paths.
- **Don't put a root `SKILL.md` alongside a `skills/` dir**: a root `SKILL.md`
  **short-circuits discovery** — the CLI treats the repo as one skill and never
  scans subdirectories unless consumers pass `--full-depth`. Use one layout or
  the other.
- `README.md` = the **human** index (a table of skills) + SEO. The machine index
  is just each skill's `description`; no separate index file.
- `AGENTS.md` (+ `CLAUDE.md` symlink) = authoring conventions for the repo.
- A `.claude-plugin/marketplace.json` manifest is **optional**, only for
  plugin-marketplace features or non-standard skill paths.

## The `skills` CLI (vercel-labs/skills)

```bash
npx skills init skills/<name>        # scaffold a new skill folder + SKILL.md

npx skills add owner/repo            # interactive: pick skills + agents
npx skills add owner/repo --list     # browse the repo, install nothing
npx skills add owner/repo --skill a b   # install specific skills
npx skills add owner/repo --all -g   # everything, all agents, global — no prompts
npx skills add owner/repo --copy     # copy instead of symlink into agent dirs

npx skills list                      # installed skills (-g for global)
npx skills find <keyword>            # search
npx skills update [name...]          # update
npx skills remove [name...]          # remove
npx skills use owner/repo@skill      # one-off prompt without installing
```

Flags that matter: `-s/--skill`, `-a/--agent` (`*` = all), `-g/--global`,
`-l/--list`, `-y/--yes` (skip prompts), `--all`, `--full-depth` (scan every
subdirectory even when a root `SKILL.md` exists — needed for a repo that has both
a root skill and a `skills/` dir). Telemetry is on by default; set
`DISABLE_TELEMETRY=1` (or `DO_NOT_TRACK=1`) to opt out.

> Provenance: CLI commands, flags, and behaviour verified against `skills`
> v1.5.x (2026-07). The CLI iterates fast — re-check flags if it's since moved.

## Publishing to GitHub

```bash
git init && git add -A && git commit -m "chore: bootstrap skills repo"
gh repo create owner/skills --public --source=. --push
# SEO: a clear description + topics make it discoverable
gh repo edit owner/skills \
  --description "Agent skills for … — install: npx skills add owner/skills" \
  --add-topic agent-skills --add-topic claude-skills --add-topic claude-code \
  --add-topic skills --add-topic ai-agents
```

Keep the README's skills table and each `description` sharp — those are what
both humans and `npx skills find` read.

## Public vs private

`npx skills add` **`git clone`s** the repo under the hood (defaulting to the
HTTPS URL) — apart from a no-clone GitHub-API fast path reserved for a few
allowlisted first-party owners (e.g. `vercel`), any other repo is cloned. So:

- **Public** → clones with no auth.
- **Private** → works too, **if the machine is authed to clone it**. For HTTPS,
  run `gh auth setup-git` once so git uses your GitHub login non-interactively;
  or pass an SSH URL directly: `npx skills add git@github.com:owner/repo.git`.
- Anyone you share the install command with also needs repo access + auth, and
  public discovery surfaces (skills.sh leaderboard/search) only index **public**
  repos. So: private = great for personal/studio use; public = shareable +
  discoverable.

## Checklist before publishing a skill

- [ ] Folder is `skills/<kebab-name>/` and `name:` matches.
- [ ] `description` reads as triggers ("Use when …"), not marketing.
- [ ] Body is actionable, scannable, one concern.
- [ ] `metadata.version` set (semver).
- [ ] Added to the README skills table.
- [ ] `npx skills add <repo> --list` shows it with the right description.
