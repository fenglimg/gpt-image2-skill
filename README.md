# gpt-2-image-skill

A portable **Agent Skill + CLI** for OpenAI **GPT Image 2** (`gpt-image-2`). Works with Claude Code, Codex CLI, OpenCode, Cursor Agent, Aider, and plain shell — anywhere you can run `uv`.

Comes with a curated prompt gallery for the hard stuff: dense Chinese typography, photorealism, posters, infographics, character sheets, research-paper figures, image editing.


---

## 1. Skill Quick Start

Once installed, invoke the skill with the same slash command in any SKILL.md-aware agent:

```
/gpt-image a photorealistic convenience store at 10pm, 1024x1024

/gpt-image Design a 3:4 tea poster with exact Chinese copy
"山川茶事" / "冷泡系列" / "中杯 16 元" / "大杯 19 元"

/gpt-image colorize ./fig/manga-page.jpg and translate the text to Chinese

/gpt-image combine fig/cat.png and fig/kfc_logo.png into a collab poster
```

Compatible with:

- **Claude Code**
- **Codex**
- **OpenCode**
- Any SKILL.md-aware runtime

### Tips

- Put displayed text in **quotes** — agents preserve it verbatim.
- State **aspect / size** upfront (`3:4`, `2K`, `landscape`, `portrait`, `4K`).
- Name a **reference image path** to flip to edit mode; add a **mask** for inpainting.
- Default `--quality` is `high` — say "use quality low" for cheap iteration.

---

## 2. Install

### Option A — Skill-aware agent (auto-discovery)

```bash
git clone https://github.com/wuyoscar/gpt_image_2_skill ~/.claude/skills/gpt-image
export OPENAI_API_KEY=sk-...
```

Restart the agent and it will surface the skill on any image-gen intent.

| Runtime | Install path |
|---|---|
| Claude Code | `~/.claude/skills/<name>/SKILL.md` |
| Claude.ai Skills | upload `.zip` of this repo via the UI |
| OpenCode / Hermes | check the project docs for their skills dir |

### Option B — Standalone CLI anywhere

```bash
git clone https://github.com/wuyoscar/gpt_image_2_skill ~/tools/gpt-image
export OPENAI_API_KEY=sk-...
uv run ~/tools/gpt-image/scripts/generate.py -p "a cat astronaut"
```

Requires `uv` and Python ≥ 3.11. Dependencies (`httpx`, `python-dotenv`) auto-install on first run via PEP 723 inline metadata — no pip install, no venv.

---

## 3. Showcase

All images produced one-shot at `--quality high`. Every prompt + its source is in [`references/gallery.md`](references/gallery.md); captions below name the origin so you can trace it.

### Editorial posters & typography (portrait)

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-tea-poster.png" alt="Chinese tea-launch poster" /><br><em>Chinese tea-launch poster · community (<a href="https://mp.weixin.qq.com/s/ASxig6mFVYxrIE8-8Fthew">卡尔的AI沃茨</a>)</em></td>
<td width="50%" valign="top"><img src="docs/example-propaganda-poster.png" alt="1980s propaganda poster" /><br><em>1980s propaganda poster · community (<a href="https://x.com/akokoi1/status/2046558658096738672">@akokoi1</a>) + adapted</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-museum-infographic.png" alt="Museum-catalog infographic (唐代襦裙)" /><br><em>Museum-catalog infographic (唐代襦裙) · community (<a href="https://x.com/MrLarus/status/2045504669401653414">@MrLarus</a>)</em></td>
<td valign="top"><img src="docs/example-song-dynasty-feed.png" alt="Song Dynasty social-media feed (宋朝朋友圈)" /><br><em>Song Dynasty social-media feed (宋朝朋友圈) · community (<a href="https://x.com/Panda20230902/status/2045385588065313057">@Panda20230902</a>)</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-saul-bass-poster.png" alt="Saul-Bass-style thriller poster — THE LAST HEIR" /><br><em>Saul-Bass-style thriller poster · original (Bass lineage)</em></td>
<td valign="top"><img src="docs/example-manga-relationship.png" alt="A Tale of Two Cities manga relationship map" /><br><em>Manga relationship map — <em>A Tale of Two Cities</em> · community (<a href="https://x.com/cht0001/status/2046920121239908380">@cht0001</a>)</em></td>
</tr>
</table>

### Product, food & knowledge cards (portrait)

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-encyclopedia-panda.png" alt="Giant Panda field-guide infographic" /><br><em>Encyclopedia field guide (Giant Panda) · community (<a href="https://x.com/MrLarus/status/2046231542817497392">@MrLarus</a>)</em></td>
<td width="50%" valign="top"><img src="docs/example-product-chocolate-wafer.png" alt="Chocolate wafer JSON-style product render" /><br><em>Chocolate wafer product render (JSON-style) · community (<a href="https://x.com/mehvishs25/status/2020693181730598932">@mehvishs25</a>)</em></td>
</tr>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-food-salad-explosion.png" alt="Salad explosion food photography" width="55%" /><br><em>Salad-explosion food photography (JSON-style) · community (<a href="https://x.com/ChillaiKalan__">@ChillaiKalan__</a>)</em></td>
</tr>
</table>

### Games & photorealism (landscape)

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-hitman-openai.png" alt="Hitman-style gameplay at OpenAI HQ" /><br><em>Hitman-style gameplay (OpenAI HQ) · community (<a href="https://x.com/flowersslop/status/2044734896321532390">@flowersslop</a>)</em></td>
<td width="50%" valign="top"><img src="docs/example-gta6-beach.png" alt="GTA 6 Vice City beach gameplay" /><br><em>GTA 6 gameplay — Vice City beach · community (<a href="https://x.com/WolfRiccardo/status/2041187268711321735">@WolfRiccardo</a>)</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-photoreal-subway.png" alt="RAW iPhone subway photorealism" /><br><em>RAW iPhone — 42nd Street subway · community (<a href="https://x.com/WolfRiccardo/status/2041192232623972441">@WolfRiccardo</a>)</em></td>
<td valign="top"><img src="docs/example-handwritten-notebook.png" alt="Handwritten notebook flatlay" /><br><em>Handwritten notebook flatlay · community (<a href="https://x.com/patrickassale/status/2044569086013718958">@patrickassale</a>)</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-chess-midgame.png" alt="Chess board mid-game photorealism" /><br><em>Chess board mid-game · community (<a href="https://x.com/EddGorenstein/status/2046923077993259196">@EddGorenstein</a>)</em></td>
<td valign="top"><img src="docs/example-panorama-jungle.png" alt="360° equirectangular jungle panorama" /><br><em>360° equirectangular panorama · community (<a href="https://x.com/AIimagined/status/2046915800263802880">@AIimagined</a>)</em></td>
</tr>
</table>

### Cinematic & animation (landscape)

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-pixar-kitchen.png" alt="Pixar-style kitten in kitchen" /><br><em>Pixar-style 3D still (kitten + soufflé) · community style pattern</em></td>
<td width="50%" valign="top"><img src="docs/example-noir-detective.png" alt="1940s film-noir detective photo" /><br><em>1940s film-noir still · original (Alton / Toland lineage)</em></td>
</tr>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-storyboard.png" alt="6-panel film storyboard" width="85%" /><br><em>Professional 6-panel storyboard (Tokyo rooftop chase) · original</em></td>
</tr>
</table>

### Character design

<table>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-character-sheet.png" alt="Cyberpunk engineer character reference sheet" width="85%" /><br><em>Cyberpunk engineer reference sheet · community (<a href="https://x.com/MANISH1027512/status/2045013913901867334">@MANISH1027512</a>)</em></td>
</tr>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-anime-expression-grid.png" alt="16-panel anime expression grid" width="55%" /><br><em>16-panel anime expression grid · community (<a href="https://mp.weixin.qq.com/s/ASxig6mFVYxrIE8-8Fthew">卡尔的AI沃茨</a>)</em></td>
</tr>
</table>

### Research paper figures (landscape)

<table>
<tr>
<td width="50%" valign="top"><img src="docs/example-transformer-arch.png" alt="Transformer encoder-decoder architecture" /><br><em>Transformer encoder–decoder · Vaswani et al., 2017</em></td>
<td width="50%" valign="top"><img src="docs/example-rag-pipeline.png" alt="RAG pipeline diagram" /><br><em>Retrieval-Augmented Generation pipeline · Lewis et al., 2020</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-agent-architecture.png" alt="Multi-agent LLM system architecture" /><br><em>Multi-agent LLM system · AutoGen (Wu et al., 2023) / LangGraph / Managed Agents</em></td>
<td valign="top"><img src="docs/example-diffusion-chain.png" alt="Denoising diffusion chain" /><br><em>Denoising diffusion forward / reverse chain · Ho et al., 2020</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-scaling-curves.png" alt="Empirical scaling laws plot" /><br><em>Empirical scaling laws · Kaplan 2020, Chinchilla (Hoffmann et al., 2022)</em></td>
<td valign="top"><img src="docs/example-benchmark-heatmap.png" alt="Benchmark comparison heatmap" /><br><em>Benchmark comparison heatmap · HELM (Liang et al., 2023)</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-ablation-bars.png" alt="Ablation bar chart with error bars" /><br><em>Ablation bar chart · generic reasoning-paper layout</em></td>
<td valign="top"><img src="docs/example-data-sankey.png" alt="Pretraining data-mixture sankey" /><br><em>LLM pretraining data-mixture sankey · GPT-3 / LLaMA / Pile compositions</em></td>
</tr>
<tr>
<td valign="top"><img src="docs/example-attention-heatmap.png" alt="Multi-head attention heatmaps" /><br><em>Multi-head attention heatmaps · Clark et al., 2019</em></td>
<td valign="top"><img src="docs/example-model-timeline.png" alt="LLM family tree timeline" /><br><em>Frontier LLM lineage, 2018–2026 · community survey format</em></td>
</tr>
<tr>
<td colspan="2" align="center" valign="top"><img src="docs/example-react-trace.png" alt="ReAct reasoning trace" width="60%" /><br><em>ReAct reasoning trace · Yao et al., 2022</em></td>
</tr>
</table>

---

## Ecosystem

Drop-in for the broader agent ecosystem. Known-working integrations:

| Runtime | Trigger | Install hint |
|---|---|---|
| **Claude Code** | `/gpt-image …` or natural language | `~/.claude/skills/gpt-image/` |
| **Claude.ai Skills** | built-in skill picker | upload repo zip via the UI |
| **Codex** | `/gpt-image …` | drop under Codex's skills dir |
| **OpenCode** | auto-discovery on image-gen intent | drop under OpenCode's skills dir |
| **Cursor Agent** | `/gpt-image …` | paste [`SKILL.md`](SKILL.md) as system prompt |
| **Aider** | direct invoke | `/run uv run scripts/generate.py …` |
| **Hermes** | auto-discovery | per Hermes skill conventions |
| **Plain shell** | `uv run scripts/generate.py …` | zero agent needed |

Not listed? Any runtime that can execute a Python script and read `~/.env` works — the script has no SDK pin, no venv, just PEP 723 inline deps.

### Upstream credits

- **OpenAI** — the `gpt-image-2` model itself (`/v1/images/generations`, `/v1/images/edits`).
- [`ZeroLu/awesome-gpt-image`](https://github.com/ZeroLu/awesome-gpt-image) — 56 community-curated editorial prompts under CC BY 4.0; per-entry `@handle` attribution preserved in [`references/gallery.md`](references/gallery.md).
- **Research-figure prompts** — original contributions, paper inspirations cited per-entry (Vaswani, Lewis, Ho, Kaplan / Hoffmann, Madaan, Clark, Yao, Wu et al., Greshake, …).

### Reference files

| Need | File |
|---|---|
| Full flag table | [`SKILL.md`](SKILL.md) |
| 69 prompt templates with attribution | [`references/gallery.md`](references/gallery.md) |
| 12 prompt-craft principles | [`references/craft.md`](references/craft.md) |
| The script | [`scripts/generate.py`](scripts/generate.py) |

**API-key resolution** (later wins): process env → `./.env` → `~/.env`.

---

## License

CC BY 4.0 — see [`LICENSE`](LICENSE).
