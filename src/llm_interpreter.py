import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
from models import FallIncident

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generate_sms(incident: FallIncident) -> str:
    triggered = ", ".join(incident.triggered_by)
    log_string = (
        f"{incident.timestamp} | "
        f"{incident.location} | "
        f"triggered by: {triggered} | "
        f"last upright {incident.last_upright_position}"
    )

    # Bygg meddelanden
    messages = [
        {
    "role": "system",
    "content": "You are a safety assistant for a senior monitoring system. "
               "You will receive an image and sensor data indicating a potential fall. "
               "Write a calm, clear 2-3 sentence SMS to a relative. "
               "Focus on the person — their position and any potential risk of injury. "
               "Briefly mention what room it appears to be based on the image. "
               "Always assume this COULD be a real fall — never dismiss it. "
               "Always mention the time in the format HH:MM:SS. "
               "End every message with: 'Please check on them as soon as possible.' "
               "Be caring but not overly dramatic."
        }
    ]

    # Om bild finns — skicka med den
    if incident.screenshot_path and os.path.exists(incident.screenshot_path):
        image_data = encode_image(incident.screenshot_path)
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                },
                {
                    "type": "text",
                    "text": log_string
                }
            ]
        })
    else:
        # Fallback utan bild
        messages.append({
            "role": "user",
            "content": log_string
        })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return response.choices[0].message.content