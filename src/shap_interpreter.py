import os
import json
import threading
from llmSHAP import DataHandler, BasicPromptCodec, ShapleyAttribution
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

    if not data:
        print("llmSHAP: no more features to analyze")
        return {}

    print(f"\nllmSHAP is analyzing {incident.id} with features: {data}")

    handler = DataHandler(data)

    prompt_codec = BasicPromptCodec(
        system="You are analyzing sensor data from an elderly fall detection system. "
               "The data contains observations about a person's position and movement. "
               "Determine which features most strongly indicate that a fall has occurred. "
               "Answer ONLY with: FALL CONFIRMED or FALSE ALARM, "
               "followed by one sentence explaining your reasoning."
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
        label = extract_label(val, data.get(key, key))
        scored.append((label, score))

    # Sortera högst till lägst
    scored.sort(key=lambda x: x[1], reverse=True)

    readable_attribution = {label: round(score, 4) for label, score in scored}

    output = {
        "incident_id": incident.id,
        "verdict": result.output,
        "attribution": readable_attribution,
        "features": data
    }

    # Spara till JSON
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    shap_dir = os.path.join(BASE_DIR, "falls_data")
    os.makedirs(shap_dir, exist_ok=True)
    shap_path = os.path.join(shap_dir, f"shap_{incident.id}.json")

    with open(shap_path, "w") as f:
        json.dump(output, f, indent=4)

    print(f"llmSHAP finished processing incident {incident.id}: {readable_attribution}")

    if on_complete:
        on_complete(output)

    return output


def run_shap_async(incident: FallIncident, on_complete=None):
    """Runs llmSHAP in a background thread so it doesn't block SMS sending."""
    thread = threading.Thread(
        target=run_shap,
        args=(incident,),
        kwargs={"on_complete": on_complete},
        daemon=True
    )
    thread.start()