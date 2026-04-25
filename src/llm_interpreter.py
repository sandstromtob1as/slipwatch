import os
from dotenv import load_dotenv
from openai import OpenAI
from models import FallIncident

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_sms(incident: FallIncident) -> str:
    triggered = ", ".join(incident.triggered_by)
    log_string = (
        f"{incident.timestamp} | "
        f"{incident.location} | "
        f"triggered by: {triggered} | "
        f"last upright {incident.last_upright_position}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a safety assistant for a senior monitoring system. "
                           "When given a sensor log, write a calm and clear 2-3 sentence "
                           "SMS message to a relative explaining what happened. "
                           "Be reassuring but honest. Do not be alarmist or dramatic. "
                           "Always mention the time and location of the incident."
            },
            {
                "role": "user",
                "content": log_string
            }
        ]
    )

    return response.choices[0].message.content