import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_sms(message: str) -> None:
    requests.post(
        "https://api.46elks.com/a1/sms",
        auth=(os.getenv("ELKS_USERNAME"), os.getenv("ELKS_PASSWORD")),
        data={
            "from": "SlipWatch",
            "to": os.getenv("RECIPIENT_PHONE_NUMBER"),
            "message": message
        }
    )
    print("✅ SMS skickat!")

if __name__ == "__main__":
    response = requests.post(
        "https://api.46elks.com/a1/sms",
        auth=(os.getenv("ELKS_USERNAME"), os.getenv("ELKS_PASSWORD")),
        data={
            "from": "SlipWatch",
            "to": os.getenv("RECIPIENT_PHONE_NUMBER"),
            "message": "Mamma: Hjälp mig!"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Svar: {response.text}")