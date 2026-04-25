import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Read from JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "test_file.json")

with open(json_path, "r") as f:
    data = json.load(f)

# Convert to log string
triggered = ", ".join(data['triggered_by'])
log_string = (
    f"{data['timestamp']} | "
    f"{data['location']} | "
    f"triggered by: {triggered} | "
    f"last upright {data['last_upright_position']}"
)

# Get API key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize client
client = OpenAI(api_key=api_key)

# Make a request
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

# Print result
print(response.choices[0].message.content)