import time
import os
import sys
import threading
import uvicorn
from dotenv import load_dotenv

from models import FallIncident
from llm_interpreter import generate_sms
from sms_sender import send_sms, send_dummy_sms
from server import app, add_incident, add_shap_result
from shap_interpreter import run_shap

load_dotenv()

threshold_raw = os.getenv('FALL_LIKELIHOOD_THRESHOLD', '65')
FALL_LIKELIHOOD_THRESHOLD = float(threshold_raw)
if FALL_LIKELIHOOD_THRESHOLD < 1.0:
    FALL_LIKELIHOOD_THRESHOLD *= 100.0
FALL_LIKELIHOOD_THRESHOLD = max(0.0, min(100.0, FALL_LIKELIHOOD_THRESHOLD))

# Relations that are not relevant for fall detection
IRRELEVANT_RELATIONS = ['wearing', 'holding', 'carrying', 'looking at', 'using', 'reading']


def clean_triggered_by(raw: list[str]) -> list[str]:
    """
    Filters and deduplicates triggered_by features.
    Removes irrelevant relations and duplicates.
    """
    filtered = [
        t for t in raw
        if not any(irr in t.lower() for irr in IRRELEVANT_RELATIONS)
    ]
    # Deduplicate while preserving order
    return list(dict.fromkeys(filtered))[:4]


def post_to_dashboard(incident: FallIncident):
    """Adds incident directly to in-memory store via server module."""
    add_incident({
        "id": incident.id,
        "timestamp": incident.timestamp,
        "location": incident.location,
        "triggered_by": incident.triggered_by,
        "last_upright_position": incident.last_upright_position,
        "screenshot_path": incident.screenshot_path,
        "sms_message": incident.sms_message,
    })
    print("Incident added to dashboard")


def on_fall_detected(fall_data: dict, screenshot_path: str = None) -> FallIncident:

    # Bygg triggered_by från event history
    raw_triggered = []
    for event in fall_data["situation_description"]["during_fall"]:
        activity = event["activity"]
        if isinstance(activity, list):
            raw_triggered.extend(activity)
        else:
            raw_triggered.append(activity)

    # Filtrera och deduplicera
    triggered_by = clean_triggered_by(raw_triggered)

    # Hämta senaste kända position innan fallet
    leading_up = fall_data["situation_description"].get("leading_up_to_fall", [])
    last_upright = leading_up[-1]["timestamp"] if leading_up else "unknown"

    # 1. Skapa incident
    incident = FallIncident(
        timestamp=time.strftime("%H:%M:%S"),
        location=os.getenv("CAMERA_LOCATION", "Living Room"),
        triggered_by=triggered_by,
        last_upright_position=last_upright,
        screenshot_path=screenshot_path
    )

    # 2. Kör llmSHAP först och vänta på sannolikheten
    shap_result = run_shap(incident)
    if not shap_result:
        print(f"⚠️ SHAP-analys misslyckades för incident {incident.id}. Avbryter fallregistrering.")
        return incident

    likelihood = shap_result.get("fall_likelihood_percent", 0.0)
    print(f"🔎 Fall likelihood: {likelihood}%")

    if likelihood < FALL_LIKELIHOOD_THRESHOLD:
        print(
            f"⚠️ Håller inte tröskeln ({likelihood}% < {FALL_LIKELIHOOD_THRESHOLD}%). "
            "Inga fallalarm eller dashboard-rapport skickas."
        )
        return incident

    # 3. Generera SMS
    incident.sms_message = generate_sms(incident)
    #print(f"\nText message:\n{incident.sms_message}")

    # 4. Skicka SMS
    # send_sms(incident.sms_message)  # ANVÄND ENDAST FÖR DEMO!!
    send_dummy_sms(incident.sms_message)  # Dummy för utveckling

    # 5. Skicka till dashboard
    post_to_dashboard(incident)
    add_shap_result(incident.id, shap_result)

    print(f"\nIncident created with ID: {incident.id}")
    return incident


if __name__ == "__main__":
    sys.path.append(os.path.dirname(__file__))
    from fall_detector import FallDetectionExplainer

    onnx_model_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'SGG_Bench', 'yolov8m', 'model.onnx')
    )

    if not os.path.exists(onnx_model_path):
        print(f"ERROR: the ONNX-model is missing: {onnx_model_path}")
        sys.exit(1)

    # Starta FastAPI i bakgrunden
    server_thread = threading.Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": "0.0.0.0", "port": 8000, "log_level": "warning"},
        daemon=True
    )
    server_thread.start()
    print("Dashboard API is running on http://localhost:8000")

    # Starta detektor
    print("Starting SlipWatch...")
    detector = FallDetectionExplainer(onnx_path=onnx_model_path)
    detector.run_webcam(on_fall_callback=on_fall_detected)