# Agent Instructions

This repository builds and renders Hong Kong / Lantau terrain outputs with Codex, Claude Code, and Claude Cowork. The primary deliverable is the interactive 3D terrain viewer in `3d-viewer/`, intended for deployment to Vercel.

## Project Root & Version Control

- **This top-level folder is the single project root.** All agents work directly in it — there are no per-agent working folders anymore.
- This project is (being) tracked as a **git repository**. Commit meaningful units of work; keep generated artefacts and source references in their documented locations rather than scattering scratch files at the root.
- **Use semantic / conventional commit messages** (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `perf:`, etc.). Commit as you go — one logical change per commit — rather than batching unrelated changes.
- Deployment target is **Vercel** (static hosting for the viewer). Keep the deployable app self-contained and buildable from the repo.

## Project Management

- Work for this repo is tracked in **Linear** under team **HKS** (Hong Kong Sandbox) —
  this one team owns the whole repo: https://linear.app/stealth-company/team/HKS/overview
- There are **two Linear projects** under that team:
  - **Hong Kong Sandbox** — the main / general project (most issues go here):
    https://linear.app/stealth-company/project/hong-kong-sandbox-e6dde81f1f15/overview
  - **HK Sandbox Community** — the social/community arm, organised into four milestones
    (M1 stats & leaderboards · M2 accounts & identity · M3 historical-reconstruction
    pipeline · M4 era themes & community building):
    https://linear.app/stealth-company/project/hk-sandbox-community-13d43e3f3c93
- When creating an issue, file it under the **HKS** team and pick the right project:
  stats/leaderboards, accounts, old-Hong-Kong reconstruction, era themes, or any
  user-generated/social feature → **HK Sandbox Community** (assign the fitting
  milestone); everything else → the main project.
- Historical note: two earlier projects — *Hong Kong Sandbox · Leaderboard* and
  *Reconstruct Old Hong Kong in 3D* — were merged into HK Sandbox Community
  (12 Jul 2026); both are Canceled in Linear with pointer notes.
- Reference the relevant Linear issue (e.g. `HKS-123`) in commits/PRs when a change maps to one.
- **Completion includes Linear updates.** After every completed implementation or subagent hand-off, update the relevant existing issues in the authorised milestone, their parent progress and the milestone overview before reporting completion. Include the commit, delivered behaviour, verification/evidence, executor and remaining gaps; synchronise local tracking notes. Use In Review for implemented work awaiting review and close broader issues only when all acceptance criteria pass. Report any failed Linear write as pending rather than claiming it succeeded. For Astra city work, the authorised milestone is **Astra - Living Hong Kong — buildings, regional detail & feature parity** in the main Hong Kong Sandbox project. Standing authorisation is already given; routine updates do not need another permission request.

## Project Context

- Treat `references/lantau-maps/` as the source reference set for Lantau map work.
- The folder contains historical maps, stitched map tiles, contact sheets, manifests, and notes for different Lantau naming, contour, coastal, and cartographic styles.
- Read `references/lantau-maps/README.md`, `references/lantau-maps/SECOND_PASS_README.md`, and the relevant manifest entries before relying on an image.
- `references/codex/` holds Codex's prior implementation (viewers, meshes, vector B50K skin data, illustrations). Treat it as **read-only reference** — study it and reuse its data/techniques, but build new work in the main project folders (`3d-viewer/`, `source-scripts/`, `docs/`).
- Preserve source provenance. When a rendered output depends on a reference map, record the source filename and any important source-page or licence details in the output notes or nearby metadata.

## Working Layout

- `3d-viewer/` — the deployable interactive viewer and its build scripts/data.
- `source-scripts/` — reproducible DEM pipelines (`srtm-30m/`, `hk-5m/`).
- `docs/` — method and provenance notes.
- `references/` — read-only source references (`lantau-maps/`) and prior work (`codex/`).
- Keep drafts, scripts, and intermediate files alongside the component they belong to. If an output is a shared final deliverable, include a short note identifying which agent produced it and which `references/lantau-maps/` sources were used.

## Working Rules

- Prefer small, reproducible scripts and documented commands over manual-only image edits.
- Keep generated outputs separate from source references. Do not modify files inside `references/` (neither `lantau-maps/` nor `codex/`) unless the task is explicitly to curate or repair the reference set.
- Use descriptive filenames that include the map area, style, date or version, and output dimensions when relevant.
- If a process creates intermediate files, keep them next to the component they belong to rather than mixing them with the archival references in `references/`.
- Before large or risky transformations, make an adjacent backup or keep the original input untouched.

## Map And Geography Quality

- **Astra City uses fixed 1× vertical scale.** User decision, 7 September 2026: do not port vertical exaggeration, a vertical multiplier or an “epic mountains” height setting. Terrain, buildings, bridges, water/tides, navigation, collisions and camera altitude share real-world metres/HKPD. Ignore legacy VE settings/URL parameters in City. Preserve surveyed elevations; source-backed terrain corrections and explicitly labelled estimates remain allowed. This is an explicit exception to original-game feature parity.

- Cross-check generated maps against the reference set rather than trusting plausible-looking output.
- Pay attention to historical naming variants such as Lantau, Lantao, Lan Tao, Lanto, Tai Yue Shan, Tai-ü-shan, Nam-tao/Nam Tau, Tyho, 大嶼山, 爛頭島, 爛頭山, 大庾山, 大虞, and 大奚山.
- For contour, terrain, coastline, and place-name placement work, verify the shape and relative geography against multiple references when possible.
- Be explicit when a source is a full map, a crop, a stitched tile set, a nautical chart, or a low-resolution contextual reference.
- Do not fabricate precision. If the references do not support exact placement, label the result as approximate and explain the basis.

## Rendering And Export Quality

- Render final raster outputs at the target dimensions or a documented supersampled scale. Avoid scaling up a low-resolution preview canvas for final export.
- Check final output sharpness, alignment, cropping, transparency/background, and text legibility before calling a render complete.
- When browser or canvas rendering is involved, verify the exported file itself, not only the on-screen preview.
- For poster, wallpaper, or print-sized outputs, document dimensions, scale factor, and export format.

## Collaboration Notes

- Codex and Claude should use this file as the shared project instruction source.
- `CLAUDE.md` should remain a symlink to `AGENTS.md`.
- Keep task-specific notes close to the generated artefacts so another agent can resume the work without reconstructing decisions from chat history.

- For source-backed building/landmark refinement and cross-device resumption, use the repository skill at `.agents/skills/hong-kong-model-improvement/SKILL.md`; its supporting references route to the existing scripts and portable hand-off.
