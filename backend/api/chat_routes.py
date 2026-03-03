from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

router = APIRouter()

import time
# Read Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

LAST_CALL = 0

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in environment variables")

# ---------- Request Model ----------
class ChatInput(BaseModel):
    message: str
    context: str = ""  # Optional soil / crop context


# ---------- Chat Endpoint ----------
@router.post("/chat")
async def chat_with_advisor(data: ChatInput):
    global LAST_CALL
    now = time.time()
    
    if now - LAST_CALL < 5: # 5 second cooldown
         raise HTTPException(
            status_code=429,
            detail="⏳ Please wait a few seconds before asking again."
        )
    
    LAST_CALL = now

    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini API Key not configured on server."
        )

    # ✅ UPDATED MODEL (Verified via debug script)
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.0-flash:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    system_prompt = """
You are an expert Agricultural Advisor for the 'Smart Soil' project.

Your role:
- Help farmers with crop, fertilizer, and irrigation advice
- Use soil data when provided
- Keep answers short, practical, and easy to understand

Rules:
1. Use soil values (N, P, K, pH, moisture) if given
2. Give actionable farming advice
3. Avoid technical jargon
4. If question is NOT about farming, politely redirect to agriculture
"""

    # Combine system + user input
    final_prompt = f"""
{system_prompt}

Soil / Farm Context:
{data.context}

Farmer Question:
{data.message}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": final_prompt}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Gemini API Error ({response.status_code}):", response.text)
            
            if response.status_code == 429:
                 raise HTTPException(
                    status_code=429,
                    detail="⚠️ Monthly/Daily AI Quota Exceeded. Please try again later."
                )
            
            raise HTTPException(
                status_code=500,
                detail=f"AI Provider Error ({response.status_code})."
            )

        result = response.json()

        # Safely extract text
        try:
            answer = (
                result["candidates"][0]
                ["content"]["parts"][0]
                ["text"]
            )
        except (KeyError, IndexError):
            answer = "Sorry, I couldn't generate a response."

        return {
            "response": answer.strip()
        }

    except requests.exceptions.RequestException as e:
        print("❌ Network Error:", e)
        raise HTTPException(
            status_code=500,
            detail="Failed to contact AI service."
        )
