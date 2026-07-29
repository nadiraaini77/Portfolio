"""
All calls to OpenRouter's Vision API live here. Nothing else in the codebase
should import `requests` for AI calls — this is the single seam, which makes
it easy to swap models/providers later or mock out in tests.
"""
import base64
import json
import re
from typing import Optional

import requests

from backend import config
from backend.schemas import ClassificationResult, KTPExtraction

CLASSIFICATION_PROMPT = (
    "Apakah gambar ini merupakan KTP (Kartu Tanda Penduduk) Indonesia yang asli, "
    "bukan dokumen lain seperti SIM, STNK, struk belanja, atau foto biasa?\n"
    "Jawab HANYA dengan JSON tanpa teks lain, tanpa markdown code fence, dalam format:\n"
    '{"is_ktp": true} atau {"is_ktp": false}'
)

OCR_PROMPT = (
    "Ekstrak seluruh informasi dari gambar KTP Indonesia ini. "
    "Jawab HANYA dengan JSON tanpa teks lain, tanpa markdown code fence, "
    "menggunakan persis struktur berikut (isi string kosong \"\" jika field "
    "tidak terbaca/tidak ada):\n"
    "{\n"
    '  "nik": "", "nama": "", "tempat_tgl_lahir": "", "jenis_kelamin": "",\n'
    '  "agama": "", "alamat": "", "rt": "", "rw": "", "kelurahan": "",\n'
    '  "kecamatan": "", "status_perkawinan": "", "pekerjaan": "",\n'
    '  "kewarganegaraan": "", "berlaku_hingga": ""\n'
    "}"
)


class OpenRouterError(RuntimeError):
    pass


def encode_image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def _guess_mime_type(image_bytes: bytes) -> str:
    if image_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if image_bytes[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"  # reasonable default


def _extract_json_block(text: str) -> dict:
    """Models occasionally wrap JSON in markdown fences or add stray text
    despite instructions. This pulls out the first balanced {...} block."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise OpenRouterError(f"No JSON object found in model response: {text[:200]!r}")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise OpenRouterError(f"Model response was not valid JSON: {e}\nRaw: {text[:200]!r}")


def _call_vision(prompt: str, image_bytes: bytes, model: str) -> str:
    config.require_api_key()
    mime = _guess_mime_type(image_bytes)
    b64 = encode_image_to_base64(image_bytes)

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            }
        ],
        "temperature": 0,
    }
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": config.APP_SITE_URL,
        "X-Title": config.APP_NAME,
    }

    try:
        resp = requests.post(
            f"{config.OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=config.REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as e:
        raise OpenRouterError(f"Request to OpenRouter failed: {e}")

    if resp.status_code != 200:
        raise OpenRouterError(f"OpenRouter returned {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise OpenRouterError(f"Unexpected OpenRouter response shape: {data}")


def classify_document(image_bytes: bytes, model: Optional[str] = None) -> ClassificationResult:
    model = model or config.MODEL_CLASSIFICATION
    raw = _call_vision(CLASSIFICATION_PROMPT, image_bytes, model)
    parsed = _extract_json_block(raw)
    return ClassificationResult(is_ktp=bool(parsed.get("is_ktp", False)), raw_response=raw)


def extract_ktp_fields(image_bytes: bytes, model: Optional[str] = None) -> KTPExtraction:
    model = model or config.MODEL_OCR
    raw = _call_vision(OCR_PROMPT, image_bytes, model)
    parsed = _extract_json_block(raw)
    # KTPExtraction defaults every field to "", so unexpected/missing keys
    # from the model never crash this — they just come back empty.
    known_fields = set(KTPExtraction.model_fields.keys())
    cleaned = {k: str(v) if v is not None else "" for k, v in parsed.items() if k in known_fields}
    return KTPExtraction(**cleaned)
