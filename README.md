# DougHub / InvokeAI Project

## Setup Instructions

### 1. Create and Activate Virtual Environment
```
python -m venv venv_invokeai
venv_invokeai\Scripts\activate
```

### 2. Install Requirements
```
pip install -r requirements.txt
```

### 3. Download SDXL and Inpainting Models
Run the provided script:
```
setup_models.bat
```
Or manually download the models as described in the script.

### 4. Copy and Edit Configs
Copy `InvokeAI/invokeai.example.yaml` to `InvokeAI/invokeai.yaml` and edit as needed for your environment.

### 5. Run the App
```
python app.py
```

---

## Notes
- Large files (models, outputs, databases, venv, uploads) are excluded from git for performance and storage reasons.
- If you need to re-download models, use the provided script or follow the Hugging Face links in the script.
- For more details, see comments in `.gitignore`. 