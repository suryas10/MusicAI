import os
import uuid
from functools import lru_cache
from pathlib import Path

import numpy as np
import scipy.io.wavfile
import torch
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

try:
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
except Exception:
    AutoProcessor = None
    MusicgenForConditionalGeneration = None


load_dotenv()

app = FastAPI(title="SonicCanvas API")

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1:5173,http://localhost:5173",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUDIO_DIR = Path("generated_audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/generated-audio", StaticFiles(directory=str(AUDIO_DIR)), name="generated-audio")


MODEL_ID = os.getenv("MUSICGEN_MODEL", "facebook/musicgen-small")
SAMPLE_RATE_FALLBACK = 32000


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def _load_musicgen():
    """Load local MusicGen model and cache it for subsequent requests."""
    if AutoProcessor is None or MusicgenForConditionalGeneration is None:
        return None, None, None

    processor = AutoProcessor.from_pretrained(MODEL_ID)
    model = MusicgenForConditionalGeneration.from_pretrained(MODEL_ID)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    return processor, model, device


@app.get("/")
async def index():
    return {
        "name": "SonicCanvas API",
        "status": "ok",
        "docs": "/docs",
        "model": MODEL_ID,
        "frontend": "Run SonicCanvas frontend at http://127.0.0.1:5173",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/generate-music")
async def generate_music(request: Request, prompt: str = Form(...), duration: int = Form(...)):
    prompt = prompt.strip()
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "Prompt is required."})

    duration = max(1, min(20, int(duration)))

    if _is_truthy(os.getenv("FORCE_DEMO_MODE")):
        return JSONResponse(
            content={
                "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                "mode": "demo",
                "message": "FORCE_DEMO_MODE is enabled.",
            }
        )

    processor, model, device = _load_musicgen()
    if processor is None or model is None or device is None:
        return JSONResponse(
            status_code=500,
            content={
                "error": "MusicGen dependencies are unavailable. Install requirements and restart.",
            },
        )

    try:
        inputs = processor(text=[prompt], padding=True, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Approximate mapping: higher duration -> more generated tokens.
        max_new_tokens = max(64, min(1024, duration * 50))

        with torch.no_grad():
            audio_values = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                guidance_scale=3.0,
            )

        audio_tensor = audio_values[0]
        if audio_tensor.ndim == 2:
            audio_tensor = audio_tensor[0]

        audio_np = audio_tensor.detach().cpu().numpy()
        audio_np = np.clip(audio_np, -1.0, 1.0)
        audio_int16 = (audio_np * 32767).astype(np.int16)

        sample_rate = getattr(model.config, "audio_encoder", None)
        if sample_rate is not None and hasattr(sample_rate, "sampling_rate"):
            sr = int(sample_rate.sampling_rate)
        else:
            sr = SAMPLE_RATE_FALLBACK

        filename = f"{uuid.uuid4().hex}.wav"
        file_path = AUDIO_DIR / filename
        scipy.io.wavfile.write(str(file_path), sr, audio_int16)

        file_url = str(request.base_url).rstrip("/") + f"/generated-audio/{filename}"
        return JSONResponse(
            content={
                "url": file_url,
                "mode": "live",
                "message": "Music generated successfully.",
            }
        )
    except Exception as exc:
        return JSONResponse(
            status_code=502,
            content={
                "error": f"Music generation failed: {exc}",
            },
        )
