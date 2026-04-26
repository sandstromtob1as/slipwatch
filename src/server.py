import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores
incidents = []
shap_results = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(BASE_DIR, "falls_images")
os.makedirs(img_dir, exist_ok=True)
app.mount("/images", StaticFiles(directory=img_dir), name="images")


class IncidentPayload(BaseModel):
    id: int
    timestamp: str
    location: str
    triggered_by: list[str]
    last_upright_position: str
    screenshot_path: Optional[str] = None
    sms_message: Optional[str] = None


def add_incident(incident_dict: dict):
    """Called directly from main.py to add an incident."""
    if any(i["id"] == incident_dict.get("id") for i in incidents):
        print(f"Duplicate incident ignored: {incident_dict.get('id')}")
        return

    if incident_dict.get("screenshot_path"):
        filename = os.path.basename(incident_dict["screenshot_path"])
        incident_dict["image_url"] = f"http://localhost:8000/images/{filename}"
    else:
        incident_dict["image_url"] = None
    incident_dict["shap_ready"] = False
    incidents.append(incident_dict)


def add_shap_result(incident_id: int, result: dict):
    """Called from main.py when SHAP analysis is complete."""
    shap_results[incident_id] = result
    for i in incidents:
        if i["id"] == incident_id:
            i["shap_ready"] = True
            i["shap"] = result
            break
    print(f"SHAP result added for incident {incident_id}")


@app.post("/incidents")
def create_incident(payload: IncidentPayload):
    incident = payload.dict()
    add_incident(incident)
    return {"status": "ok", "id": incident["id"]}


@app.get("/incidents")
def get_incidents():
    return list(reversed(incidents))


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: int):
    for i in incidents:
        if i["id"] == incident_id:
            return i
    raise HTTPException(status_code=404, detail="Not found")


@app.get("/incidents/{incident_id}/shap")
def get_shap(incident_id: int):
    if incident_id in shap_results:
        return shap_results[incident_id]
    raise HTTPException(status_code=404, detail="SHAP not ready yet")


@app.get("/health")
def health():
    return {"status": "ok", "incidents": len(incidents)}