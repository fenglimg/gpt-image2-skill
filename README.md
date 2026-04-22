# gpt-2-image-skill

A Claude Skill + CLI for **OpenAI GPT Image 2** (`gpt-image-2`), with a curated prompt gallery for the hard stuff: dense Chinese typography, photorealism, posters, infographics, character sheets, and image editing.

Drop it into any skill-aware agent runtime (Claude Code, Hermes, etc.) or just call the script directly from the shell.


## What you get

```
gpt-2-image-skill/
├── SKILL.md                  # Claude Skill spec: triggers, CLI reference, examples
├── scripts/
│   └── generate.py           # Self-contained PEP 723 uv script, no venv needed
└── references/
    ├── craft.md              # 12 prompt-craft principles for GPT Image 2
    └── gallery.md            # 56 community-curated prompt patterns, 8 categories
```

- **`SKILL.md`** — Frontmatter + CLI table. Claude loads this automatically when image-generation intent is detected; other agents can read it as Markdown.
- **`scripts/generate.py`** — One Python file. Every documented API parameter exposed as a flag. Uses raw `httpx` (no SDK pinning), so new API params keep working.
- **`references/`** — Optional deep material. Loaded on demand when the request signals a matching category.

## Install

### Option A: User-scope Claude Skill

```bash
git clone https://github.com/<your-handle>/gpt-2-image-skill ~/.claude/skills/gpt-image
```

Claude Code auto-discovers `~/.claude/skills/*/SKILL.md`. Restart the session and Claude will surface the skill on any image-gen intent.

### Option B: Standalone CLI

```bash
git clone https://github.com/<your-handle>/gpt-2-image-skill ~/tools/gpt-2-image-skill
export OPENAI_API_KEY=sk-...
uv run ~/tools/gpt-2-image-skill/scripts/generate.py -p "a cat astronaut"
```

The PEP 723 header pulls `httpx` + `python-dotenv` automatically on first run; no separate venv or `pip install` needed. Requires [`uv`](https://github.com/astral-sh/uv) and Python ≥ 3.11.

## Showcase

All images below were produced one-shot at `--quality high`. Every prompt is in [`references/gallery.md`](references/gallery.md).

### Editorial & commercial

<table>
<tr>
<td width="50%" valign="top">
<img src="docs/example-tea-poster.png" alt="Chinese tea-launch poster" />
<br><em>Chinese tea-launch poster</em>
</td>
<td width="50%" valign="top">
<img src="docs/example-propaganda-poster.png" alt="1980s propaganda poster" />
<br><em>1980s propaganda poster</em>
</td>
</tr>
<tr>
<td valign="top">
<img src="docs/example-museum-infographic.png" alt="Museum-catalog infographic" />
<br><em>Museum-catalog infographic (唐代襦裙)</em>
</td>
<td valign="top">
<img src="docs/example-photoreal-subway.png" alt="RAW iPhone photorealism" />
<br><em>RAW iPhone photorealism</em>
</td>
</tr>
<tr>
<td colspan="2" valign="top">
<img src="docs/example-character-sheet.png" alt="Character reference sheet" />
<br><em>Character reference sheet — three-view, expression grid, equipment, world notes</em>
</td>
</tr>
</table>

### Research paper figures

<table>
<tr>
<td width="50%" valign="top">
<img src="docs/example-transformer-arch.png" alt="Transformer architecture" />
<br><em>Transformer encoder–decoder (Vaswani et al., 2017)</em>
</td>
<td width="50%" valign="top">
<img src="docs/example-rag-pipeline.png" alt="RAG pipeline" />
<br><em>Retrieval-Augmented Generation pipeline (Lewis et al., 2020)</em>
</td>
</tr>
<tr>
<td valign="top">
<img src="docs/example-agent-architecture.png" alt="Multi-agent LLM system" />
<br><em>Multi-agent LLM system (AutoGen / LangGraph / Managed Agents)</em>
</td>
<td valign="top">
<img src="docs/example-diffusion-chain.png" alt="Diffusion chain" />
<br><em>Denoising diffusion forward / reverse chain (Ho et al., 2020)</em>
</td>
</tr>
<tr>
<td valign="top">
<img src="docs/example-scaling-curves.png" alt="Scaling laws plot" />
<br><em>Empirical scaling laws (Kaplan 2020, Chinchilla 2022)</em>
</td>
<td valign="top">
<img src="docs/example-benchmark-heatmap.png" alt="Benchmark heatmap" />
<br><em>Benchmark comparison heatmap</em>
</td>
</tr>
<tr>
<td valign="top">
<img src="docs/example-ablation-bars.png" alt="Ablation bar chart" />
<br><em>Ablation bar chart with error bars</em>
</td>
<td valign="top">
<img src="docs/example-data-sankey.png" alt="Pretraining data mixture sankey" />
<br><em>LLM pretraining data-mixture sankey</em>
</td>
</tr>
<tr>
<td valign="top">
<img src="docs/example-algorithm-box.png" alt="Algorithm pseudocode block" />
<br><em>Algorithm pseudocode block (Self-Refine, Madaan et al., 2023)</em>
</td>
<td valign="top">
<img src="docs/example-attention-heatmap.png" alt="Attention weight heatmaps" />
<br><em>Multi-head attention heatmaps (Clark et al., 2019)</em>
</td>
</tr>
<tr>
<td valign="top">
<img src="docs/example-model-timeline.png" alt="LLM family tree timeline" />
<br><em>Frontier LLM family tree, 2018–2026</em>
</td>
<td valign="top">
<img src="docs/example-react-trace.png" alt="ReAct reasoning trace" />
<br><em>ReAct reasoning trace (Yao et al., 2022)</em>
</td>
</tr>
<tr>
<td colspan="2" valign="top">
<img src="docs/example-prompt-injection-flow.png" alt="Indirect prompt injection attack flow" />
<br><em>Indirect prompt-injection attack flow (Greshake et al., 2023)</em>
</td>
</tr>
</table>

## Quick reference

### Primary path — conversational (Claude Code, Codex, Cline, etc.)

Once the skill is installed, you have two equivalent ways to trigger it:

**(a) Slash command** — explicit, short:

```
/gpt-image a photorealistic convenience store at 10pm, 1024x1024

/gpt-image Design a 3:4 Chinese tea-launch poster. Exact copy:
"山川茶事" / "冷泡系列" / "中杯 16 元" / "大杯 19 元".
Dark green / off-white / gold, rice-paper texture.

/gpt-image colorize ./fig/manga-page.jpg and translate text to Chinese

/gpt-image combine fig/cat.png and fig/kfc_logo.png into a collab poster
```

Everything after `/gpt-image` is the prompt. Agents parse paths out of the prompt — any `.png` / `.jpg` it sees becomes an `-i` reference image for the edit endpoint.

**(b) Natural language** — skill auto-loads on image-gen intent, no slash needed:

```
you:   Generate a photorealistic convenience-store-at-night photo, 1K square.
agent: [loads gpt-image skill, runs scripts/generate.py, returns PNG path]

you:   Colorize ./fig/manga-page.jpg and translate the text to Chinese.
agent: [detects reference image → edits endpoint,
        calls generate.py -i fig/manga-page.jpg]
```

Tips for either form:
- Put **exact displayed text in quotes** — the agent will preserve it verbatim through to the API call.
- Mention **aspect / size** upfront (`3:4`, `2K`, `landscape`) — the agent maps this to the right `--size` flag.
- Mention a **reference image path** to trigger the edit endpoint; mention a **mask** to trigger inpainting.
- If you want the agent to iterate cheaply while you workshop the prompt, say "use quality low first" — the skill default is `high`.

### Secondary path — direct CLI

For scripting, CI, or batch jobs you can call the script yourself:

```bash
# vanilla generate, auto filename, 1K square, high quality (default)
uv run generate.py -p "a photorealistic convenience store at 10pm"

# 3:4 portrait poster with exact Chinese copy
uv run generate.py \
  -p 'Design a 3:4 tea poster. Exact copy: "山川茶事" / "冷泡系列" / "中杯 16 元"' \
  --size portrait -f poster.png

# edit / colorize existing image
uv run generate.py -p "colorize and translate to Chinese" -i page.jpg -f out.png

# multi-reference brand collab
uv run generate.py -p "cat × KFC poster" -i cat.png -i kfc_logo.png -f collab.png

# masked inpaint
uv run generate.py -p "replace sky with aurora" -i photo.jpg -m sky_mask.png -f out.png

# 4K widescreen, cheap preview
uv run generate.py -p "Shanghai skyline" --size 4k --quality low -f draft.png
```

Full flag table and size shortcuts live in [`SKILL.md`](SKILL.md).

## API-key resolution

The script reads `OPENAI_API_KEY` in this order, with later entries winning:

1. process env (`export OPENAI_API_KEY=...`)
2. `./.env` in cwd
3. `~/.env` in home (override-on, so this is the source of truth when present)

Put the key wherever fits your workflow — dotenv users don't need to re-export on every shell.

## Design notes

- **Defaults bias quality.** `--quality high` is default because GPT Image 2's typography and fine-detail rendering degrade noticeably below it. Use `--quality low` for quick iteration.
- **Raw HTTP, no SDK.** The script uses `httpx` directly, so every parameter the API documents (including newer ones like `background`, `moderation`, `output_format`, `partial_images`) is forwarded verbatim. No waiting for SDK releases.
- **Endpoint auto-selected.** Pass `-i` once or more to switch from `/v1/images/generations` to `/v1/images/edits` (multipart form). Add `-m` for alpha-channel inpainting.
- **Progressive disclosure.** `SKILL.md` is ~120 lines (fits in an agent's context). Load `references/gallery.md` only when the request matches a category.

## Attribution

Prompt patterns curated from [`ZeroLu/awesome-gpt-image`](https://github.com/ZeroLu/awesome-gpt-image) under CC BY 4.0. Every entry in `references/gallery.md` preserves its original `Source: @handle` tag. The skill's `SKILL.md`, `craft.md`, and `generate.py` are released under CC BY 4.0 as well — keep the attribution intact when you fork, vendor, or publish derivatives.

## License

CC BY 4.0 — see [`LICENSE`](LICENSE).
