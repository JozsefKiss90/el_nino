"""
EL NIÑO VOICE BRIDGE — local STT/TTS server
============================================
Endpoints:
  GET  /health        -> {"ok": true, ...}
  POST /stt           -> multipart 'audio' (webm/ogg/wav) -> {"text": "..."}
  POST /tts           -> JSON {"text": "..."} -> audio/wav bytes
  GET  /              -> serves el_nino_jarvis_interface.html if present
                         (solves file:// mic restrictions: open http://127.0.0.1:8585/)

Run:
  uvicorn voice_bridge:app --host 127.0.0.1 --port 8585

Models are lazy-loaded on first use, so the server starts instantly.
First STT call downloads the Whisper model (~75 MB for base.en).
TTS needs a Piper voice in ./voices/ — see README_VOICE_BRIDGE.md.
"""
import io
import os
import wave
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ----------------------------------------------------------------- config
WHISPER_MODEL = os.environ.get("BRIDGE_WHISPER_MODEL", "base.en")   # tiny.en / base.en / small.en
PIPER_VOICE   = os.environ.get("BRIDGE_PIPER_VOICE", "en_GB-alan-medium")
VOICES_DIR    = Path(__file__).parent / "voices"
DASHBOARD     = Path(__file__).parent / "el_nino_jarvis_interface.html"

app = FastAPI(title="El Nino Voice Bridge")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # file:// pages send Origin: null — '*' covers it
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------- lazy models
_stt = None
_tts = None
_tts_err = None
_stt_err = None


def get_stt():
    global _stt, _stt_err
    if _stt is None and _stt_err is None:
        try:
            from faster_whisper import WhisperModel
            _stt = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        except Exception as e:  # noqa: BLE001
            _stt_err = str(e)
    return _stt


def get_tts():
    global _tts, _tts_err
    if _tts is None and _tts_err is None:
        try:
            from piper import PiperVoice
            onnx = VOICES_DIR / f"{PIPER_VOICE}.onnx"
            if not onnx.exists():
                _tts_err = f"voice model not found: {onnx} — see README_VOICE_BRIDGE.md"
                return None
            _tts = PiperVoice.load(str(onnx))
        except Exception as e:  # noqa: BLE001
            _tts_err = str(e)
    return _tts


# ----------------------------------------------------------------- routes
@app.get("/health")
def health():
    return {
        "ok": True,
        "stt_model": WHISPER_MODEL,
        "tts_voice": PIPER_VOICE,
        "stt_ready": _stt is not None,
        "tts_ready": _tts is not None,
        "stt_error": _stt_err,
        "tts_error": _tts_err,
    }


@app.post("/stt")
async def stt(audio: UploadFile = File(...)):
    model = get_stt()
    if model is None:
        return JSONResponse({"text": "", "error": _stt_err or "stt unavailable"}, status_code=500)
    data = await audio.read()
    # faster-whisper decodes webm/opus via PyAV — temp file in, text out
    suffix = Path(audio.filename or "clip.webm").suffix or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(data)
        tmp = f.name
    try:
        segments, _info = model.transcribe(tmp, language="en", vad_filter=True)
        text = " ".join(s.text.strip() for s in segments).strip()
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    return {"text": text}


class TTSIn(BaseModel):
    text: str


@app.post("/tts")
def tts(body: TTSIn):
    voice = get_tts()
    if voice is None:
        return JSONResponse({"error": _tts_err or "tts unavailable"}, status_code=500)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        voice.synthesize(body.text, w)
    return Response(content=buf.getvalue(), media_type="audio/wav")


@app.get("/")
def root():
    if DASHBOARD.exists():
        return FileResponse(str(DASHBOARD), media_type="text/html")
    return JSONResponse({"ok": True, "hint": "place el_nino_jarvis_interface.html next to voice_bridge.py to serve it here"})
