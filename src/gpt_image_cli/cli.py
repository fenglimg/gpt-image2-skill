#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai>=1.55",
#     "python-dotenv>=1.0",
# ]
# ///
"""General-purpose CLI for OpenAI GPT Image 2.

Mirrors the two official endpoints from the OpenAI cookbook using the official
`openai` Python SDK:

    client.images.generate(...)   — text → image          (no  -i)
    client.images.edit(...)       — text + image(s) → image (with -i; mask via -m)

Every documented parameter is exposed as a flag. Reads OPENAI_API_KEY from
process env, then .env, then ~/.env without overriding existing env. Writes the
returned PNG/JPEG/WebP bytes to disk and prints the output path(s) on stdout.

Exit codes: 0 success, 1 API error, 2 bad args.

Examples:
    # Basic generate, auto filename, 1K square
    gpt-image -p "a cat astronaut on the moon"

    # Named output, portrait 2K, high quality
    gpt-image -p "Chinese tea poster" -f poster.png --size 2k --quality high

    # Edit existing image (colorize, restyle, translate text, etc.)
    gpt-image -p "colorize this manga page" -i page.jpg -f colored.png

    # Multi-reference edit (outfit transfer, pet + brand, etc.)
    gpt-image -p "77 × KFC collab poster" -i cat.png -i kfc_logo.png -f collab.png

    # Alpha-channel inpaint (mask opaque = keep, transparent = regenerate)
    gpt-image -p "replace sky with aurora" -i photo.jpg -m sky_mask.png -f aurora.png

    # Grid of 4, transparent background, webp
    gpt-image -p "isometric chair, minimalist" -n 4 --background opaque --format webp

    # Skill launcher (same implementation, installed skill-folder path)
    uv run "$SKILL_DIR/scripts/generate.py" -p "a cat astronaut on the moon"
"""
from __future__ import annotations

import argparse
import base64
import http.client
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APIError, OpenAI


def _load_env_chain() -> None:
    """Resolve OPENAI_API_KEY without overriding runtime-provided env.

    Order: process env → ./.env → ~/.env. Existing process env wins so
    hosted agents or explicit shell exports are not replaced by local files.
    """
    load_dotenv(Path.cwd() / ".env", override=False)
    load_dotenv(Path.home() / ".env", override=False)


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
DEFAULT_MODERATION = "low"
DEFAULT_PROVIDER = "openai"
RIGHT_CODE_BASE_URL = "https://www.right.codes/draw"


class ImageItem:
    def __init__(self, b64_json: str | None = None, url: str | None = None) -> None:
        self.b64_json = b64_json
        self.url = url


class ImageResult:
    def __init__(self, data: list[ImageItem]) -> None:
        self.data = data


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


def model_rejects_input_fidelity(model: str) -> bool:
    return model.strip().lower().startswith("gpt-image-2")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="gpt-image",
        description="Call GPT Image 2 via OpenAI or an OpenAI-compatible image proxy.",
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
             "Presence of any -i switches endpoint to client.images.edit().",
    )
    p.add_argument(
        "-m", "--mask", type=Path, default=None,
        help="Alpha-channel PNG mask (opaque = preserved, transparent = regenerated). "
             "Edits endpoint only; requires -i.",
    )
    p.add_argument(
        "--model",
        default=os.environ.get("GPT_IMAGE_MODEL", DEFAULT_MODEL),
        help=f"Model ID (default {DEFAULT_MODEL}, or GPT_IMAGE_MODEL).",
    )
    p.add_argument(
        "--provider",
        default=os.environ.get("GPT_IMAGE_PROVIDER", DEFAULT_PROVIDER),
        choices=["openai", "rightcode-images", "rightcode-chat"],
        help="API provider. Defaults to GPT_IMAGE_PROVIDER or openai.",
    )
    p.add_argument(
        "--base-url",
        default=os.environ.get("GPT_IMAGE_BASE_URL") or os.environ.get("OPENAI_BASE_URL"),
        help="API base URL. Right Code defaults to https://www.right.codes/draw.",
    )
    p.add_argument(
        "--api-key-env",
        default=os.environ.get("GPT_IMAGE_API_KEY_ENV"),
        help="Environment variable name that stores the API key.",
    )
    p.add_argument(
        "--api-key",
        default=None,
        help="API key value. Prefer env vars; this flag is mainly for one-off local testing.",
    )
    p.add_argument(
        "--size", default=DEFAULT_SIZE,
        help="Image size. Accepts literals (1024x1024, 1536x1024, 2048x2048, 3840x2160, "
             "any 16px-multiple up to 3840 max edge, 3:1 ratio cap) or shortcuts "
             "(1k, 2k, 4k, portrait, landscape, square, wide, tall). Default 1024x1024.",
    )
    p.add_argument(
        "--quality", default="high", choices=["auto", "low", "medium", "high"],
        help="Rendering fidelity / budget knob (cost scales ~10× per step). Default high. "
             "Use low for cheap drafts, medium for normal exploration, high for final text-heavy or shipping-facing assets.",
    )
    p.add_argument("-n", "--n", type=int, default=1, help="Number of images to return. Default 1.")
    p.add_argument(
        "--background", default=None, choices=["auto", "opaque"],
        help="`opaque` disables transparency. Default API-side auto.",
    )
    p.add_argument(
        "--moderation", default=DEFAULT_MODERATION, choices=["auto", "low"],
        help="Generations only. Default low. Use `auto` if you want the stricter API-side default.",
    )
    p.add_argument(
        "--input-fidelity", dest="input_fidelity", default=None, choices=["low", "high"],
        help="Edits only. gpt-image-2 rejects this parameter, so the CLI drops it locally before calling the API.",
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


def _filter_none(d: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose value is None — SDK treats missing vs None differently."""
    return {k: v for k, v in d.items() if v is not None}


def provider_base_url(args: argparse.Namespace) -> str | None:
    if args.base_url:
        return str(args.base_url).rstrip("/")
    if args.provider.startswith("rightcode"):
        return RIGHT_CODE_BASE_URL
    return None


def resolve_api_key(args: argparse.Namespace) -> str | None:
    if args.api_key:
        return args.api_key
    env_names = []
    if args.api_key_env:
        env_names.append(args.api_key_env)
    if args.provider.startswith("rightcode"):
        env_names.extend(["RIGHT_CODE_API_KEY", "RIGHT_CODES_API_KEY", "GPT_IMAGE_API_KEY"])
    env_names.append("OPENAI_API_KEY")
    for name in env_names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def openai_client(args: argparse.Namespace, api_key: str) -> OpenAI:
    base_url = provider_base_url(args)
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def call_generate(client: OpenAI, args: argparse.Namespace) -> Any:
    return client.images.generate(**_filter_none({
        "model": args.model,
        "prompt": args.prompt,
        "size": resolve_size(args.size),
        "quality": args.quality,
        "n": args.n,
        "background": args.background,
        "moderation": args.moderation,
        "output_format": args.output_format,
        "output_compression": args.output_compression,
        "user": args.user,
    }))


def post_json(url: str, api_key: str, body: dict[str, Any], stream: bool = False) -> Any:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream" if stream else "application/json",
        },
        method="POST",
    )
    return urllib.request.urlopen(request, timeout=600)  # noqa: S310 - user-configured API host


def local_image_to_base64(path: Path) -> str:
    if not path.is_file():
        print(f"error: --image not found: {path}", file=sys.stderr)
        sys.exit(2)
    return base64.b64encode(path.read_bytes()).decode("ascii")


def rightcode_images_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload = {
        "model": args.model,
        "prompt": args.prompt,
        "image": [local_image_to_base64(p) for p in (args.image or [])],
        "size": resolve_size(args.size),
        "response_format": "url",
    }
    return _filter_none(payload)


def normalize_image_items(payload: dict[str, Any]) -> list[ImageItem]:
    items: list[ImageItem] = []
    for item in payload.get("data") or []:
        if isinstance(item, dict):
            items.append(ImageItem(b64_json=item.get("b64_json"), url=item.get("url")))
    return items


def call_rightcode_images(args: argparse.Namespace, api_key: str) -> ImageResult:
    base_url = provider_base_url(args) or RIGHT_CODE_BASE_URL
    with post_json(f"{base_url}/v1/images/generations", api_key, rightcode_images_payload(args)) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return ImageResult(normalize_image_items(payload))


def extract_image_items_from_text(text: str) -> list[ImageItem]:
    items: list[ImageItem] = []
    for match in re.finditer(r"data:image/[^;]+;base64,([A-Za-z0-9+/=\r\n]+)", text):
        items.append(ImageItem(b64_json=re.sub(r"\s+", "", match.group(1))))
    for match in re.finditer(r"https?://[^\s)\"']+\.(?:png|jpe?g|webp)(?:\?[^\s)\"']*)?", text, re.I):
        items.append(ImageItem(url=match.group(0)))
    return items


def stream_chat_content(response: Any) -> str:
    chunks: list[str] = []
    for raw_line in response:
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if not data or data == "[DONE]":
            continue
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            continue
        for choice in payload.get("choices") or []:
            delta = choice.get("delta") or {}
            content = delta.get("content")
            if content:
                chunks.append(content)
    return "".join(chunks)


def call_rightcode_chat(args: argparse.Namespace, api_key: str) -> ImageResult:
    base_url = provider_base_url(args) or RIGHT_CODE_BASE_URL
    body = {
        "model": args.model,
        "stream": True,
        "messages": [
            {
                "role": "user",
                "content": args.prompt,
            }
        ],
    }
    with post_json(f"{base_url}/v1/chat/completions", api_key, body, stream=True) as response:
        content = stream_chat_content(response)
    items = extract_image_items_from_text(content)
    if not items:
        print("error: Right Code chat response did not contain an image URL or data URL.", file=sys.stderr)
        if content:
            print(content[:1000], file=sys.stderr)
        sys.exit(1)
    return ImageResult(items[: args.n])


def call_edit(client: OpenAI, args: argparse.Namespace) -> Any:
    for p in args.image:
        if not p.is_file():
            print(f"error: --image not found: {p}", file=sys.stderr)
            sys.exit(2)
    if args.mask and not args.mask.is_file():
        print(f"error: --mask not found: {args.mask}", file=sys.stderr)
        sys.exit(2)

    input_fidelity = args.input_fidelity
    if input_fidelity and model_rejects_input_fidelity(args.model):
        print(
            "note: dropping --input-fidelity because gpt-image-2 rejects that parameter.",
            file=sys.stderr,
        )
        input_fidelity = None

    image_handles = [p.open("rb") for p in args.image]
    mask_handle = args.mask.open("rb") if args.mask else None
    try:
        return client.images.edit(**_filter_none({
            "model": args.model,
            "image": image_handles,
            "mask": mask_handle,
            "prompt": args.prompt,
            "size": resolve_size(args.size),
            "quality": args.quality,
            "n": args.n,
            "background": args.background,
            "input_fidelity": input_fidelity,
            "output_format": args.output_format,
            "output_compression": args.output_compression,
            "user": args.user,
        }))
    finally:
        for h in image_handles:
            h.close()
        if mask_handle:
            mask_handle.close()


def write_outputs(data: list[Any], out_path: Path, n: int) -> list[Path]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for i, item in enumerate(data):
        b64 = item.get("b64_json") if isinstance(item, dict) else getattr(item, "b64_json", None)
        url = item.get("url") if isinstance(item, dict) else getattr(item, "url", None)
        if b64:
            raw = base64.b64decode(b64)
        elif url:
            with urllib.request.urlopen(url, timeout=300) as r:  # noqa: S310 — OpenAI-owned host
                raw = r.read()
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
    _load_env_chain()
    args = parse_args()
    api_key = resolve_api_key(args)
    if not api_key:
        print(
            "error: API key not set. Add OPENAI_API_KEY, RIGHT_CODE_API_KEY, GPT_IMAGE_API_KEY, "
            "or pass --api-key-env.",
            file=sys.stderr,
        )
        return 2

    if args.mask and not args.image:
        print("error: --mask requires --image (edits endpoint only)", file=sys.stderr)
        return 2

    ext = args.output_format or "png"
    out_path = Path(args.file).expanduser().resolve() if args.file else default_output_path(args.prompt, ext)

    try:
        if args.provider == "openai":
            client = openai_client(args, api_key)
            result = call_edit(client, args) if args.image else call_generate(client, args)
        elif args.provider == "rightcode-images":
            if args.mask:
                print("error: --mask is only supported by the openai provider.", file=sys.stderr)
                return 2
            result = call_rightcode_images(args, api_key)
        else:
            if args.image or args.mask:
                print("error: rightcode-chat currently supports text-to-image only.", file=sys.stderr)
                return 2
            result = call_rightcode_chat(args, api_key)
    except APIError as e:
        print(f"error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"error: HTTP {e.code}: {body[:1000]}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"error: URL error: {e}", file=sys.stderr)
        return 1
    except http.client.RemoteDisconnected as e:
        print(f"error: remote disconnected before sending a response: {e}", file=sys.stderr)
        return 1

    data = result.data or []
    if not data:
        print(f"error: no image data in response: {result}", file=sys.stderr)
        return 1

    for p in write_outputs(data, out_path, args.n):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
