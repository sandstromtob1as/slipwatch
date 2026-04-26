import os
import re
import json
import threading
from llmSHAP import DataHandler, BasicPromptCodec, ShapleyAttribution
from llmSHAP.image import Image
from llmSHAP.llm import OpenAIInterface
from models import FallIncident


def clean_feature(item: str) -> str:
    """
    Cleans raw SGG-Bench relation strings into readable features.
    Example: "0_person - lying on - 1_floor: (triplet_score=0.05)" -> "lying on floor"
    """
    item = item.split(":")[0].strip()

    if " - " in item:
        parts = item.split(" - ")
        if len(parts) >= 3:
            relation = parts[1].strip()
            obj = parts[2].split("_", 1)[-1].strip() if "_" in parts[2] else parts[2].strip()
            item = f"{relation} {obj}"
        elif len(parts) == 2:
            item = parts[1].strip()

    item = item.replace("(inferred by bounding box)", "").strip()
    item = item.replace("floor-wood", "floor").strip()

    return item


def extract_score(val) -> float:
    """
    Safely extract a float score from llmSHAP attribution value.
    llmSHAP returns: {'value': 'feature name', 'score': 0.765}
    """
    if isinstance(val, dict):
        return float(val.get("score", 0.0))
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def extract_label(val, fallback: str) -> str:
    """Extract the feature label from llmSHAP attribution value."""
    if isinstance(val, dict):
        return val.get("value", fallback)
    return fallback


def extract_likelihood(output: str) -> float:
    """Find a numeric likelihood percentage in the model output."""
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", output)
    if match:
        value = float(match.group(1))
        return max(0.0, min(100.0, value))
    # Fallback: try to infer from common words
    lowered = output.lower()
    if "very likely" in lowered or "very probable" in lowered:
        return 90.0
    if "likely" in lowered or "probable" in lowered:
        return 70.0
    if "unlikely" in lowered or "not likely" in lowered:
        return 25.0
    if "almost certainly" in lowered or "definitely" in lowered:
        return 95.0
    return 50.0


def make_json_safe(value):
    if isinstance(value, Image):
        return str(value)
    if isinstance(value, dict):
        return {
            str(key): make_json_safe(val)
            for key, val in value.items()
        }
    if isinstance(value, list):
        return [make_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [make_json_safe(item) for item in value]
    return value


def run_shap(incident: FallIncident, on_complete=None) -> dict:
    """
    Runs llmSHAP attribution on a FallIncident.
    Explains which features contributed most to the fall decision.
    Calls on_complete(result) when done if provided.
    """

    # Bygg features från triggered_by — deduplicera
    seen = set()
    data = {}
    for item in incident.triggered_by:
        clean = clean_feature(item)
        if clean and clean not in seen:
            seen.add(clean)
            data[f"feature_{len(data)}"] = clean

    if incident.screenshot_path and os.path.exists(incident.screenshot_path):
        data["fall_image"] = Image(image_path=incident.screenshot_path)

    if not data:
        print("llmSHAP: no more features to analyze")
        return {}
    
    print(f"\nllmSHAP is analyzing {incident.id} with features: {list(data.keys())}")

    handler = DataHandler(data)

    prompt_codec = BasicPromptCodec(
        system="You are analyzing a possible fall from a security camera image and a short set of observations. "
               "Use the image as the primary evidence and the observations only for context. "
               "Answer with a single likelihood percentage between 0 and 100, and one short explanation. "
               "Example: 'LIKELIHOOD: 82% - The person is lying on the floor with limbs extended, indicating a fall.' "
               "Do not output any additional commentary."
    )

    llm = OpenAIInterface(model_name="gpt-4o-mini")
    shap = ShapleyAttribution(
        model=llm,
        data_handler=handler,
        prompt_codec=prompt_codec,
        use_cache=True
    )

    result = shap.attribution()

    # Extrahera scores och labels
    scored = []
    for key, val in result.attribution.items():
        score = extract_score(val)
        label = extract_label(val, str(data.get(key, key)))
        scored.append((label, score))

    # Sortera högst till lägst
    scored.sort(key=lambda x: x[1], reverse=True)

    readable_attribution = {label: round(score, 4) for label, score in scored}
    likelihood = extract_likelihood(result.output)

    output = {
        "incident_id": incident.id,
        "verdict": result.output,
        "fall_likelihood_percent": round(likelihood, 2),
        "attribution": readable_attribution,
        "features": data
    }

    safe_output = make_json_safe(output)

    # Spara till JSON
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    shap_dir = os.path.join(BASE_DIR, "falls_data")
    os.makedirs(shap_dir, exist_ok=True)
    shap_path = os.path.join(shap_dir, f"shap_{incident.id}.json")

    with open(shap_path, "w") as f:
        json.dump(safe_output, f, indent=4)

    print(f"llmSHAP finished processing incident {incident.id}: {readable_attribution}")

    if on_complete:
        on_complete(safe_output)

    return safe_output


def run_shap_async(incident: FallIncident, on_complete=None):
    """Runs llmSHAP in a background thread so it doesn't block SMS sending."""
    thread = threading.Thread(
        target=run_shap,
        args=(incident,),
        kwargs={"on_complete": on_complete},
        daemon=True
    )
    thread.start()