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
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### 3) Frontend setup

```powershell
cd frontend
npm install
Copy-Item .env.example .env
cd ..
```

### 4) Run app

Terminal A (backend):

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

Terminal B (frontend):

```powershell
cd frontend
npm run dev
```

Open: [http://127.0.0.1:5173](http://127.0.0.1:5173)

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

## Notes

- First real generation can take longer due to model load/download.
- Generated audio is saved in generated_audio/ and excluded from git.
- Use FORCE_DEMO_MODE=true for fast frontend-only checks.

## License

MIT
