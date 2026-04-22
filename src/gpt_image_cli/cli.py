#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx>=0.27",
#     "python-dotenv>=1.0",
# ]
# ///
"""General-purpose CLI for OpenAI GPT Image 2.

Wraps `/v1/images/generations` and `/v1/images/edits` with every documented
parameter exposed as a flag. Writes the returned PNG/JPEG/WebP bytes to disk
and prints the output path(s) on stdout. Designed for agents: reads
OPENAI_API_KEY from env, fails fast on errors, no hidden state.

Endpoints auto-selected: pass `-i / --image` (one or more) to switch from
generations → edits. Pass `-m / --mask` for alpha-channel inpainting on edits.

Exit codes: 0 success, 1 API error, 2 bad args.

Examples:
    # Basic generate, auto filename, 1K square
    uv run generate.py -p "a cat astronaut on the moon"

    # Named output, portrait 2K, high quality
    uv run generate.py -p "Chinese tea poster" -f poster.png --size 2k --quality high

    # Edit existing image
    uv run generate.py -p "colorize this manga page" -i page.jpg -f colored.png

    # Multi-reference edit (outfit transfer, pet + brand, etc.)
    uv run generate.py -p "77 × KFC collab poster" -i cat.png -i kfc_logo.png -f collab.png

    # Masked inpaint
    uv run generate.py -p "replace sky with aurora" -i photo.jpg -m sky_mask.png -f aurora.png

    # Grid of 4, transparent background, webp
    uv run generate.py -p "isometric chair, minimalist" -n 4 --background opaque --format webp
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv


API_BASE = "https://api.openai.com/v1/images"


def _load_env_chain() -> None:
    """Resolve OPENAI_API_KEY from the canonical config chain.

    Order (first match wins, later entries override earlier ones):
      1. process env (shell export, parent process)
      2. ./.env            (project-local)
      3. ~/.env            (user-global secret store)

    `override=True` for ~/.env reflects the common convention of using a
    dotenv file as the canonical secret store; when present, it wins over
    stale shell exports that may have diverged. If you do not use ~/.env,
    the call is a no-op and the process env is used as-is.
    """
    load_dotenv(Path.cwd() / ".env", override=False)
    load_dotenv(Path.home() / ".env", override=True)

SIZE_SHORTCUTS: dict[str, str] = {
    "1k": "1024x1024",
    "2k": "2048x2048",
    "4k": "3840x2160",
    "portrait": "1024x1536",
    "landscape": "1536x1024",
    "square": "1024x1024",
    "wide": "2048x1152",
    "tall": "2160x3840",
}

DEFAULT_MODEL = "gpt-image-2"
DEFAULT_SIZE = "1024x1024"
TIMEOUT_SECONDS = 300.0


def slugify(text: str, max_len: int = 30) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[-\s]+", "-", s)[:max_len]
    return s or "image"


def default_output_path(prompt: str, extension: str) -> Path:
    cwd = Path.cwd()
    target_dir = cwd / "fig" if (cwd / "fig").is_dir() else cwd
    stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return target_dir / f"{stamp}-{slugify(prompt)}.{extension}"


def resolve_size(value: str) -> str:
    return SIZE_SHORTCUTS.get(value.lower(), value)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="generate.py",
        description="Call OpenAI GPT Image 2 (generations or edits). All API params exposed.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("-p", "--prompt", required=True, help="Text prompt / edit instruction.")
    p.add_argument(
        "-f", "--file",
        help="Output path. Auto-generated as YYYY-MM-DD-HH-MM-SS-<slug>.<ext> if omitted "
             "(written to ./fig/ if that dir exists, else ./).",
    )
    p.add_argument(
        "-i", "--image", action="append", type=Path, default=None,
        help="Reference image path. Repeat flag for multi-reference edits. "
             "Presence of any -i switches endpoint to /v1/images/edits.",
    )
    p.add_argument(
        "-m", "--mask", type=Path, default=None,
        help="Alpha-channel PNG mask for inpainting (edits endpoint only). "
             "Opaque regions are preserved, transparent regions regenerated.",
    )
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Model ID (default {DEFAULT_MODEL}).")
    p.add_argument(
        "--size", default=DEFAULT_SIZE,
        help="Image size. Accepts literals (1024x1024, 1536x1024, 2048x2048, 3840x2160, "
             "any 16px-multiple up to 3840 max edge, 3:1 ratio cap) or shortcuts "
             "(1k, 2k, 4k, portrait, landscape, square, wide, tall). Default 1024x1024.",
    )
    p.add_argument(
        "--quality", default="high", choices=["auto", "low", "medium", "high"],
        help="Generations only. Rendering fidelity (cost scales ~10× per step). "
             "Default high — gpt-image-2's typography and scene density degrade noticeably below high. "
             "Ignored on /v1/images/edits (the endpoint rejects this parameter).",
    )
    p.add_argument("-n", "--n", type=int, default=1, help="Number of images to return. Default 1.")
    p.add_argument(
        "--background", default=None, choices=["auto", "opaque"],
        help="Generations only. `opaque` disables transparency. Default API-side auto.",
    )
    p.add_argument(
        "--moderation", default=None, choices=["auto", "low"],
        help="Generations only. `low` relaxes content filter. Default API-side auto.",
    )
    p.add_argument(
        "--format", dest="output_format", default=None,
        choices=["png", "jpeg", "webp"],
        help="Output encoding. Default png.",
    )
    p.add_argument(
        "--compression", dest="output_compression", type=int, default=None,
        help="0-100 compression level for jpeg/webp. Ignored for png.",
    )
    p.add_argument(
        "--user", default=None,
        help="Optional end-user identifier forwarded to OpenAI for abuse tracking.",
    )
    return p.parse_args()


def build_payload(args: argparse.Namespace, is_edit: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": args.model,
        "prompt": args.prompt,
        "size": resolve_size(args.size),
        "n": args.n,
    }
    # `quality`, `background`, `moderation` are /v1/images/generations-only.
    # /v1/images/edits rejects them with `unknown_parameter` errors.
    if not is_edit:
        payload["quality"] = args.quality
        if args.background:
            payload["background"] = args.background
        if args.moderation:
            payload["moderation"] = args.moderation
    if args.output_format:
        payload["output_format"] = args.output_format
    if args.output_compression is not None:
        payload["output_compression"] = args.output_compression
    if args.user:
        payload["user"] = args.user
    return payload


def call_generations(payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    r = httpx.post(
        f"{API_BASE}/generations",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )
    r.raise_for_status()
    return r.json()


def call_responses_edit(
    prompt: str,
    image_paths: list[Path],
    args: argparse.Namespace,
    api_key: str,
) -> dict[str, Any]:
    """Reference-image edit for gpt-image-2 via the Responses API.

    Why not /v1/images/edits directly? — that legacy endpoint currently accepts
    only `dall-e-2`. To get gpt-image-2 quality on a reference image we route
    through /v1/responses with the `image_generation` tool. The tool runs
    gpt-image-2 under the hood and accepts the same knobs (size, quality,
    background, output_format). Returns the canonical {data: [{b64_json}]}
    shape so `write_outputs` works unchanged.
    """
    import mimetypes

    content: list[dict[str, Any]] = []
    for p in image_paths:
        if not p.is_file():
            print(f"error: --image not found: {p}", file=sys.stderr)
            sys.exit(2)
        mime = mimetypes.guess_type(str(p))[0] or "image/png"
        b64 = base64.b64encode(p.read_bytes()).decode()
        content.append({"type": "input_image", "image_url": f"data:{mime};base64,{b64}"})
    content.append({"type": "input_text", "text": prompt})

    tool: dict[str, Any] = {"type": "image_generation", "model": args.model}
    resolved_size = resolve_size(args.size)
    if resolved_size and resolved_size != "auto":
        tool["size"] = resolved_size
    if args.quality:
        tool["quality"] = args.quality
    if args.output_format:
        tool["output_format"] = args.output_format
    if args.background:
        tool["background"] = args.background

    body = {
        "model": "gpt-4o",
        "input": [{"role": "user", "content": content}],
        "tools": [tool],
        "tool_choice": "auto",
    }

    r = httpx.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body,
        timeout=TIMEOUT_SECONDS,
    )
    r.raise_for_status()
    resp = r.json()

    data_items: list[dict[str, Any]] = []
    refusal_text: str | None = None
    for item in resp.get("output", []):
        if item.get("type") == "image_generation_call" and item.get("status") == "completed":
            result = item.get("result")
            if isinstance(result, str):
                data_items.append({"b64_json": result})
        elif item.get("type") == "message":
            for c in item.get("content", []) or []:
                if c.get("type") == "output_text":
                    refusal_text = c.get("text", "")

    if not data_items:
        msg = (refusal_text or "unknown")[:500]
        print(
            f"error: Responses API returned no image. Likely a content-policy refusal.\n"
            f"model replied: {msg}",
            file=sys.stderr,
        )
        sys.exit(1)
    return {"data": data_items}


def write_outputs(
    data: list[dict[str, Any]],
    out_path: Path,
    n: int,
) -> list[Path]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for i, item in enumerate(data):
        b64 = item.get("b64_json")
        url = item.get("url")
        if b64:
            raw = base64.b64decode(b64)
        elif url:
            raw = httpx.get(url, timeout=TIMEOUT_SECONDS).content
        else:
            print(f"error: response item {i} has neither b64_json nor url", file=sys.stderr)
            sys.exit(1)

        if n == 1:
            target = out_path
        else:
            stem = out_path.with_suffix("")
            target = stem.parent / f"{stem.name}_{i}{out_path.suffix}"
        target.write_bytes(raw)
        written.append(target)
    return written


def main() -> int:
    args = parse_args()

    _load_env_chain()
    try:
        api_key = os.environ["OPENAI_API_KEY"]
    except KeyError:
        print(
            "error: OPENAI_API_KEY not set. Add it to ~/.env or `export OPENAI_API_KEY=...`.",
            file=sys.stderr,
        )
        return 2

    ext = args.output_format or "png"
    out_path = Path(args.file).expanduser().resolve() if args.file else default_output_path(args.prompt, ext)

    is_edit = bool(args.image)
    if args.mask:
        print(
            "error: --mask (alpha-channel inpainting) is not supported for gpt-image-2. "
            "The Responses API image_generation tool does not accept masks.",
            file=sys.stderr,
        )
        return 2

    payload = build_payload(args, is_edit)

    try:
        if is_edit:
            resp = call_responses_edit(args.prompt, args.image, args, api_key)
        else:
            resp = call_generations(payload, api_key)
    except httpx.HTTPStatusError as e:
        body = e.response.text[:2000]
        print(f"error: {e.response.status_code} from OpenAI: {body}", file=sys.stderr)
        return 1

    data = resp.get("data") or []
    if not data:
        print(f"error: no image data in response: {resp}", file=sys.stderr)
        return 1

    written = write_outputs(data, out_path, args.n)
    for p in written:
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
