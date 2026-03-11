# Kids Shorts Factory

Kids Shorts Factory is a cloud-first, single-run Python pipeline for generating kids-friendly YouTube Shorts planning assets around Roblox, animations, memes, Brookhaven, Adopt Me, Rainbow Friends, "99 Nights", and similar trend-friendly topics.

One run does the full job:

1. collect topic ideas
2. choose one topic
3. generate a short ranking-style script
4. prepare media search metadata
5. prepare cleaned voiceover text
6. prepare a render plan
7. prepare upload metadata
8. save outputs
9. exit cleanly

The project is intentionally modular and beginner-readable. Some modules already support cloud-ready hooks, but real external integrations are still placeholders with safe fallback behavior.

## Current Status

Current state:

- The full pipeline runs end to end with one command.
- Topic generation supports curated fallback topics and optional online hooks.
- Script generation is template-based only.
- Media, TTS, render, and upload steps generate structured planning files.
- Real trend APIs, real media fetch, real TTS, and real YouTube upload are still TODO items.

This keeps the repo stable for GitHub Actions while leaving clean upgrade points for later.

## Pipeline Flow

`topic_generator.py`
- loads curated fallback topics
- optionally tries online topic hooks
- saves `output/topic.txt`
- saves `output/topic_debug.json`

`script_generator.py`
- reads the topic
- builds a short ranked script
- saves `output/script.txt`
- saves `output/script_data.json`

`media_fetcher.py`
- reads the topic and script data
- builds search queries and placeholder asset metadata
- saves `output/media_manifest.json`

`tts_generator.py`
- reads the script
- normalizes voiceover text
- saves `output/voiceover.txt`
- saves `output/tts_config.json`

`render_video.py`
- reads the script and media manifest
- creates a production-oriented text render plan
- saves `output/render_plan.txt`
- saves `output/render_config.json`

`upload_youtube.py`
- reads topic and script data
- builds YouTube Shorts metadata
- saves `output/upload_metadata.json`
- saves `output/youtube_config.json`

`main.py`
- runs every step in sequence
- handles failures clearly
- saves `output/run_summary.txt`

## Project Structure

```text
.
|- .env.example
|- .github/
|  |- workflows/
|  |  |- generate.yml
|- .gitignore
|- README.md
|- logs/
|  |- .gitkeep
|- media/
|  |- .gitkeep
|- output/
|  |- .gitkeep
|- requirements.txt
|- scripts/
|  |- main.py
|  |- media_fetcher.py
|  |- render_video.py
|  |- script_generator.py
|  |- topic_generator.py
|  |- tts_generator.py
|  |- upload_youtube.py
|- voices/
|  |- .gitkeep
```

## Quick Start

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/main.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts/main.py
```

Run the pipeline one step at a time:

```bash
python scripts/topic_generator.py
python scripts/script_generator.py
python scripts/media_fetcher.py
python scripts/tts_generator.py
python scripts/render_video.py
python scripts/upload_youtube.py
```

## Output Files From One Run

The pipeline writes these files into `output/`:

- `topic.txt`
- `topic_debug.json`
- `script.txt`
- `script_data.json`
- `media_manifest.json`
- `voiceover.txt`
- `tts_config.json`
- `render_plan.txt`
- `render_config.json`
- `upload_metadata.json`
- `youtube_config.json`
- `run_summary.txt`

These files are safe planning artifacts. They make the pipeline useful today even before real media, TTS, or upload integrations are connected.

## Environment Variables

The repo uses `.env` values when available.

- `YOUTUBE_CLIENT_SECRET=` placeholder for future upload support
- `YOUTUBE_CLIENT_ID=` placeholder for future upload support
- `PEXELS_API_KEY=` optional future media hook
- `PIXABAY_API_KEY=` optional future media hook
- `GOOGLE_TRENDS_ENABLED=false` optional online topic hook
- `ROBLOX_TRENDS_ENABLED=false` optional Roblox-specific topic hook
- `TTS_ENGINE=placeholder` future TTS engine selector
- `TTS_LANGUAGE=en` future TTS language
- `TTS_VOICE=default` future TTS voice
- `UPLOAD_TO_YOUTUBE=false` upload toggle

If these values are missing, the pipeline falls back to safe placeholder behavior instead of crashing.

## GitHub Actions

The repo includes `.github/workflows/generate.yml`.

It supports:

- manual runs through `workflow_dispatch`
- scheduled runs every 6 hours
- Python 3.11 on `ubuntu-latest`
- automatic `.env` fallback from `.env.example`
- artifact upload of the `output/` folder

GitHub Actions is the main cloud-first path for running this project as a single-shot job.

## Notes About Placeholders

Several modules are intentionally placeholder-first right now:

- topic online fetching uses guarded hooks and safe fallback
- media fetching generates structured asset metadata instead of downloading files
- TTS prepares clean voiceover text and config only
- render planning creates a production plan, not a real FFmpeg output yet
- YouTube upload writes metadata and config, but does not upload yet

This is deliberate. The current goal is a stable, cloud-first pipeline that can be upgraded safely.

## Future Upgrade Path

Best next upgrades:

- connect a real trend source
- connect real media fetch
- connect real TTS
- connect real YouTube upload
