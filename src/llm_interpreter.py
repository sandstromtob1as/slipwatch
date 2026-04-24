import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

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
        {"role": "user", "content": "12:03:45 | person lying on floor | no movement | 90 seconds | sudden position change | kitchen | hard floor tiles | last upright 12:01:55"}
    ]
)

# Print result
print(response.choices[0].message.content)