from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
SCRIPT_FILE = OUTPUT_DIR / "script.txt"
MEDIA_MANIFEST_FILE = OUTPUT_DIR / "media_manifest.json"
RENDER_PLAN_FILE = OUTPUT_DIR / "render_plan.txt"
RENDER_CONFIG_FILE = OUTPUT_DIR / "render_config.json"
DEFAULT_SCRIPT = "Today we're counting down fun Roblox moments you need to see!"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def read_script() -> str:
    if not SCRIPT_FILE.exists():
        print("[render_video] Missing output/script.txt. Using fallback script text.")
        return DEFAULT_SCRIPT

    script_text = SCRIPT_FILE.read_text(encoding="utf-8").strip()
    return script_text or DEFAULT_SCRIPT


def read_media_manifest() -> dict:
    if not MEDIA_MANIFEST_FILE.exists():
        print("[render_video] Missing output/media_manifest.json. Using fallback manifest.")
        return {
            "topic": "Roblox trending moments",
            "search_queries": [],
            "images": [],
            "videos": [],
            "notes": ["No media manifest found. Replace placeholder media later."],
        }

    try:
        return json.loads(MEDIA_MANIFEST_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("[render_video] Invalid media_manifest.json. Using fallback manifest.")
        return {
            "topic": "Roblox trending moments",
            "search_queries": [],
            "images": [],
            "videos": [],
            "notes": ["Media manifest JSON was invalid. Replace placeholder media later."],
        }


def extract_script_lines(script_text: str) -> list[str]:
    return [line.strip() for line in script_text.splitlines() if line.strip()]


def build_render_config(scene_count: int) -> dict:
    return {
        "format": "1080x1920",
        "fps": 30,
        "subtitle_style": "Bold lower-third captions with high contrast",
        "transition_style": "Quick zoom pops and swipe cuts",
        "scene_count": scene_count,
        "cta_enabled": True,
    }


def build_visual_suggestions(manifest: dict, scene_count: int) -> list[str]:
    queries = manifest.get("search_queries", [])
    if not queries:
        queries = [manifest.get("topic", "Roblox trending moments")]

    suggestions = []
    for index in range(scene_count):
        suggestions.append(queries[index % len(queries)])
    return suggestions


def build_render_plan(script_text: str, manifest: dict, render_config: dict) -> str:
    script_lines = extract_script_lines(script_text)
    visual_suggestions = build_visual_suggestions(manifest, len(script_lines))

    lines = [
        "Render Plan",
        "===========",
        "",
        "Short format: 9:16 vertical video",
        f"Canvas: {render_config['format']}",
        f"Frame rate: {render_config['fps']} fps",
        f"Estimated scenes: {render_config['scene_count']}",
        "",
        f"Subtitle usage: {render_config['subtitle_style']}",
        f"Transition style: {render_config['transition_style']}",
        "Ranking card overlays: Show bright Number 5 to Number 1 cards with playful motion.",
        "CTA ending: Reserve the final beat for a follow/comment prompt.",
        "",
        "Background visual suggestions:",
    ]

    for query in manifest.get("search_queries", [])[:6]:
        lines.append(f"- {query}")

    if not manifest.get("search_queries"):
        lines.append(f"- {manifest.get('topic', 'Roblox trending moments')}")

    lines.extend(["", "Scene Breakdown:"])
    for index, narration_line in enumerate(script_lines, start=1):
        lines.append(f"{index}. Narration: {narration_line}")
        lines.append(f"   Visual: {visual_suggestions[index - 1]}")
        lines.append("   Overlay: Subtitle chunks plus a bold ranking card if this is a ranked item.")

    lines.extend(
        [
            "",
            "Notes:",
        ]
    )
    for note in manifest.get("notes", []):
        lines.append(f"- {note}")

    lines.extend(
        [
            "",
            "TODO:",
            "- Replace this text plan with a real FFmpeg render implementation.",
            "- Map scene timing, subtitle timing, voiceover timing, music, and overlays.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def save_render_plan(render_plan: str) -> Path:
    ensure_output_dir()
    RENDER_PLAN_FILE.write_text(render_plan, encoding="utf-8")
    print(f"[render_video] Saved render plan to {RENDER_PLAN_FILE.relative_to(PROJECT_ROOT)}")
    return RENDER_PLAN_FILE


def save_render_config(render_config: dict) -> Path:
    ensure_output_dir()
    RENDER_CONFIG_FILE.write_text(
        json.dumps(render_config, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[render_video] Saved render config to {RENDER_CONFIG_FILE.relative_to(PROJECT_ROOT)}")
    return RENDER_CONFIG_FILE


def main() -> str:
    script_text = read_script()
    manifest = read_media_manifest()
    script_lines = extract_script_lines(script_text)
    render_config = build_render_config(scene_count=len(script_lines))
    render_plan = build_render_plan(script_text, manifest, render_config)
    save_render_plan(render_plan)
    save_render_config(render_config)
    return render_plan


if __name__ == "__main__":
    main()
