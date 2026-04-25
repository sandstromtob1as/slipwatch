import json
import time
import os
import sys
from models import FallIncident
from llm_interpreter import generate_sms
from sms_sender import send_sms, send_dummy_sms

def on_fall_detected(fall_data: dict, screenshot_path: str = None) -> FallIncident:
    
    # Bygg triggered_by från event history
    triggered_by = []
    for event in fall_data["situation_description"]["during_fall"]:
        activity = event["activity"]
        if isinstance(activity, list):
            triggered_by.extend(activity)
        else:
            triggered_by.append(activity)

    # Hämta senaste kända position innan fallet
    leading_up = fall_data["situation_description"].get("leading_up_to_fall", [])
    last_upright = leading_up[-1]["timestamp"] if leading_up else "unknown"

    # 1. Skapa incident
    incident = FallIncident(
        timestamp=time.strftime("%H:%M:%S"),
        location="unknown",
        triggered_by=triggered_by[:4],
        last_upright_position=last_upright,
        screenshot_path=screenshot_path
    )

    # 2. Generera SMS
    incident.sms_message = generate_sms(incident)
    print(f"\n📱 SMS:\n{incident.sms_message}")

    # 3. Skicka SMS
    #send_sms(incident.sms_message) #ANVÄND ENDAST FÖR DEMO!!
    send_dummy_sms(incident.sms_message) #Dummy sms för utveckling

    print(f"\n✅ Incident skapad med ID: {incident.id}")
    return incident


# Test med JSON-fil
if __name__ == "__main__":
    # Om du vill testa med en riktig JSON från detector.py:
    # .venv/bin/python src/main.py src/falls_data/fall_detected_XXXX.json

    if len(sys.argv) > 1:
        json_path = sys.argv[1]
        with open(json_path, "r") as f:
            fall_data = json.load(f)
        on_fall_detected(fall_data)

    else:
        # Fallback testdata
        fall_data = {
            "situation_description": {
                "leading_up_to_fall": [
                    {
                        "timestamp": "2025-01-01 14:30:15",
                        "activity": "person standing near kitchen counter"
                    }
                ],
                "during_fall": [
                    {
                        "timestamp": "2025-01-01 14:32:10",
                        "activity": "person lying on floor"
                    },
                    {
                        "timestamp": "2025-01-01 14:32:15",
                        "activity": "no movement detected"
                    }
                ]
            }
        }
        on_fall_detected(fall_data, screenshot_path=None)