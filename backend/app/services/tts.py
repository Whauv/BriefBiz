from __future__ import annotations

import base64
from pathlib import Path

import httpx

from app.core.config import get_settings


class TextToSpeechService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.media_root = Path(__file__).resolve().parents[2] / "media" / "audio"
        self.media_root.mkdir(parents=True, exist_ok=True)

    async def synthesize_summary(self, *, article_id: int, text: str) -> str | None:
        if not text.strip():
            return None

        endpoint = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.settings.google_tts_key}"
        payload = {
            "input": {"text": text},
            "voice": {"languageCode": "en-US", "name": "en-US-Chirp3-HD-Achernar"},
            "audioConfig": {"audioEncoding": "MP3"},
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
        except Exception:
            return None

        audio_content = response.json().get("audioContent")
        if not audio_content:
            return None

        file_path = self.media_root / f"article-{article_id}.mp3"
        file_path.write_bytes(base64.b64decode(audio_content))
        return f"/media/audio/{file_path.name}"

