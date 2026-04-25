from src.fall_detector import run_detector
from src.llm_interpreter import generate_sms
from src.sms import send_sms
from src.server import post_to_dashboard

def on_fall_detected(data, screenshot):
    # 1. Generera SMS
    sms_text = generate_sms(data)
    
    # 2. Skicka SMS till anhörig
    send_sms(sms_text, screenshot)
    
    # 3. Skicka till dashboard
    post_to_dashboard(data, sms_text, screenshot)
    
    print(f"⚠️ Fall detekterat kl {data['timestamp']}")
    print(f"SMS: {sms_text}")

if __name__ == "__main__":
    run_detector(callback=on_fall_detected)