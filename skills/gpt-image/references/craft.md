# GPT Image 2 Prompt Craft

Cross-cutting principles distilled from the full 151-prompt Gallery Atlas. Use this file as the prompt-design checklist; use `gallery.md` as the concrete Scale/case atlas.

## 0. Use the Scale before writing from scratch

Before drafting a prompt, identify the closest `gallery.md` category and read 3–8 nearby cases. The skill should not behave like a bare CLI wrapper: it should remix the repo's collected patterns.

Fast routing examples:
- Anime/manga or multi-character boards → No. 1–12.
- Product/food commercial render, especially structured config prompts → No. 55–58.
- Brand, poster, typography, dense Chinese copy → No. 32–44, 59–61, 66–73.
- Research, data, technical, scientific figures → No. 74–90, 102–121.
- UI / app / dashboard mockups → No. 97–101.
- Edit endpoint / reference transformations → No. 95–96.

## 1. Exact text goes in quotes

GPT Image 2 renders typography well when literal copy is explicit.

Weak:
> Create a tea poster with the brand name and promo copy.

Strong:
> Design a 3:4 vertical poster. The poster must accurately display the following exact Chinese copy: "山川茶事" / "冷泡系列" / "中杯 16 元" / "大杯 19 元".

Rules:
- Wrap every displayed string in `"…"`.
- Keep user-supplied Chinese verbatim; do not paraphrase.
- Separate text blocks with `/`, bullets, or layout labels.
- For dense text, include title, subtitle, module labels, legend labels, numbers, fine print, and any required axes/tabs.
- If text is only decorative, say so. If it must be readable, say `crisp`, `legible`, `large enough`, and `no garbled characters`.

## 2. Put canvas, aspect ratio, and layout before subject

The strongest gallery prompts allocate space before describing surface detail.

Useful first clauses:
- `Landscape 16:9 academic concept figure…` (No. 74–90).
- `Design a 3:4 vertical poster…` (No. 32, No. 146).
- `Create a square 3×3 grid…` (No. 21, No. 24).
- `A 6-panel film storyboard laid out as a 3×2 grid…` (No. 27).
- `Create one tall manga chapter proof sheet containing 19 numbered miniature pages…` (No. 10).

When structure matters, state the structure before the subject. Otherwise the model spends detail budget on the object and improvises the layout.

## 3. JSON / config-style prompts are a core pattern

Do not omit this. The gallery uses JSON-like structured prompts for premium product and food rendering (No. 56, No. 57). This pattern works when the output has many interacting systems: environment, subject, materials, lighting, particles, motion, and render goals.

When to use:
- Product hero renders with material/lighting precision.
- Food photography with suspended ingredients or motion.
- Complex scenes where you want a controllable schema rather than prose.
- Any prompt that benefits from reusable slots.

Recommended schema:

```text
/* PRODUCT_RENDER_CONFIG: Short Name
   AESTHETIC: Premium Commercial Photography */
{
  "GLOBAL_SETTINGS": {
    "aspect_ratio": "2:3 vertical",
    "style": "hyper-realistic commercial photography",
    "clarity": "sharp foreground, micro-texture visibility"
  },
  "ENVIRONMENT": {
    "background": "warm gradient studio backdrop",
    "lighting": "directional softbox with glossy highlights",
    "atmosphere": ["floating particles", "cinematic bokeh"]
  },
  "CORE_ASSETS": {
    "primary_subject": "hero product",
    "materials": ["brushed metal", "condensation", "paper label"],
    "composition": "diagonal zero-gravity arrangement"
  },
  "MOTION_OR_DETAIL_SYSTEMS": [
    { "object": "ingredient fragments", "state": "suspended mid-air" },
    { "object": "liquid splash", "behavior": "thick glossy arc" }
  ],
  "OUTPUT": {
    "mood": "premium, indulgent, editorial",
    "avoid": ["cheap e-commerce banner", "plastic CGI", "fake brand logos"]
  }
}
```

Craft rules:
- Keys should describe visual subsystems, not implementation internals.
- Values should be concrete visual constraints, not vague praise.
- Arrays are good for visible elements; nested objects are good for materials, physics, lighting, and output goals.
- JSON does not have to be machine-valid if comments help the model, but keep it clean and readable.
- Still include aspect ratio and output mood inside the schema.

## 4. Use fixed-region schemas for infographics and educational boards

Several high-performing prompts are not just descriptions; they are layout contracts. See the museum catalog disassembly infographic (No. 67), field guides (No. 68, No. 73), travel/cooking cards (No. 69, No. 71), and anatomy/science posters (No. 117–121).

Pattern:
1. Name the artifact type: `museum catalog-style Chinese disassembly infographic`, `field guide`, `classroom wall chart`.
2. Define the fixed layout zones: top title, left disassembly, right summary, bottom legend, etc.
3. Specify annotation behavior: lead lines, numbered labels, close-up details, material notes.
4. Specify style boundary: museum board, scientific poster, editorial card — not generic poster / anime / e-commerce.
5. Add exact label text where correctness matters.

This is stronger than saying “make an infographic about X”.

## 5. Research/data figures need diagram grammar

For academic and technical figures, use the language of diagrams, not illustration only.

Include:
- Orientation and venue style: `Landscape 16:9`, `NeurIPS camera-ready`, `conference-paper figure`.
- Structural primitives: columns, zones, stacks, panels, nodes, ribbons, heatmaps, bars, dashed dividers.
- Directed relationships: arrows, residual arcs, feedback loops, dashed attack paths, numbered flow markers.
- Exact labels: module names, axes, legend values, titles, subtitles.
- Visual semantics: color meanings, line styles, thickness ∝ quantity, benign vs attack flows.
- Cleanliness constraints: `large readable labels`, `white background`, `uncluttered`, `publication-grade`.

Examples:
- No. 74 uses left/right encoder-decoder columns with exact block labels.
- No. 76 uses zones, worker nodes, tool registry, memory panels, and trace timeline.
- No. 81 uses Sankey source blocks, processing blocks, final splits, and proportional ribbons.
- No. 90 uses four columns plus benign/injection arrow semantics.

## 6. UI prompts should read like product specs

The UI/UX examples (No. 97–101) succeed because they specify product context, device frame, information architecture, real copy, and data.

Pattern:
- Fictional product name to avoid real-brand leakage.
- Device/canvas: `1290x2796 smartphone screen`, `16:10 monitor canvas`.
- Palette and component system.
- Header, cards, charts, nav, transaction/activity rows.
- Exact values and labels: balances, percentages, axis labels, button names.
- Quality constraints: `crisp typography`, `clean spacing`, `precise icon alignment`, `production-quality mockup`.

Avoid generic UI words alone (`modern`, `clean`, `beautiful`). Add rows, labels, charts, and plausible product data.

## 7. Multi-panel boards need consistency constraints

For grids, proof sheets, storyboards, character sheets, and worldbuilding boards, the key is not “many images”; it is coherence across panels.

Examples:
- No. 5: 16-panel expression grid.
- No. 9: ten-panel character grid.
- No. 10: 19-page manga proof sheet.
- No. 21: 3×3 dark-fantasy worldbuilding set.
- No. 27: 6-panel storyboard with shot/camera metadata.
- No. 30: official character reference sheet.

Rules:
- State the grid/page count exactly.
- Give each panel a role or beat.
- Specify shared art direction, palette, costume motifs, symbols, lighting, and character identity.
- For storyboards, add camera language: WIDE, OTS, CU, low angle, aerial, match cut, pan/tilt/static, duration.
- For character sheets, require front/side/back views, expression variations, parts breakdown, palette, and setting notes.

## 8. Camera and capture context unlock photorealism

The strongest photorealistic prompts name how the image was captured, not just that it is realistic.

Useful phrases:

| Phrase | Effect |
|---|---|
| `RAW, unprocessed, full iPhone camera quality` | Reduces AI polish; adds casual realism. |
| `amateur iPhone photo` | Tourist / spectator feel. |
| `shot from the crowd at a distance` | Real-event perspective. |
| `eye level with a 28 mm lens feel` | Architectural realism. |
| `low three-quarter angle` | Product/vehicle hero composition. |
| `natural morning side light` | Beauty/lifestyle softness. |

Pick one dominant capture frame. Too many camera specs can conflict.

## 9. Scene density beats adjectives

Vague: `a convenience store at night`.

Strong: name concrete objects, surfaces, and situational details: freezer stickers, promotional posters, trash cans, entrance mats, glass reflections, shared bikes, water droplets, phone glow, wet asphalt.

Rule of thumb: include 5–12 concrete nouns for the scene and 2–4 material/lighting constraints. Do not stack empty adjectives like `stunning`, `professional`, `beautiful`, `high quality` without visual anchors.

## 10. Style anchors should be specific and bounded

Name an aesthetic, medium, movement, or production context:
- `MAPPA-style digital 2D animation`, `Studio Pierrot Naruto-Shippuden aesthetic`.
- `New Chinese visual style, light-luxury and restrained`.
- `Swiss grid discipline meets friendly risograph community poster`.
- `gongbi-level architectural detail combined with loose ink atmosphere`.
- `traditional Japanese irezumi tattoo aesthetics`.
- `NeurIPS camera-ready style`.

If using a living studio/IP aesthetic, keep characters original and avoid direct copying where the output is meant for publication.

## 11. Promotional hierarchy for commercial posters

Posters, ads, menus, and campaign visuals should specify hierarchy.

Include:
- Product/event name largest.
- Claim/tagline.
- SKU / variants / modules.
- Prices or dates if relevant.
- CTA or ordering/info module.
- Fine print.
- Distance readability: `legible from a distance`, `clear promotional hierarchy`.

This prevents flat banner layouts where every text block has the same weight.

## 12. Material, lighting, and palette are separate controls

Do not compress them into “premium”. Split them:
- Materials: brushed steel, brass, ruby jewel accents, travertine, linen, glass thickness, condensation, rice paper.
- Lighting: softbox, rim light, natural morning side light, neon reflections, warm-copper highlights, cold blue-grey evening.
- Palette: muted teal/rust/bone, cream/warm stone/pale green, slate/amber/teal, indigo/red-orange/cream.

This is especially important for product renders, interiors, architecture, tattoo flash, beauty lifestyle, and technical exploded views.

## 13. Edit endpoint prompts must preserve invariants

For `images.edit`, be surgical. State what changes and what must remain unchanged.

Pattern:
> Make it a winter evening with heavy snowfall, snow dusted on the board and pieces, breath vapor in the air, cold blue-grey lighting, chess position still clearly readable.

Rules:
- Name the target transformation first.
- Preserve identity/layout/position/readability explicitly.
- If editing a poster/mockup, preserve original text unless translation/replacement is requested.
- Use `-i` reference images; use masks for localized changes.

## 14. Negation is for strong priors

Use explicit avoid-lines when the model has a likely bad default.

Examples:
- `Avoid anime style, avoid modern cyberpunk, avoid random fake kanji clutter.`
- `Avoid motorcycle aggression, sci-fi excess, fake brand logos, and toy-like proportions.`
- `Avoid generic festival chaos, fake sponsor logos, and unreadable microtext.`
- `No gore, no body horror, no actual person, no photorealistic skin photo.`

Avoid lists should be short and targeted. Too many negatives can dominate the prompt.

## 15. Category-specific mini-schemas

Reusable category formulas from the atlas:

- **Anime/Manga:** style anchor + original characters + action/pose + environment + palette + line/cel-shading direction + safety/IP boundary.
- **Gaming:** game-camera context + HUD elements + playable scene detail + screenshot/monitor realism.
- **Cyberpunk/Retro:** board/grid format + named subcharacters/items + neon material vocabulary + original designs.
- **Brand systems:** logo/wordmark + color palette + type system + packaging/social/touchpoints in one showcase board.
- **Photography:** capture device + time/place + ordinary imperfections + real-world props.
- **Architecture/Interior:** room type + camera/lens + materials + light direction + negative space + realistic shadows.
- **Technical illustration:** exploded/cutaway structure + ordered components + numbered callouts + materials + blueprint/plate style.
- **Tattoo:** tattooable placement + linework/shading/color tradition + negative-space gaps + flash-sheet presentation + no real skin photo.

## 16. Dense Chinese and multilingual layouts need extra constraints

For Chinese-heavy outputs:
- Say `Simplified Chinese` or `Traditional Chinese` if it matters.
- Provide all copy exactly.
- Specify layout modules and hierarchy.
- Require readable, neat text without garbled characters, typos, English, or pinyin unless desired.
- Use high quality for final assets.

Chinese calligraphy or brush-signage prompts should specify style (`brush style`, `calligraphy-style labels`, `rice-paper texture`) and avoid fake clutter.

## 17. Attribution and gallery metadata

Every `gallery.md` entry preserves either `Original` metadata or visible `Author + Source` attribution when it came from an outside source. When adapting an outside-source pattern into README/gallery entries, keep attribution in the metadata/footer.

Use `Original` only for repo-created prompts/images.

## 18. Safety and copyright notes

- Real-person likeness edits often fail at the API moderation layer; surface the API error verbatim.
- Keep adult/fashion prompts clearly adult, tasteful, non-explicit, and non-nude.
- Brand/IP aesthetics appear in the gallery; use original characters/products when creating reusable or public examples.
- For research/security figures, preserve benign framing and avoid operational instructions beyond defensive illustration.
