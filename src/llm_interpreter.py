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
        {"role": "system", "content": "You rewrite logs from a senior accident tracking system and your job is to inform relatives with a short message that something has happened"},
        {"role": "user", "content": "11:45 Person fell on ground, 11:48 No movement yet, 12:02 Person still on the ground"}
    ]
)

# Print result
print(response.choices[0].message.content)