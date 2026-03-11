from __future__ import annotations

import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv() -> bool:
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
TOPIC_FILE = OUTPUT_DIR / "topic.txt"
SCRIPT_DATA_FILE = OUTPUT_DIR / "script_data.json"
MEDIA_MANIFEST_FILE = OUTPUT_DIR / "media_manifest.json"
DEFAULT_TOPIC = "Roblox trending moments"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def read_topic() -> str:
    if not TOPIC_FILE.exists():
        print(f"[media_fetcher] Missing output/topic.txt. Using fallback topic: {DEFAULT_TOPIC}")
        return DEFAULT_TOPIC

    topic = TOPIC_FILE.read_text(encoding="utf-8").strip()
    return topic or DEFAULT_TOPIC


def read_script_data() -> dict:
    if not SCRIPT_DATA_FILE.exists():
        print("[media_fetcher] Missing output/script_data.json. Using fallback ranked content.")
        return {
            "topic": DEFAULT_TOPIC,
            "intro": "",
            "ranked_items": [],
            "cta": "",
        }

    try:
        return json.loads(SCRIPT_DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("[media_fetcher] Invalid script_data.json. Using fallback ranked content.")
        return {
            "topic": DEFAULT_TOPIC,
            "intro": "",
            "ranked_items": [],
            "cta": "",
        }


def slugify(value: str) -> str:
    characters = []
    for char in value.lower():
        if char.isalnum():
            characters.append(char)
        elif char in {" ", "-", "_"}:
            characters.append("_")
    slug = "".join(characters).strip("_")
    return "_".join(part for part in slug.split("_") if part)


def unique_strings(values: list[str]) -> list[str]:
    seen = set()
    unique_values = []
    for value in values:
        clean_value = " ".join(value.split()).strip()
        if not clean_value:
            continue
        key = clean_value.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_values.append(clean_value)
    return unique_values


def build_search_queries(topic: str, ranked_items: list[str]) -> list[str]:
    queries = [
        f"{topic} Roblox vertical gameplay",
        f"{topic} meme edit background",
        f"{topic} kids short visual",
    ]

    for item in ranked_items[:5]:
        queries.append(f"{topic} {item}")
        queries.append(f"Roblox {item} vertical scene")

    return unique_strings(queries)


def build_placeholder_assets(
    search_queries: list[str],
    asset_type: str,
    source_label: str,
    limit: int,
) -> list[dict]:
    extension = "png" if asset_type == "image" else "mp4"
    assets = []

    for index, query in enumerate(search_queries[:limit], start=1):
        assets.append(
            {
                "id": f"{asset_type}_{index}",
                "type": f"placeholder_{asset_type}",
                "query": query,
                "source": source_label,
                "status": "placeholder_ready",
                "path_hint": f"media/{slugify(query)}_{index}.{extension}",
            }
        )

    return assets


def create_media_manifest(topic: str, script_data: dict) -> dict:
    load_dotenv()
    ranked_items = script_data.get("ranked_items", [])
    search_queries = build_search_queries(topic, ranked_items)

    pexels_key = os.getenv("PEXELS_API_KEY", "").strip()
    pixabay_key = os.getenv("PIXABAY_API_KEY", "").strip()

    image_source = "placeholder"
    video_source = "placeholder"
    notes = [
        "Use only bright, safe, kids-friendly visuals.",
        "Prefer Roblox-style gameplay clips, funny edits, and non-scary reactions.",
        "Keep every asset easy to replace with real fetched media later.",
    ]

    if pixabay_key:
        image_source = "pixabay_stub"
        notes.append("PIXABAY_API_KEY detected. Real Pixabay image fetching is still a TODO.")
    else:
        notes.append("PIXABAY_API_KEY missing. Using placeholder image entries.")

    if pexels_key:
        video_source = "pexels_stub"
        notes.append("PEXELS_API_KEY detected. Real Pexels video fetching is still a TODO.")
    else:
        notes.append("PEXELS_API_KEY missing. Using placeholder video entries.")

    # TODO: When the real media integration is ready, replace these placeholder
    # entries with fetched asset metadata and downloaded local file paths.
    manifest = {
        "topic": topic,
        "search_queries": search_queries,
        "images": build_placeholder_assets(search_queries, "image", image_source, limit=4),
        "videos": build_placeholder_assets(search_queries, "video", video_source, limit=3),
        "notes": notes,
    }
    return manifest


def save_media_manifest(manifest: dict) -> Path:
    ensure_output_dir()
    MEDIA_MANIFEST_FILE.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[media_fetcher] Saved media manifest to {MEDIA_MANIFEST_FILE.relative_to(PROJECT_ROOT)}")
    return MEDIA_MANIFEST_FILE


def main() -> dict:
    topic = read_topic()
    script_data = read_script_data()
    print(f"[media_fetcher] Building media manifest for topic: {topic}")
    manifest = create_media_manifest(topic, script_data)
    save_media_manifest(manifest)
    return manifest


if __name__ == "__main__":
    main()
