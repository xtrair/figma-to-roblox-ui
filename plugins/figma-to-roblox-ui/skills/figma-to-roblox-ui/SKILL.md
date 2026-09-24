---
name: "figma-to-roblox-ui"
description: "Import Figma frames and designs into Roblox Studio GUI (ScreenGui/Frame/ImageLabel): Scale-only layout, centered AnchorPoint, UIStroke ScaledSize, UICorner in Scale, detailed art and custom shapes exported as images. Use for any Figma to Roblox UI transfer."
---

# Figma → Roblox GUI: high-fidelity import

Use this skill whenever a frame, screen, or component from Figma has to end up as GUI in Roblox Studio — built by hand in Luau, through the Roblox Studio MCP, or when checking the output of import plugins (FigBloxUI, RoImport, Bloxporter, Figma To Roblox).

## 0. HARD RULES (never break these)

1. **Scale everywhere, Offset = 0.** `Size`, `Position`, `UIListLayout.Padding`, `UIGridLayout.CellSize/CellPadding`, every `UIPadding` side, `UIShadow.Offset/BlurRadius/Spread` — Scale component only. Offset is always `0`.
2. **AnchorPoint = `Vector2.new(0.5, 0.5)` on every GuiObject by default**, so `Position` is the element's center. With a corner anchor like `(0, 0)`, UIAspectRatioConstraint, Size tweens and resolution changes shrink/grow the box toward that corner, so buttons and panels skew and drift away from their Figma spot. Use another anchor only when there is a concrete reason (section 4, "When not to center") and record it in the `AnchorReason` attribute so the validator accepts it.
3. **UIStroke always uses `StrokeSizingMode = Enum.StrokeSizingMode.ScaledSize`.** In this mode `Thickness` is a fraction of the *parent's shortest axis* (0.1 on a 200×300 frame = 20 px). Keep values between 0 and 1. `BorderOffset` is Scale too.
4. **UICorner always uses Scale.** `CornerRadius = UDim.new(radius / min(w, h), 0)`. Scale is measured against the shortest side; `0.5` = full pill/circle. For different corners use `TopLeftRadius / TopRightRadius / BottomLeftRadius / BottomRightRadius` (also Scale). Do not set `CornerRadius` and per-corner radii at the same time.
5. **Detailed art and non-standard shapes are exported from Figma as images and placed as ImageLabel/ImageButton** — never approximated with Frames (see section 2).
6. Text: `TextScaled = true` + `UITextSizeConstraint` (MaxTextSize ≈ Figma size × 1.5, MinTextSize ≈ 8). No fixed `TextSize`.
7. After every build, run the validator (section 8) and compare screenshots at several resolutions (section 9).

## 1. Prepare the Figma file (before export)

- The root frame is the reference screen. Use **1920×1080** (PC) or **1280×720**; check mobile at 844×390. Remember the root size — all Scale values derive from it.
- Anything that becomes a UI object must be a **Frame**, not a Group: groups have no bounds or clipping of their own, and plugins/math break on them.
- Auto Layout → becomes `UIListLayout` + `UIPadding`. Gap and padding are converted to Scale.
- Layer names = instance names in Roblox (Latin, no spaces: `ShopPanel`, `BuyButton`). Hint prefixes: `btn_` → ImageButton/TextButton, `scroll_` → ScrollingFrame, `img_` → ImageLabel (export as image).
- Fonts: pick ones available in Roblox (Font/FontFace: Gotham/Montserrat, Fredoka One, Luckiest Guy, Bangers, Source Sans, etc.). Otherwise that text must be rasterized.
- Before exporting, sort every layer into **native** or **image** using section 2.

## 2. Native vs image — the decision (how pros do it)

Professional Figma → Roblox workflow: **structure, layout and text are native; artwork is images.** Roblox can only draw rectangles and rounded rectangles with a flat fill, linear gradient, border and drop shadow. Everything beyond that is exported from Figma as PNG and dropped into Studio as ImageLabel/ImageButton.

### ALWAYS export as an image

- **Non-standard shapes** — anything that is not a rectangle / rounded rectangle / circle: stars, hexagons, shields, badges, ribbons, banners with cut ends, speech bubbles with tails, arrows, tabs with slanted edges, blobs, torn paper, irregular panels, custom vector paths, boolean-op shapes. UICorner and UIStroke only follow the rectangular box, so they can't reproduce these.
- **Highly detailed elements** — multi-layer buttons (glossy highlight + inner shadow + bevel + outline), panels with bevels, texture, stud/noise patterns, illustrations, character art, item/currency/rarity icons, logos, decorative frames and borders.
- **Effects Roblox can't render** — inner shadow, layer blur, background blur, blend modes, radial/angular/diamond gradients, image fills with masks, multiple stacked strokes, dashed strokes, strokes on custom shapes.
- **Stylized text** that uses a font Roblox doesn't have, or heavy effects (multiple outlines, gradient fill + 3D extrusion) — titles and logo text only; normal UI text stays TextLabel.

### Build natively

- Plain rectangles/rounded rectangles with a flat fill or linear gradient, a single border and a drop shadow → Frame + UICorner + UIGradient + UIStroke + UIShadow. Zero textures, perfectly crisp on any screen.
- All regular text (labels, prices, counters, descriptions) → TextLabel with a Roblox font. Crisp at every resolution, changeable from scripts, localizable.
- Containers, lists, grids, scroll areas → Frame / ScrollingFrame + layouts.

### Hybrid (the typical pro result)

A shop button is usually: `ImageButton` (exported artwork of the button body without text) → `TextLabel` child (price/text, native) → `ImageLabel` child (coin icon). The layout around it is native Frames in Scale.

### How pros export the images

- **Separate the art from the text.** Hide text layers before exporting the body; text is rebuilt as TextLabel.
- **Export each asset as its own layer/frame**, tightly cropped to the visible content, transparent background, PNG. Include the outline and outer glow/shadow *inside* the image if they are part of the art — then size the ImageLabel to the exported bounds, not the Figma shape size.
- **Resolution:** the longest side ≤ 1024 px (Roblox limit — anything bigger is downscaled and blurs). Usually @2x for elements ≤ 512 px in the mockup, exact 1024 for large ones.
- **Stretchable art → 9-slice.** Panels, bars, buttons with a custom shape but uniform edges: export a small version (e.g. 128×128 / 256×256), `ScaleType = Slice`, `SliceCenter = Rect(inset, inset, size−inset, size−inset)`, tune `SliceScale` so corners match the mockup. One texture stretches to any size without blur.
- **Color variants → one white/grey base + `ImageColor3`.** Rarity slots, team colors, button colors: export a neutral light version once and tint in Studio instead of uploading 6 copies.
- **Button states** (normal / hover / pressed / disabled): either separate images swapped from script, or one base image with `ImageColor3`/size tweens. Set `AutoButtonColor = false` when you handle states yourself.
- **Many small icons → spritesheet** 1024×1024, one upload, `ImageRectOffset` / `ImageRectSize` per ImageLabel. Saves memory and upload limits.
- **Artwork larger than 1024** (full-screen illustration) → cut into tiles ≤ 1024 (2×2, 3×2) and assemble with several ImageLabels in a Scale grid inside one Frame with UIAspectRatioConstraint. Tiles butt exactly edge to edge, `ResampleMode = Default`.
- Pixel art → `ResampleMode = Pixelated`.
- Every exported image still gets `UIAspectRatioConstraint` = exported width / height, so it never stretches.

## 3. Pull data from Figma

Through the Figma MCP (load any Figma skill the server requires first):
1. `get_metadata` on the root nodeId → tree, types, x/y/w/h, names.
2. `get_design_context` → fills, strokes (weight + align), radii, effects, fonts, auto layout.
3. `get_screenshot` of the root → reference for comparison.
4. `download_assets` for every layer marked as **image** in section 2.

Figma coordinates are absolute → convert them to coordinates **relative to the direct parent** before computing Scale.

## 4. px → Scale formulas

For an element (x, y, w, h) inside a parent (pw, ph), relative coordinates:

```
Size      = UDim2.fromScale(w / pw, h / ph)
Position  = UDim2.fromScale((x + w*ax) / pw, (y + h*ay) / ph)   -- ax,ay = AnchorPoint (default 0.5, 0.5)
Corner    = UDim.new(radius / min(w, h), 0)                       -- max 0.5
Stroke    = Thickness = strokeWeight / min(w, h)  (ScaledSize)
ListPad   = UDim.new(gap / pw, 0) (horizontal) | UDim.new(gap / ph, 0) (vertical)
UIPadding = Left/Right: p / pw ; Top/Bottom: p / ph
```

- **Default AnchorPoint = (0.5, 0.5)**, so `Position = UDim2.fromScale((x + w/2) / pw, (y + h/2) / ph)`, the center of the Figma box. The `place` helper does this unless you pass another anchor.
- A child's Position is always measured from the parent's top-left corner, whatever the parent's AnchorPoint, so the formulas stay the same at every level.
- If the parent has UIPadding, pw/ph = its *inner* area.
- Round Scale values to 4 decimals.

### When not to center

Change the anchor only when the element must stay glued to a side or grow from one side. Put the anchor on that side and set the `AnchorReason` attribute (the `place` helper does it for you):
- **HUD pinned to a screen edge or corner** (currency top-left, menu buttons on the left edge, hotbar at the bottom): anchor on that edge/corner, e.g. `(0, 0)`, `(0, 0.5)`, `(0.5, 1)`, `(1, 1)`. With a center anchor, UIAspectRatioConstraint pulls it away from the edge on narrow and wide screens.
- **Progress / health / XP bar fill** that grows through `Size.X`: `(0, 0.5)`, so it fills from the left.
- **Dropdowns, tooltips, lists with AutomaticSize** that must expand in one direction: anchor on the side that stays fixed (usually the top, `(0.5, 0)`).

Everything else (panels, buttons, icons, text, images, slots) stays `(0.5, 0.5)`.

### Keeping proportions
Scale on both axes stretches elements on wide/narrow screens, so:
- Every **root panel**, button, icon, avatar, slot and exported image gets `UIAspectRatioConstraint` with `AspectRatio = w/h` from Figma; pick `DominantAxis` by intent (usually Width for horizontal panels, Height for HUD on screen edges).
- Children inside such a panel are already Scale relative to it → proportions stay intact automatically.
- Round elements: AspectRatio = 1 + CornerRadius Scale 0.5.

## 5. Property mapping Figma → Roblox

| Figma | Roblox |
|---|---|
| Layer x/y | `AnchorPoint = (0.5, 0.5)`, `Position` = center of the layer box in Scale (section 4) |
| Rectangle frame with fill | `Frame` (BackgroundColor3, BackgroundTransparency = 1 − opacity) |
| Frame without fill | `Frame`, BackgroundTransparency = 1 |
| Non-standard shape / detailed art | `ImageLabel`/`ImageButton` with exported PNG (section 2), BackgroundTransparency = 1 |
| Raster image | `ImageLabel` (BackgroundTransparency = 1, ScaleType = Fit or Slice) |
| Text | `TextLabel` (TextScaled, UITextSizeConstraint, FontFace, TextXAlignment/TextYAlignment) |
| Button | `ImageButton`/`TextButton` (AutoButtonColor = false if it has its own hover) |
| Clip content | `ClipsDescendants = true` (does not clip to rounded corners — use `CanvasGroup` for that, but it is memory-heavy, use sparingly) |
| Stroke Inside / Center / Outside | `UIStroke.BorderStrokePosition = Inner / Center / Outer` |
| Stroke weight | `Thickness = weight / min(w,h)`, `StrokeSizingMode = ScaledSize` |
| Text outline | `UIStroke` with `ApplyStrokeMode = Contextual` inside the TextLabel, also ScaledSize |
| Corner radius | `UICorner` in Scale; different corners → per-corner *Radius properties |
| Drop shadow | `UIShadow`: Offset = UDim2.fromScale(dx/w, dy/h), BlurRadius/Spread = UDim.new(v/min(w,h), 0), Color, Transparency = 1 − alpha, ZIndex < 0. Compare blur against the screenshot — Figma and Roblox blur are not 1:1 |
| Inner shadow, blur, blend mode | export as image |
| Linear gradient | `UIGradient`: Color = ColorSequence, Transparency = NumberSequence (1 − alpha), Rotation = atan2(dy·h, dx·w) in degrees from gradientHandlePositions. Max 20 keypoints |
| Radial/angular gradient | export as image |
| Auto Layout | `UIListLayout` (FillDirection, Padding in Scale, SortOrder = LayoutOrder, alignment) + `UIPadding` in Scale; LayoutOrder = layer order |
| Grid | `UIGridLayout` (CellSize/CellPadding in Scale) + `UIAspectRatioConstraint` on the cell |
| Scroll | `ScrollingFrame` (CanvasSize = UDim2.fromScale(0,0), AutomaticCanvasSize = Y/X, thin ScrollBarThickness) |
| Group opacity | `CanvasGroup.GroupTransparency` (only when really needed — expensive) |
| Layer order | `ZIndex` by layer order (bottom layer = lowest ZIndex), ScreenGui.ZIndexBehavior = Sibling |

## 6. Uploading and performance

1. **Upload:** via the Roblox Studio MCP (`upload_image`/`store_image` if available), otherwise Asset Manager → Bulk Import, or the Open Cloud Assets API. Keep a table `layer name → rbxassetid://ID` to avoid duplicate uploads. Images go through moderation — until approved they render blank; that is not a layout bug.
2. **Performance:** fewer than 300 visible UIStrokes and fewer than 100 UIShadows at once (Roblox guidance for low-end devices). CanvasGroup only where group alpha or rounded clipping is required. Reuse images (tint with ImageColor3, spritesheets) to save texture memory.

## 7. Build order in Studio

1. `ScreenGui` in StarterGui: `ResetOnSpawn = false`, `ZIndexBehavior = Sibling`, `IgnoreGuiInset` as in the mockup (usually true for full-screen, false for HUD), `ScreenInsets = CoreUISafeInsets` for mobile.
2. Build the tree top-down in one Luau script (through `execute_luau` in the Roblox Studio MCP) using the helpers below, so Offset physically can't appear.
3. Containers + layouts first, then native visuals (Corner/Stroke/Gradient/Shadow), then images, then text on top.
4. Buttons: hover/press animations with TweenService on `Size` (Scale). With AnchorPoint (0.5, 0.5) the button grows and shrinks evenly around its center. Do **not** use `UIScale`: it mis-scales UIStrokes in ScaledSize mode (known bug, March 2026).

### Helpers (Luau)

```lua
local function S(x, y) return UDim2.fromScale(x, y) end
local function r4(n) return math.floor(n * 10000 + 0.5) / 10000 end
local CENTER = Vector2.new(0.5, 0.5)

-- Figma px -> Scale relative to the parent. Anchor is the center unless a
-- non-center anchor is passed together with the reason for it (section 4).
local function place(obj, x, y, w, h, pw, ph, anchor, reason)
	anchor = anchor or CENTER
	if anchor ~= CENTER then
		assert(reason, obj.Name .. ": non-center AnchorPoint needs a reason")
		obj:SetAttribute("AnchorReason", reason)
	end
	obj.AnchorPoint = anchor
	obj.Size = S(r4(w / pw), r4(h / ph))
	obj.Position = S(r4((x + w * anchor.X) / pw), r4((y + h * anchor.Y) / ph))
end

local function corner(obj, radiusPx, w, h)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(math.min(0.5, r4(radiusPx / math.min(w, h))), 0)
	c.Parent = obj
	return c
end

local POS = { INSIDE = Enum.BorderStrokePosition.Inner, CENTER = Enum.BorderStrokePosition.Center, OUTSIDE = Enum.BorderStrokePosition.Outer }
local function stroke(obj, weightPx, w, h, color, align, contextual)
	local s = Instance.new("UIStroke")
	s.StrokeSizingMode = Enum.StrokeSizingMode.ScaledSize
	s.Thickness = r4(weightPx / math.min(w, h))
	s.Color = color
	s.ApplyStrokeMode = contextual and Enum.ApplyStrokeMode.Contextual or Enum.ApplyStrokeMode.Border
	if not contextual then s.BorderStrokePosition = POS[align or "INSIDE"] end
	s.Parent = obj
	return s
end

local function aspect(obj, w, h, axis)
	local a = Instance.new("UIAspectRatioConstraint")
	a.AspectRatio = w / h
	a.DominantAxis = axis or Enum.DominantAxis.Width
	a.Parent = obj
end

local function text(obj, figmaSize)
	obj.TextScaled = true
	local c = Instance.new("UITextSizeConstraint")
	c.MaxTextSize = math.floor(figmaSize * 1.5)
	c.MinTextSize = 8
	c.Parent = obj
end

-- exported artwork (non-standard shape / detailed element)
local function image(parent, name, assetId, x, y, w, h, pw, ph, slice, anchor, anchorReason)
	local i = Instance.new("ImageLabel")
	i.Name = name
	i.BackgroundTransparency = 1
	i.Image = assetId
	place(i, x, y, w, h, pw, ph, anchor, anchorReason)
	if slice then
		i.ScaleType = Enum.ScaleType.Slice
		i.SliceCenter = slice.center
		i.SliceScale = slice.scale or 1
	else
		i.ScaleType = Enum.ScaleType.Fit
		aspect(i, w, h)
	end
	i.Parent = parent
	return i
end
```

For text outlines (Contextual), `min(w,h)` is the TextLabel's own size; tune against the screenshot, usually 0.04–0.08.

## 8. Validator (run after EVERY build)

```lua
local root = game.StarterGui:FindFirstChild("SCREEN_GUI_NAME")
local bad = {}
local function udim(v) return typeof(v) == "UDim" and v.Offset ~= 0 end
local function udim2(v) return typeof(v) == "UDim2" and (v.X.Offset ~= 0 or v.Y.Offset ~= 0) end
for _, d in root:GetDescendants() do
	local p = d:GetFullName()
	if d:IsA("GuiObject") then
		if udim2(d.Size) then table.insert(bad, p .. " Size offset") end
		if udim2(d.Position) then table.insert(bad, p .. " Position offset") end
		if d.AnchorPoint ~= Vector2.new(0.5, 0.5) and not d:GetAttribute("AnchorReason") then table.insert(bad, p .. " AnchorPoint not center (set AnchorReason if intentional)") end
		if (d:IsA("TextLabel") or d:IsA("TextButton") or d:IsA("TextBox")) and not d.TextScaled then table.insert(bad, p .. " TextScaled=false") end
		if (d:IsA("ImageLabel") or d:IsA("ImageButton")) and d.Image == "" then table.insert(bad, p .. " empty Image") end
	elseif d:IsA("UIStroke") then
		if d.StrokeSizingMode ~= Enum.StrokeSizingMode.ScaledSize then table.insert(bad, p .. " Stroke not ScaledSize") end
		if d.Thickness > 1 then table.insert(bad, p .. " Stroke Thickness>1 (looks like px)") end
		if udim(d.BorderOffset) then table.insert(bad, p .. " BorderOffset offset") end
	elseif d:IsA("UICorner") then
		for _, k in {"CornerRadius","TopLeftRadius","TopRightRadius","BottomLeftRadius","BottomRightRadius"} do
			local ok, v = pcall(function() return d[k] end)
			if ok and udim(v) then table.insert(bad, p .. " " .. k .. " offset") end
		end
	elseif d:IsA("UIListLayout") then
		if udim(d.Padding) then table.insert(bad, p .. " Padding offset") end
	elseif d:IsA("UIGridLayout") then
		if udim2(d.CellSize) or udim2(d.CellPadding) then table.insert(bad, p .. " Grid offset") end
	elseif d:IsA("UIPadding") then
		for _, k in {"PaddingLeft","PaddingRight","PaddingTop","PaddingBottom"} do
			if udim(d[k]) then table.insert(bad, p .. " " .. k .. " offset") end
		end
	elseif d:IsA("UIShadow") then
		if udim2(d.Offset) or udim(d.BlurRadius) or udim(d.Spread) then table.insert(bad, p .. " Shadow offset") end
	end
end
print(#bad == 0 and "OK: everything is Scale and centered" or table.concat(bad, "\n"))
```

If the output is not `OK`, fix and rerun until it is clean.

## 9. Visual check

1. Studio screenshot (`screen_capture`) vs Figma `get_screenshot`: spacing, stroke thickness, radii, colors, fonts, image sharpness.
2. Device Emulator: 1920×1080, 1366×768, phone (844×390 landscape), tablet (1024×768). Nothing may go off-screen or overlap; strokes must not become hairline or chunky.
3. Blurry images: if an ImageLabel is shown larger than its source, re-export bigger (≤ 1024) or switch to 9-slice.

## 10. Common mistakes

- **Buttons skew or drift when resized, on other screens or during hover tweens** → AnchorPoint left at `(0, 0)`. Use `(0.5, 0.5)`; other anchors only for edge-pinned HUD, fill bars and one-way expanding elements (section 4).
- **Elements drift apart on other screens** → missing UIAspectRatioConstraint on root panels, or coordinates computed from the root instead of the direct parent.
- **Custom shape rebuilt from Frames looks cheap/wrong** → it should have been an exported image (section 2).
- **Stroke thickness differs on same-style buttons** → in ScaledSize thickness depends on min(w,h); compute Thickness per size with the formula, don't copy the number.
- **Rounded corners missing on an image** → UICorner must be inside the ImageLabel itself; ClipsDescendants doesn't clip to rounded corners. For non-rectangular art, bake the shape into the PNG.
- **Jagged shadow** → large CornerRadius + UIShadow causes jaggies (known limitation); reduce BlurRadius or bake the shadow into the image.
- **Text size differs between neighboring buttons** → TextScaled fits the box; equalize TextLabel heights and MaxTextSize.
- **Blurry art** → image > 1024 or stretched beyond its source; see section 2.
- **Text baked into images** → blurry, can't be changed from scripts or localized; keep it as TextLabel unless it is a stylized title.
- **Plugins (FigBloxUI, RoImport, Bloxporter, Figma To Roblox)** save time, but ALWAYS run their output through the validator: they can leave Offset, `(0, 0)` anchors, FixedSize strokes and px radii. Figma components/variants don't carry over — they become plain instances.