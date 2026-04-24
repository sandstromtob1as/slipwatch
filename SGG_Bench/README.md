# SGG_Bench

This folder contains a simple tutorial for running the SGG benchmark pipeline locally. [SGG Benchmark](https://github.com/Maelic/SGG-Benchmark) is a collection of tools and models for the Scene Graph Generation (SGG) task. The model used in this demo is [REACT++](https://huggingface.co/maelic/REACTPlusPlus_PSG), a state-of-the-art SGG model trained on the PSG dataset.

For more information and troubleshooting, see the [SGG Benchmark repository](https://github.com/Maelic/SGG-Benchmark).

## Prerequisites

- Python 3.9+ (recommended)
- `pip` available in your Python installation
- A working webcam

## 1) Create and activate a virtual environment

Open a terminal in the `SGG_Bench` directory.

### Linux

```bash
cd SGG_Bench
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
cd SGG_Bench
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows (Command Prompt)

```bat
cd SGG_Bench
py -m venv .venv
.venv\Scripts\activate.bat
```

When the environment is active, your shell prompt usually shows `(.venv)`.

## 2) Install required packages

With the virtual environment activated, run:

```bash
pip install onnxruntime-gpu opencv-python numpy matplotlib
```

## 3) Download the ONNX model

Go to [Huggingface](https://huggingface.co/maelic/REACTPlusPlus_PSG/tree/main/yolo12m) and download the `react_pp_yolo12m.onnx` file. Place it in the `SGG_Bench` folder. Alternatively, you can run this command from the `SGG_Bench` folder (Linux/Mac):

```bash
wget "https://huggingface.co/maelic/REACTPlusPlus_PSG/resolve/main/yolo12m/react_pp_yolo12m.onnx?download=true" -O react_psg_yolo12m.onnx
```

And for other models (trained on VG150 and IndoorVG datasets), each command is in its own block so GitHub shows a separate copy button:

```bash
wget "https://huggingface.co/maelic/REACTPlusPlus_IndoorVG/resolve/main/yolov8m/model.onnx?download=true" -O react_indoorvg_yolov8m.onnx
```

```bash
wget "https://huggingface.co/maelic/REACTPlusPlus_VG150/resolve/main/yolo12m/model.onnx?download=true" -O react_vg150_yolo12m.onnx
```

More information about the models and their classes can be found in [MODELS.md](./MODELS.md).

## 4) Run the webcam demo

From the same `SGG_Bench` folder (and with the venv still active):

```bash
python webcam_demo.py --onnx_path react_psg_yolo12m.onnx --rel_conf 0.1 --box_conf 0.5 --provider CPUExecutionProvider # or CUDAExecutionProvider if you have a compatible GPU
```

## 5) Exit the virtual environment

When you are done:

```bash
deactivate
```

## Troubleshooting

- If `python` is not recognized on Windows, use `py` instead:
	- `py webcam_demo.py`
- If PowerShell blocks activation scripts, run:
	- `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
	- Then activate again: `.\.venv\Scripts\Activate.ps1`
- If the webcam does not open, close other apps that might be using the camera.