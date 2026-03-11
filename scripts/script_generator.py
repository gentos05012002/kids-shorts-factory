from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
TOPIC_FILE = OUTPUT_DIR / "topic.txt"
SCRIPT_FILE = OUTPUT_DIR / "script.txt"
SCRIPT_DATA_FILE = OUTPUT_DIR / "script_data.json"
DEFAULT_TOPIC = "Roblox trending moments"
DEFAULT_ITEM_COUNT = 5


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def read_topic() -> str:
    if not TOPIC_FILE.exists():
        print(f"[script_generator] Missing output/topic.txt. Using fallback topic: {DEFAULT_TOPIC}")
        return DEFAULT_TOPIC

    topic = TOPIC_FILE.read_text(encoding="utf-8").strip()
    return topic or DEFAULT_TOPIC


def build_intro(topic: str) -> str:
    return f"Today we're checking out the top 5 picks for {topic} right now!"


def build_ranked_items(topic: str, item_count: int = DEFAULT_ITEM_COUNT) -> list[str]:
    topic_lower = topic.lower()

    keyword_templates = {
        "brookhaven": [
            "wild roleplay intros",
            "secret room flexes",
            "funny family plot twists",
            "mansion reveal moments",
            "instant replay endings",
        ],
        "adopt me": [
            "surprise pet trades",
            "rare egg reveals",
            "house glow-up flexes",
            "update reaction moments",
            "dream pet wins",
        ],
        "rainbow friends": [
            "hidden map details",
            "close-call escapes",
            "smart hiding spots",
            "funny chase fails",
            "secret ending clues",
        ],
        "99 nights": [
            "safe first-night plays",
            "clutch team saves",
            "loot route upgrades",
            "last-second recoveries",
            "survival streak moments",
        ],
        "brainrot": [
            "chaotic meme edits",
            "sound effect overloads",
            "caption spam timing",
            "random combo jokes",
            "replay-worthy endings",
        ],
        "animation": [
            "smooth intro moves",
            "dramatic zoom reveals",
            "funny reaction loops",
            "clean transition pops",
            "big finale shots",
        ],
        "obby": [
            "perfect jump saves",
            "funny fail clips",
            "speedrun shortcuts",
            "rage-to-win moments",
            "crazy finish jumps",
        ],
        "meme": [
            "fast-cut reaction edits",
            "silly sound syncs",
            "avatar face zooms",
            "glitchy joke transitions",
            "top replay moments",
        ],
    }

    ranked_items = [
        "fast trend clips",
        "funny replay moments",
        "secret little details",
        "crowd favorite twists",
        "big finish reveals",
    ]

    for keyword, template_items in keyword_templates.items():
        if keyword in topic_lower:
            ranked_items = template_items
            break

    return ranked_items[:item_count]


def build_cta() -> str:
    return "Comment your number one pick and follow for more kid-friendly Shorts!"


def build_script_data(topic: str) -> dict:
    # TODO: Replace this template-only logic with an LLM step later if the
    # project needs more dynamic scripts.
    intro = build_intro(topic)
    ranked_items = build_ranked_items(topic)
    cta = build_cta()
    return {
        "topic": topic,
        "intro": intro,
        "ranked_items": ranked_items,
        "cta": cta,
    }


def render_script(script_data: dict) -> str:
    ranked_items = script_data["ranked_items"]
    total_items = len(ranked_items)

    lines = [script_data["intro"], ""]
    for index, item in enumerate(ranked_items):
        rank_number = total_items - index
        lines.append(f"Number {rank_number}: {item}.")

    lines.extend(["", script_data["cta"]])
    return "\n".join(lines).strip() + "\n"


def save_script(script_text: str) -> Path:
    ensure_output_dir()
    SCRIPT_FILE.write_text(script_text, encoding="utf-8")
    print(f"[script_generator] Saved script to {SCRIPT_FILE.relative_to(PROJECT_ROOT)}")
    return SCRIPT_FILE


def save_script_data(script_data: dict) -> Path:
    ensure_output_dir()
    SCRIPT_DATA_FILE.write_text(
        json.dumps(script_data, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[script_generator] Saved script data to {SCRIPT_DATA_FILE.relative_to(PROJECT_ROOT)}")
    return SCRIPT_DATA_FILE


def main() -> str:
    topic = read_topic()
    print(f"[script_generator] Building ranking script for topic: {topic}")
    script_data = build_script_data(topic)
    script_text = render_script(script_data)
    save_script(script_text)
    save_script_data(script_data)
    return script_text


if __name__ == "__main__":
    main()
