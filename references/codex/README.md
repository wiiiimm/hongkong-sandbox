# Codex Workspace

This folder contains generated work and implementation notes for the Lantau map and terrain rendering project.

## Current Packages

- `hongkong-3d-model/` - canonical rotatable 3D Hong Kong and Lantau terrain viewer. It includes all terrain sources and dropdown pickers.
- `hongkong-3d-model/hong-kong-3d-viewer.html` - whole-Hong-Kong 3D terrain viewer with LandsD 5 m / AWS Terrarium source switching and B50K GML skins.
- `illustrations/` - generated 2D skyline, logo, and engraved illustration outputs plus the scripts used to make them.
- `reference/` - generated screenshots, previews, and visual reference exports. These are not source-of-truth assets.
- `archive/` - earlier standalone 3D packages and root-level prototypes retained for provenance.

## 3D Viewer

Open the consolidated viewer at:

```text
http://127.0.0.1:4173/hongkong-3d-model/index.html
```

The dropdown contains:

- `Hong Kong LandsD 5 m DTM` - preferred source for the whole-Hong-Kong model.
- `AWS Terrarium Terrain Tiles` - public terrain source for comparison.
- `Lantau LandsD 5 m DTM` - isolated Lantau model.
- `Lantau AWS Terrarium Terrain Tiles` - isolated Lantau comparison model.

See `hongkong-3d-model/README.md` for data sources, generation scripts, and modelling caveats.
