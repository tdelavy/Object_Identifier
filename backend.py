from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.post("/session")
def create_session():
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "realtime=v1"
    }

    data = {
        "model": "gpt-4o-realtime-preview-2024-12-17",
        "voice": "shimmer",
        "instructions": "You are a helpful assistant that describes the main object in a received image and gives a short response (2–3 sentences).",
        "input_audio_transcription": {"model": "whisper-1"},
        "turn_detection": {"type": "server_vad"}
    }

    response = requests.post("https://api.openai.com/v1/realtime/sessions", headers=headers, json=data)
    session = response.json()
    
    print("DEBUG OpenAI session response:", session)  # ✅ ADD THIS

    return {
        "client": {
            "token": session["client_secret"]["value"],
            "session_id": session["id"]
        }
    }

@app.post("/client-offer")
async def send_offer(request: Request):
    body = await request.json()
    session_id = body["session_id"]
    token = body["token"]
    sdp = body["sdp"]

    patch_headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "realtime=v1",
        "OpenAI-Client-Secret": token
    }

    patch_data = {
        "offer": {
            "type": "offer",
            "sdp": sdp
        }
    }

    res = requests.patch(f"https://api.openai.com/v1/realtime/sessions/{session_id}/client",
                         headers=patch_headers, json=patch_data)
    return res.json()
