from models import FallIncident
from llm_interpreter import generate_sms
from sms_sender import send_sms, send_dummy_sms

def on_fall_detected(data: dict, screenshot_path: str = None) -> FallIncident:
    # 1. Skapa incident
    incident = FallIncident(
        timestamp=data["timestamp"],
        location=data["location"],
        triggered_by=data["triggered_by"],
        last_upright_position=data["last_upright_position"],
        screenshot_path=screenshot_path
    )

    # 2. Generera SMS
    incident.sms_message = generate_sms(incident)
    print(f"\nGenerated SMS message:\n{incident.sms_message}")

    # 3. Skicka SMS
    #send_sms(incident)
    send_dummy_sms(incident.sms_message)

    return incident

# Test
if __name__ == "__main__":
    test_data = {
        "timestamp": "14:32:10",
        "location": "bathroom",
        "triggered_by": [
            "person lying on floor",
            "no movement 95 seconds",
            "sudden position change",
            "hard tile floor nearby"
        ],
        "last_upright_position": "14:30:15"
    }

    incident = on_fall_detected(test_data)
    print(f"\n✅ Incident skapad med ID: {incident.id}")