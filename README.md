# figma-to-roblox-ui

A Claude skill for importing Figma frames and designs into Roblox Studio GUI with high fidelity.

## What it enforces

- **Scale only, Offset = 0** — `Size`, `Position`, list/grid padding, `UIPadding`, `UIShadow`.
- **UIStroke** always in `StrokeSizingMode.ScaledSize` (`Thickness = strokeWeight / min(w, h)`).
- **UICorner** in Scale (`radius / min(w, h)`, `0.5` = pill/circle), including per-corner radii.
- **Detailed art and non-standard shapes are exported as images** (PNG → ImageLabel/ImageButton), while layout and text stay native — the way pro Roblox UI designers work.
- Image limits handled: ≤ 1024 px, 9-slice, spritesheets, tiling for large art, `ImageColor3` tinting for color variants.
- `TextScaled` + `UITextSizeConstraint` for all text.
- A Luau **validator** that flags any leftover Offset, FixedSize strokes, px radii, non-scaled text or empty images.

## Contents

- Figma prep checklist and a native-vs-image decision guide
- px → Scale formulas and a Figma → Roblox property mapping table
- Luau helpers (`place`, `corner`, `stroke`, `aspect`, `text`, `image`)
- Upload, performance, build order, visual QA and common mistakes

Works with the Figma MCP (`get_metadata`, `get_design_context`, `get_screenshot`, `download_assets`) and the Roblox Studio MCP (`execute_luau`, `screen_capture`), and for checking output from import plugins (FigBloxUI, RoImport, Bloxporter, Figma To Roblox).

## Install

Claude Code / Agent SDK:

```bash
git clone https://github.com/xtrair/figma-to-roblox-ui ~/.claude/skills/figma-to-roblox-ui
```

Claude app: download the repo as a zip and upload it as a custom skill in the app settings.

## Not covered yet

Window/transition animations, button logic, list item templates, gamepad selection, ViewportFrame previews, StyleSheets, localization.

## License

MIT
