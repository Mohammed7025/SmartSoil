from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import asyncio
from dotenv import load_dotenv
import time

from mistralai import Mistral

# Load environment variables from .env
load_dotenv()

router = APIRouter()

# Read Mistral API key
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    print("❌ MISTRAL_API_KEY not found in environment variables")

# Initialize Mistral Client
client = None
if MISTRAL_API_KEY:
    try:
        client = Mistral(api_key=MISTRAL_API_KEY)
    except Exception as e:
        print(f"❌ Failed to initialize Mistral Client: {e}")

chat_memory = {}

# ---------- Request Model ----------
class ChatInput(BaseModel):
    message: str
    user_id: str = "default_user"
    context: str = ""

# ---------- Chat Endpoint ----------
@router.post("/chat")
async def chat_with_advisor(data: ChatInput):
    if not client:
        raise HTTPException(
            status_code=500,
            detail="Mistral AI Client not initialized."
        )

    system_prompt = """
You are AgroBot, an agricultural assistant that helps with crops, soil health, irrigation, and fertilizer advice.
Keep responses short and clear.

Rules:
1. Max 3 sentences per response. 
2. Ask ONLY one question at a time to collect data.
3. Be direct and farmer-friendly.
4. You can communicate in any language. Always reply in the user's language.
"""

    # Initialize memory for user
    if data.user_id not in chat_memory:
        chat_memory[data.user_id] = [
            {"role": "system", "content": system_prompt}
        ]

    # Add new user message
    chat_memory[data.user_id].append(
        {"role": "user", "content": data.message}
    )

    # Limit memory to avoid large prompts (last 10 + system prompt)
    if len(chat_memory[data.user_id]) > 11:
        chat_memory[data.user_id] = [chat_memory[data.user_id][0]] + chat_memory[data.user_id][-10:]

    async def generate_stream():
        try:
            stream = client.chat.stream(
                model="mistral-small-latest",
                temperature=0.4,
                messages=chat_memory[data.user_id]
            )

            full_response = ""
            for chunk in stream:
                if chunk.data.choices[0].delta.content is not None:
                    content = chunk.data.choices[0].delta.content
                    full_response += content
                    yield content

            # Save assistant reply
            chat_memory[data.user_id].append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "rate limit" in error_msg or "quota" in error_msg:
                yield "⚠️ AgroBot is a little busy right now (Quota Reached). Please wait a few seconds and try again."
            else:
                print(f"❌ Chat Error: {e}")
                yield "Sorry, I'm having trouble connecting to my AI brain. Please try again later."

    return StreamingResponse(generate_stream(), media_type="text/plain")
