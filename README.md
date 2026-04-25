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