# PodiumAI — AI Public Speaking Coach

Upload a video of yourself speaking and receive instant coaching: filler-word counts, posture analysis, eye contact percentage, speech pacing, and personalised AI feedback.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + TailwindCSS (Vite) |
| Backend | Python 3.11 + Flask |
| Database | SQLite via SQLAlchemy |
| CV / ML | MediaPipe, OpenCV, librosa, openai-whisper |
| AI Coach | OpenRouter API (Claude 3.5 Sonnet) |

---

## Project Structure

```
podiumai/
├── frontend/                   # Vite + React + TS + Tailwind
│   ├── src/
│   │   ├── components/         # VideoUpload, MetricsDisplay, FeedbackCard, ScoreCard
│   │   ├── pages/              # Home, History, SessionDetail
│   │   └── App.tsx             # Router root
│   ├── package.json
│   └── vite.config.ts
└── backend/
    ├── app.py                  # Flask entry point
    ├── models.py               # Session + Metrics ORM models
    ├── database.py             # SQLite initialisation
    ├── coach.py                # OpenRouter coaching feedback
    ├── routes/
    │   ├── upload.py           # POST /api/upload
    │   └── sessions.py         # GET /api/sessions, GET /api/sessions/:id
    ├── pipeline/
    │   ├── extract_frames.py   # OpenCV frame sampling
    │   ├── pose_analysis.py    # MediaPipe Pose + Hands + Face Mesh
    │   ├── audio_analysis.py   # Whisper transcription + librosa pitch analysis
    │   └── get_metrics.py      # Pipeline orchestrator → metrics dict
    └── requirements.txt
```

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- ffmpeg (required by Whisper for audio extraction): `brew install ffmpeg`

### 1. Backend

```bash
cd podiumai/backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env .env.local               # .env already contains the OpenRouter key
# Edit .env.local if you need to change the model or DB path

# Start the Flask dev server
python app.py
# → Running on http://localhost:5000
```

### 2. Frontend

```bash
cd podiumai/frontend

npm install

npm run dev
# → Running on http://localhost:5173
```

The Vite dev server proxies all `/api/*` requests to `http://localhost:5000`, so no CORS configuration is needed during development.

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload a video file (multipart/form-data, field: `video`) |
| `GET` | `/api/sessions` | List all sessions (newest first) |
| `GET` | `/api/sessions/:id` | Get a single session with metrics |

---

## Environment Variables (backend/.env)

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `OPENROUTER_BASE_URL` | OpenRouter endpoint (default: `https://openrouter.ai/api/v1`) |
| `OPENROUTER_MODEL` | Model to use (default: `anthropic/claude-3.5-sonnet`) |
| `DATABASE_URL` | SQLAlchemy DB URL (default: `sqlite:///podiumai.db`) |
| `UPLOAD_FOLDER` | Where uploaded videos are stored (default: `uploads/`) |

---

## Development Status

The project skeleton is fully scaffolded. The following pipeline modules are **not yet implemented** (each has `TODO` comments and a `NotImplementedError`):

- `pipeline/extract_frames.py` — OpenCV frame sampling
- `pipeline/pose_analysis.py` — MediaPipe body-language metrics
- `pipeline/audio_analysis.py` — Whisper + librosa audio metrics
- `pipeline/get_metrics.py` — Pipeline orchestrator

The upload route currently saves the file and creates a `Session` row but returns a `202 Accepted` with a placeholder message until the pipeline is wired up.
