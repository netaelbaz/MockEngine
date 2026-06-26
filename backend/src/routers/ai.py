"""AI-powered mock data generation router using Gemini REST API."""

import json
import os
import httpx
from fastapi import APIRouter, HTTPException
from src.schemas import AIGenerateRequest, AIGenerateResponse

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

SYSTEM_PROMPT = (
    "You are a mock API response data generator for software testing. "
    "Given a description, return ONLY a valid JSON object representing the mock HTTP response body. "
    "Rules:\n"
    "- Output ONLY raw JSON (no markdown, no code blocks, no explanations)\n"
    "- Generate realistic-looking test data\n"
    "- Always return a JSON object ({}), never a bare JSON array\n"
    "- If the data is a list, wrap it with a meaningful semantic key (e.g. {\"users\": [...]} not {\"items\": [...]})\n"
    "- Do NOT set status codes, HTTP headers, delays, or any response metadata\n"
    "- Do NOT respond conversationally or acknowledge the request\n"
    "- If the request is unrelated to generating data, return exactly: {}"
)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


@router.post("/generate-mock-data", response_model=AIGenerateResponse)
def generate_mock_data(request: AIGenerateRequest) -> AIGenerateResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="AI features are not configured")

    context_hints = ""
    if request.url_pattern:
        context_hints += f" The endpoint is {request.url_pattern}."
    if request.method:
        context_hints += f" The HTTP method is {request.method}."

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": request.prompt + context_hints}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{GEMINI_URL}?key={api_key}", json=payload)
        resp.raise_for_status()
        body = resp.json()
        raw = body["candidates"][0]["content"]["parts"][0]["text"].strip()
        mock_data = json.loads(raw)
        if isinstance(mock_data, list):
            mock_data = {"items": mock_data}
        elif not isinstance(mock_data, dict):
            mock_data = {}
    except (json.JSONDecodeError, KeyError, IndexError, ValueError):
        mock_data = {}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {exc.response.status_code}")
    except Exception:
        mock_data = {}

    return AIGenerateResponse(mock_data=mock_data)
