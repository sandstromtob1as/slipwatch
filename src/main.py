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

    # Debug
    print(f"📸 Screenshot: {screenshot_path}")
    print(f"📸 Finns filen: {os.path.exists(screenshot_path) if screenshot_path else 'Ingen bild'}")

    # 2. Generera SMS
    incident.sms_message = generate_sms(incident)
    print(f"\n📱 SMS:\n{incident.sms_message}")

    # 3. Skicka SMS
    # send_sms(incident.sms_message)  # ANVÄND ENDAST FÖR DEMO!!
    send_dummy_sms(incident.sms_message)  # Dummy för utveckling

    print(f"\n✅ Incident skapad med ID: {incident.id}")
    return incident


if __name__ == "__main__":
    sys.path.append(os.path.dirname(__file__))
    from fall_detector import FallDetectionExplainer

    onnx_model_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'SGG_Bench', 'yolov8m', 'model.onnx')
    )

    if not os.path.exists(onnx_model_path):
        print(f"❌ ONNX-modellen saknas: {onnx_model_path}")
        sys.exit(1)

    print("🚀 Startar SlipWatch...")
    detector = FallDetectionExplainer(onnx_path=onnx_model_path)
    detector.run_webcam(on_fall_callback=on_fall_detected)