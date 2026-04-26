# 2026 WASP Lighthouse Hackathon Submission

# Python
pip install openai python-dotenv fastapi uvicorn llmshap requests opencv-python onnxruntime numpy huggingface_hub python-multipart

# Download model
hf download maelic/REACTPlusPlus_IndoorVG yolov8m/model.onnx --repo-type model --local-dir SGG_Bench

# Frontend
cd frontend && npm install

# Terminal 1:
cd frontend && npm run dev
# Terminal 2:
.venv/bin/python src/main.py

# .env file
Requires following content in an .env file:

OPENAI_API_KEY=your_openai_api_key

ELKS_USERNAME=your_46elks_username

ELKS_PASSWORD=your_46elks_password

RECIPIENT_PHONE_NUMBER=+46xxxxxxxxx

CAMERA_LOCATION=Living Room

FALL_LIKELIHOOD_THRESHOLD=%Threshold ex:50