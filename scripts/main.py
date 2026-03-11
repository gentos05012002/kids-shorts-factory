from __future__ import annotations

import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
RUN_SUMMARY_FILE = OUTPUT_DIR / "run_summary.txt"
SCRIPTS_DIR = Path(__file__).resolve().parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import media_fetcher
import render_video
import script_generator
import topic_generator
import tts_generator
import upload_youtube


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def collect_generated_files() -> list[str]:
    ensure_output_dir()
    files = []
    for path in sorted(OUTPUT_DIR.iterdir()):
        if path.name == ".gitkeep" or not path.is_file():
            continue
        files.append(f"output/{path.name}")
    return files


def write_run_summary(
    run_id: str,
    timestamp: str,
    completed_steps: list[str],
    failed_steps: list[str],
    generated_files: list[str],
    final_status: str,
) -> Path:
    ensure_output_dir()

    lines = [
        "Kids Shorts Factory Run Summary",
        "===============================",
        f"run_id: {run_id}",
        f"timestamp: {timestamp}",
        f"final_status: {final_status}",
        "",
        "completed_steps:",
    ]

    if completed_steps:
        for step in completed_steps:
            lines.append(f"- {step}")
    else:
        lines.append("- none")

    lines.extend(["", "failed_steps:"])
    if failed_steps:
        for step in failed_steps:
            lines.append(f"- {step}")
    else:
        lines.append("- none")

    lines.extend(["", "generated_files:"])
    if generated_files:
        for file_path in generated_files:
            lines.append(f"- {file_path}")
    else:
        lines.append("- none")

    RUN_SUMMARY_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return RUN_SUMMARY_FILE


def run_pipeline() -> int:
    ensure_output_dir()

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"[main] Starting kids shorts pipeline run: {run_id}")

    steps = [
        ("topic_generator", topic_generator.main),
        ("script_generator", script_generator.main),
        ("media_fetcher", media_fetcher.main),
        ("tts_generator", tts_generator.main),
        ("render_video", render_video.main),
        ("upload_youtube", upload_youtube.main),
    ]

    completed_steps = []
    failed_steps = []
    final_status = "SUCCESS"

    try:
        for step_name, step_function in steps:
            print(f"[main] Step start: {step_name}")
            try:
                step_function()
                completed_steps.append(step_name)
                print(f"[main] Step complete: {step_name}")
            except Exception as exc:  # pragma: no cover
                error_text = f"{step_name} failed with {type(exc).__name__}: {exc}"
                failed_steps.append(error_text)
                final_status = "FAILED"
                print(f"[main] {error_text}")
                traceback.print_exc()
                break
    finally:
        generated_files = collect_generated_files()
        if "output/run_summary.txt" not in generated_files:
            generated_files.append("output/run_summary.txt")
        summary_path = write_run_summary(
            run_id=run_id,
            timestamp=timestamp,
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            generated_files=generated_files,
            final_status=final_status,
        )
        print(f"[main] Run summary saved to {summary_path.relative_to(PROJECT_ROOT)}")

    if final_status == "SUCCESS":
        print("[main] Pipeline completed successfully.")
        return 0

    print("[main] Pipeline stopped after an error.")
    return 1


if __name__ == "__main__":
    raise SystemExit(run_pipeline())
