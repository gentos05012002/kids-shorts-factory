from __future__ import annotations

import json
import os
import re
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv() -> bool:
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
SCRIPT_FILE = OUTPUT_DIR / "script.txt"
VOICEOVER_FILE = OUTPUT_DIR / "voiceover.txt"
TTS_CONFIG_FILE = OUTPUT_DIR / "tts_config.json"
DEFAULT_SCRIPT = "Today we're counting down fun Roblox moments you need to see!"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def read_script() -> str:
    if not SCRIPT_FILE.exists():
        print("[tts_generator] Missing output/script.txt. Using fallback script text.")
        return DEFAULT_SCRIPT

    script_text = SCRIPT_FILE.read_text(encoding="utf-8").strip()
    return script_text or DEFAULT_SCRIPT


def normalize_line(line: str) -> str:
    line = " ".join(line.split())
    line = re.sub(r"\s+([,.;:!?])", r"\1", line)
    return line.strip()


def clean_voiceover_text(script_text: str) -> str:
    cleaned_lines = []
    for line in script_text.splitlines():
        normalized = normalize_line(line)
        if normalized:
            cleaned_lines.append(normalized)

    if not cleaned_lines:
        cleaned_lines.append(DEFAULT_SCRIPT)

    return "\n".join(cleaned_lines)


def build_tts_config() -> dict:
    load_dotenv()
    return {
        "engine": os.getenv("TTS_ENGINE", "placeholder").strip() or "placeholder",
        "language": os.getenv("TTS_LANGUAGE", "en").strip() or "en",
        "voice": os.getenv("TTS_VOICE", "default").strip() or "default",
        "enabled": False,
    }


def save_voiceover_text(voiceover_text: str) -> Path:
    ensure_output_dir()
    VOICEOVER_FILE.write_text(voiceover_text.strip() + "\n", encoding="utf-8")
    print(f"[tts_generator] Saved voiceover text to {VOICEOVER_FILE.relative_to(PROJECT_ROOT)}")
    return VOICEOVER_FILE


def save_tts_config(tts_config: dict) -> Path:
    ensure_output_dir()
    TTS_CONFIG_FILE.write_text(
        json.dumps(tts_config, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[tts_generator] Saved TTS config to {TTS_CONFIG_FILE.relative_to(PROJECT_ROOT)}")
    return TTS_CONFIG_FILE


def main() -> str:
    script_text = read_script()
    voiceover_text = clean_voiceover_text(script_text)
    tts_config = build_tts_config()

    # TODO: Integrate Piper TTS or an external TTS provider here. The current
    # step only prepares normalized text and a config file, and should remain
    # safe even when no audio engine is installed.
    save_voiceover_text(voiceover_text)
    save_tts_config(tts_config)
    return voiceover_text


if __name__ == "__main__":
    main()
