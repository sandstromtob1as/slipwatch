from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class FallIncident:
    # Från SGG-Bench
    timestamp: str
    location: str
    triggered_by: list[str]
    last_upright_position: str
    
    # Från screenshot
    screenshot_path: Optional[str] = None
    
    # Från ChatGPT
    sms_message: Optional[str] = None
    
    # Autogenererat
    id: int = field(default_factory=lambda: int(datetime.now().timestamp()))