# EmbedClipFarm

Semantic search over YouTube content — search by meaning, not just keywords.

EmbedClipFarm indexes YouTube video transcripts (and optionally visual keyframes) into vector embeddings, letting you find relevant moments even when the exact words aren't spoken.

**Web UI:** [artificialnouveau.github.io/miniprojects/embedclipfarm](https://artificialnouveau.github.io/miniprojects/embedclipfarm/)

**Source:** [github.com/artificialnouveau/artificialnouveau.github.io/tree/master/miniprojects/embedclipfarm](https://github.com/artificialnouveau/artificialnouveau.github.io/tree/master/miniprojects/embedclipfarm)

## How it works

Transcripts are split into ~30-second chunks and converted into 384-dimensional vector embeddings using [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). When you search, your query is embedded the same way and results are ranked by cosine similarity.

## Setup

```bash
pip install -r requirements.txt
```

Core dependencies: `youtube-transcript-api`, `chromadb`, `sentence-transformers`, `numpy`, `python-dotenv`, `yt-dlp`

Optional dependencies (install as needed):
- `open-clip-torch`, `Pillow` — CLIP visual embeddings
- `faster-whisper` — local speech-to-text for videos without captions
- `deepmultilingualpunctuation` — punctuation restoration
- `pyannote-audio` — speaker diarization (requires `HF_TOKEN` in `.env`)

## CLI Usage (`embedclipfarm.py`)

### Index videos

Indexing is the first step — it downloads transcripts (auto-captions) from YouTube videos, splits them into ~30-second chunks, and converts each chunk into a vector embedding that captures its semantic meaning. These embeddings are stored in a local database so you can search them later. You only need to index once per video; after that, you can search as many times as you want.

```bash
# Single video
python embedclipfarm.py index "https://youtube.com/watch?v=VIDEO_ID"

# Multiple videos
python embedclipfarm.py index "URL1" "URL2" "URL3"

# Channel (most recent videos)
python embedclipfarm.py index "@channelname" --max-videos 20

# Playlist
python embedclipfarm.py index "https://youtube.com/playlist?list=PLxxxxx"

# From a file of URLs
python embedclipfarm.py index urls.txt
```

**Optional flags for indexing:**

| Flag | Description |
|------|-------------|
| `--vision gemini` | Annotate keyframes with Gemini vision (set `GEMINI_API_KEY` in `.env`) |
| `--vision claude` | Annotate keyframes with Claude vision (set `ANTHROPIC_API_KEY` in `.env`) |
| `--clip` | Local CLIP visual embeddings (no API key needed) |
| `--whisper` | Transcribe audio locally with Whisper for videos without captions |
| `--whisper-model base` | Whisper model size (default: `base`) |
| `--speaker-id` | Speaker diarization (requires `pyannote-audio` + `HF_TOKEN`) |
| `--vision-prompt "..."` | Custom prompt for vision annotation |
| `--no-punctuate` | Disable automatic punctuation restoration |
| `--chunk-seconds 30` | Chunk duration in seconds (default: 30) |
| `--max-videos 200` | Max videos to index from a channel/playlist |
| `--cookies-from-browser chrome` | Use browser cookies for age-restricted videos |
| `--show-transcripts` | Print transcripts during indexing |

**Example with multiple features:**

```bash
python embedclipfarm.py index "@channel" --vision gemini --whisper --speaker-id --max-videos 20
```

### Search

```bash
# Basic search
python embedclipfarm.py search "economic impact of automation"

# Search with more results
python embedclipfarm.py search "climate policy" --top-k 20

# Search and download matching clips
python embedclipfarm.py search "funny moment" --download ./clips

# Search visual content only
python embedclipfarm.py search "person at podium" --mode visual

# Filter by video or source type
python embedclipfarm.py search "query" --filter-video VIDEO_ID --filter-type whisper

# Export search results as SRT subtitles
python embedclipfarm.py search "query" --srt output.srt

# Compile matching clips into one video
python embedclipfarm.py search "query" --compile compilation.mp4
```

### Interactive shell

Loads the embedding model once, then lets you run multiple searches without reloading:

```bash
python embedclipfarm.py shell
```

### Download a clip

```bash
python embedclipfarm.py clip VIDEO_ID --start 10 --end 41
python embedclipfarm.py clip "https://youtube.com/watch?v=xyz" --start 60 --end 90 --output-dir ./clips
```

### Export index for the web UI

```bash
python embedclipfarm.py export --output index.json
```

### View transcripts

```bash
python embedclipfarm.py transcripts
python embedclipfarm.py transcripts --video VIDEO_ID
python embedclipfarm.py transcripts --save transcripts.txt
```

### Merge indexes

Combine multiple project indexes into one:

```bash
python embedclipfarm.py merge project1_db project2_db --output merged_db
```

### Local server for web UI clip downloads

```bash
python embedclipfarm.py serve --port 8899
```

## Web UI (`index.html`)

The web UI lets you search your indexed videos directly in the browser — no server needed.

### How to use

1. **Index videos** using the CLI (see above). This creates an `index.json` file in your project folder.
2. **Open the web UI** at [artificialnouveau.github.io/miniprojects/embedclipfarm](https://artificialnouveau.github.io/miniprojects/embedclipfarm/) (or open `index.html` locally).
3. **Load your `index.json`** — drag and drop it onto the page or click to browse.
4. **Search by meaning** — type a query and the UI embeds it client-side using [Transformers.js](https://huggingface.co/docs/transformers.js) (loads ~80MB model on first use).
5. **Browse results** — each result shows an embedded YouTube player at the matching timestamp, the transcript text, and a similarity score.
6. **Download clips** — click "Copy clip cmd" on any result to get a ready-to-paste terminal command, or use "Copy all clip commands" to grab them all at once.

### Score interpretation

- **Strong** (>= 0.3) — high confidence semantic match
- **Related** (0.15–0.3) — topically related
- Below 0.15 is filtered out as noise
