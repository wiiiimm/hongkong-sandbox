# Agent Instructions

This repository builds and renders Hong Kong / Lantau terrain outputs with Codex, Claude Code, and Claude Cowork. The primary deliverable is the interactive 3D terrain viewer in `3d-viewer/`, intended for deployment to Vercel.

## Project Root & Version Control

- **This top-level folder is the single project root.** All agents work directly in it — there are no per-agent working folders anymore.
- This project is (being) tracked as a **git repository**. Commit meaningful units of work; keep generated artefacts and source references in their documented locations rather than scattering scratch files at the root.
- Deployment target is **Vercel** (static hosting for the viewer). Keep the deployable app self-contained and buildable from the repo.

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
