# SonicCanvas

SonicCanvas is a prompt-to-music web app with a FastAPI backend and a modern React + Vite frontend.

## Highlights

- Local open-source MusicGen generation (no paid API required)
- Clean, responsive UI with interactive prompt helpers
- Play and download generated WAV output
- CORS-ready local dev setup
- Demo mode toggle for quick UI verification

## Tech Stack

- Backend: FastAPI, Transformers, PyTorch, SciPy
- Frontend: React, Vite, CSS animations

## Prerequisites

- Python 3.10+
- Node.js 18+
- Recommended RAM: 8 GB+
- Internet on first run to download model weights

## Quick Start

### 1) Clone and enter project

```powershell
git clone <your-repo-url>
cd MusicAI
```

### 2) Backend setup

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### 3) Pre-download the MusicGen model (IMPORTANT)

This step downloads the model (~1.5 GB) before running the app. This reduces the first API request time from **5-15 minutes to seconds**.

```powershell
# Still in venv
python download_model.py
```

This will:

- Download facebook/musicgen-small model weights
- Cache them in ~/.cache/huggingface/hub/
- Take 5-20 minutes depending on internet speed
- Display progress and confirmation when complete

**⚠️ Important:** Do this step before starting the app for instant first requests!

### 4) Frontend setup

```powershell
cd frontend
npm install
Copy-Item .env.example .env
cd ..
```

### 5) Run app

**Option A - Automatic (Recommended for Windows)**

Simply run the batch file:

```powershell
.\run.bat
```

This starts both backend and frontend in separate windows automatically.

**Option B - Manual (Two terminals)**

Terminal A (backend):

```powershell
venv\Scripts\activate
uvicorn app:app --reload
```

Terminal B (frontend):

```powershell
cd frontend
npm run dev
```

Then open: [http://127.0.0.1:5173](http://127.0.0.1:5173)

## Environment Configuration

### Backend .env

```env
LYRICS_MODEL=distilgpt2
MUSICGEN_MODEL=facebook/musicgen-small
FORCE_DEMO_MODE=false
ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

### Frontend frontend/.env

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API Endpoints

- GET / : API metadata
- GET /health : health status
- POST /generate-music : form data
  - prompt: string
  - duration: integer (1-20)

Response example:

```json
{
  "url": "http://127.0.0.1:8000/generated-audio/<id>.wav",
  "mode": "live",
  "message": "Music generated successfully."
}
```

## Model Details

- **Model**: facebook/musicgen-small (configurable via MUSICGEN_MODEL env var)
- **Cache**: ~/.cache/huggingface/hub/ (auto-managed by Hugging Face)
- **Download Size**: ~1.5 GB
- **Device**: Auto-detects GPU (CUDA), falls back to CPU
- **Pre-download**: Use `python download_model.py` for manual download before running app

## Notes

- Pre-download the model using `python download_model.py` before the first run for fastest subsequent requests
- After pre-download, the first real generation is instant; only initialization takes <1 second
- Generated audio is saved in generated_audio/ and excluded from git
- Use FORCE_DEMO_MODE=true for fast frontend-only checks without generation
- hf-transfer package enables fast parallel downloads from Hugging Face Hub

## License

MIT
