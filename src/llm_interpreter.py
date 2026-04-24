from openai import OpenAI
from dotenv import load_dotenv
import json
import os

# Sökvägar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

# Läs in JSON
json_path = os.path.join(BASE_DIR, "test_file.json")
with open(json_path, "r") as f:
    data = json.load(f)

# Ta bort timestamp
timestamp = data.pop("timestamp")

# Anropa ChatGPT
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Du är ett säkerhetssystem för äldre personer. "
                       "Skriv ett kort SMS-meddelande till en anhörig "
                       "som förklarar vad som hänt. Max 3 meningar."
        },
        {
            "role": "user",
            "content": f"Tidpunkt: {timestamp}\nData: {json.dumps(data, ensure_ascii=False)}"
        }
    ]
)

print("\n### SMS-MEDDELANDE ###")
print(response.choices[0].message.content)