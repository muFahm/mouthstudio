import os
from pathlib import Path

import requests


HF_MODEL_URL = "https://api-inference.huggingface.co/models/spotify/basic-pitch"
REQUEST_TIMEOUT_SECONDS = 60


async def extract_pitch_from_audio(file_path: str) -> dict:
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_API_KEY environment variable is not set")

    audio_path = Path(file_path)
    if not audio_path.exists() or not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/octet-stream",
    }

    with audio_path.open("rb") as audio_file:
        audio_bytes = audio_file.read()

    try:
        response = requests.post(
            HF_MODEL_URL,
            headers=headers,
            data=audio_bytes,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise TimeoutError("Request to Hugging Face API timed out") from exc
    except requests.RequestException as exc:
        status_code = exc.response.status_code if exc.response is not None else None
        error_body = exc.response.text if exc.response is not None else str(exc)
        raise RuntimeError(
            f"Hugging Face API request failed (status={status_code}): {error_body}"
        ) from exc

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError("Hugging Face API returned a non-JSON response") from exc