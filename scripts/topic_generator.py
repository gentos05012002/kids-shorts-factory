from __future__ import annotations

import json
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv() -> bool:
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
TOPIC_FILE = OUTPUT_DIR / "topic.txt"
TOPIC_DEBUG_FILE = OUTPUT_DIR / "topic_debug.json"
DEFAULT_TOPIC = "Roblox trending moments"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def to_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def unique_topics(topics: list[str]) -> list[str]:
    seen = set()
    result = []
    for topic in topics:
        clean_topic = " ".join(topic.split()).strip()
        if not clean_topic:
            continue
        key = clean_topic.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(clean_topic)
    return result


def fetch_fallback_topics() -> list[str]:
    """Return a curated kids-friendly topic list for stable single-run output."""
    topics = [
        "Roblox top animations",
        "99 Nights challenge",
        "Brookhaven roleplay trends",
        "Adopt Me updates",
        "Rainbow Friends secrets",
        "funny Roblox brainrot compilations",
        "trending obby moments",
        "Roblox meme edits",
        "viral Roblox challenge ideas",
        "Brookhaven funniest house builds",
        "Adopt Me rare pet moments",
        "Rainbow Friends hidden details",
        "best Roblox avatar trends",
        "viral Roblox prank roleplays",
    ]
    topics = unique_topics(topics)
    print(f"[topic_generator] Loaded {len(topics)} curated fallback topics.")
    return topics


def normalize_google_trend(title: str) -> str | None:
    """Map raw trend names to safe, relevant kids-shorts topics."""
    lowered = title.lower()

    if "roblox" in lowered:
        return title.strip()
    if "brookhaven" in lowered:
        return "Brookhaven roleplay trends"
    if "adopt me" in lowered:
        return "Adopt Me updates"
    if "rainbow friends" in lowered:
        return "Rainbow Friends secrets"
    if "obby" in lowered:
        return "trending obby moments"
    if "animation" in lowered:
        return "Roblox top animations"
    if "meme" in lowered:
        return "Roblox meme edits"
    return None


def fetch_google_trends_topics() -> list[str]:
    """Attempt a lightweight Google Trends RSS fetch when explicitly enabled."""
    url = "https://trends.google.com/trending/rss?geo=US"
    response = requests.get(url, timeout=8)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    mapped_topics = []
    for item in root.findall(".//item/title"):
        raw_title = (item.text or "").strip()
        normalized = normalize_google_trend(raw_title)
        if normalized:
            mapped_topics.append(normalized)

    topics = unique_topics(mapped_topics)
    print(f"[topic_generator] Google Trends hook returned {len(topics)} safe topic candidates.")
    return topics


def fetch_roblox_online_topics() -> list[str]:
    """Placeholder for future Roblox-specific topic discovery."""
    # TODO: Add a stable free Roblox-friendly source here, such as an official
    # feed or a curated API endpoint. Do not add fragile scraping by default.
    print(
        "[topic_generator] Roblox trends hook is enabled, but the stable free "
        "integration is still a TODO. Using fallback behavior for now."
    )
    return []


def try_fetch_online_topics() -> tuple[str, list[str]]:
    """Try optional online hooks and return a source label with the topics found."""
    load_dotenv()
    google_enabled = to_bool(os.getenv("GOOGLE_TRENDS_ENABLED", "false"))
    roblox_enabled = to_bool(os.getenv("ROBLOX_TRENDS_ENABLED", "false"))

    collected_topics = []
    successful_sources = []

    if google_enabled:
        try:
            google_topics = fetch_google_trends_topics()
            if google_topics:
                collected_topics.extend(google_topics)
                successful_sources.append("google_trends")
        except (requests.RequestException, ET.ParseError, ValueError) as exc:
            print(f"[topic_generator] Google Trends fetch failed: {exc}")

    if roblox_enabled:
        try:
            roblox_topics = fetch_roblox_online_topics()
            if roblox_topics:
                collected_topics.extend(roblox_topics)
                successful_sources.append("roblox_trends")
        except Exception as exc:  # pragma: no cover
            print(f"[topic_generator] Roblox trends hook failed: {exc}")

    collected_topics = unique_topics(collected_topics)
    if collected_topics:
        source = ",".join(successful_sources) or "online"
        print(f"[topic_generator] Using {len(collected_topics)} online topic candidates.")
        return source, collected_topics

    if not google_enabled and not roblox_enabled:
        print("[topic_generator] Online topic hooks are disabled. Using curated fallback topics.")
    else:
        print("[topic_generator] Online topic hooks returned no safe results. Falling back.")
    return "curated_fallback", []


def choose_topic(topics: list[str]) -> str:
    """Choose one topic from the available list."""
    if not topics:
        print(f"[topic_generator] No topics available. Using default topic: {DEFAULT_TOPIC}")
        return DEFAULT_TOPIC

    chosen_topic = random.choice(topics)
    print(f"[topic_generator] Selected topic: {chosen_topic}")
    return chosen_topic


def save_topic(topic: str) -> Path:
    ensure_output_dir()
    TOPIC_FILE.write_text(topic.strip() + "\n", encoding="utf-8")
    print(f"[topic_generator] Saved topic to {TOPIC_FILE.relative_to(PROJECT_ROOT)}")
    return TOPIC_FILE


def save_topic_debug(source: str, available_topics: list[str], chosen_topic: str) -> Path:
    ensure_output_dir()
    debug_payload = {
        "source": source,
        "available_topics": available_topics,
        "chosen_topic": chosen_topic,
    }
    TOPIC_DEBUG_FILE.write_text(
        json.dumps(debug_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[topic_generator] Saved topic debug data to {TOPIC_DEBUG_FILE.relative_to(PROJECT_ROOT)}")
    return TOPIC_DEBUG_FILE


def main() -> str:
    source, online_topics = try_fetch_online_topics()
    available_topics = online_topics if online_topics else fetch_fallback_topics()
    final_source = source if online_topics else "curated_fallback"

    chosen_topic = choose_topic(available_topics)
    save_topic(chosen_topic)
    save_topic_debug(final_source, available_topics, chosen_topic)
    return chosen_topic


if __name__ == "__main__":
    main()
