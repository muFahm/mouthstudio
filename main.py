import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from services.ai_service import extract_pitch_from_audio
from services.midi_builder import generate_midi_from_pitch


app = FastAPI(title="MouthStudio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    return {"message": "Welcome to MouthStudio API"}


@app.post("/api/v1/studio/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    allowed_types = {"audio/wav", "audio/m4a", "audio/x-wav"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload audio/wav or audio/m4a.",
        )

    extension = Path(file.filename or "upload.wav").suffix.lower()
    if extension not in {".wav", ".m4a"}:
        extension = ".wav" if file.content_type in {"audio/wav", "audio/x-wav"} else ".m4a"

    temp_audio_dir = Path("temp_audio")
    temp_audio_dir.mkdir(parents=True, exist_ok=True)

    temp_audio_path = temp_audio_dir / f"{uuid4()}{extension}"

    try:
        with temp_audio_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pitch_data = await extract_pitch_from_audio(str(temp_audio_path))
        midi_path = generate_midi_from_pitch(pitch_data, output_filename=str(uuid4()))

        return FileResponse(
            path=midi_path,
            media_type="audio/midi",
            filename=Path(midi_path).name,
        )
    finally:
        await file.close()
        if temp_audio_path.exists():
            temp_audio_path.unlink(missing_ok=True)