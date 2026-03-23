# 🤖 Model Inference Demo App

Interactive demo application for comparing **pretrained** vs **fine-tuned** models using FastAPI backend and Streamlit frontend.

## 📋 Features

- **Two Model Types:**
  - 🔤 **T5**: Text simplification and lexical substitution
  - 💻 **CodeGen**: Code generation and completion

- **Version Comparison:**
  - **V1 (T5)**: Pretrained t5-base from Hugging Face (untrained for lexical task)
  - **V2 (T5)**: Fine-tuned flan-t5-lexical (trained for lexical simplification)
  - **V1 (CodeGen)**: Random weights (untrained - generates nonsense)
  - **V2 (CodeGen)**: Pretrained Salesforce/codegen-350M-mono (trained model)

- **Interactive UI:**
  - Single model inference mode
  - Side-by-side comparison mode
  - Real-time metrics (inference time, output length)
  - Adjustable parameters (temperature, max_length, etc.)

- **RESTful API:**
  - `/predict/flan-t5` - FLAN-T5 inference
  - `/predict/codegen` - CodeGen inference
  - `/compare` - Compare v1 vs v2
  - `/health` - Health check
  - `/models` - Model information

## 🏗️ Architecture

```
demo-app/
├── backend/
│   ├── api.py              # FastAPI server
│   ├── model_manager.py    # Model loading & inference
│   └── requirements.txt
│
├── frontend/
│   ├── app.py              # Streamlit UI
│   └── requirements.txt
│
├── models/                 # (Optional) Local model storage
├── start_backend.sh        # Quick start script
└── start_frontend.sh       # Quick start script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- 8GB+ RAM (16GB recommended)
- CUDA-compatible GPU (optional, for faster inference)
- [uv](https://github.com/astral-sh/uv) (fast Python package installer)

### Step 1: Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Step 2: Install Dependencies

#### Backend
```bash
cd backend
uv sync
```

#### Frontend
```bash
cd frontend
uv sync
```

### Step 3: Start the Application

#### Option A: Using Scripts (Recommended)
```bash
# Terminal 1 - Start Backend
./start_backend.sh

# Terminal 2 - Start Frontend
./start_frontend.sh
```

#### Option B: Manual Start
```bash
# Terminal 1 - Backend API
cd backend
python api.py

# Terminal 2 - Frontend UI
cd frontend
streamlit run app.py
```

### Step 4: Access the Application

- **Frontend UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## 📝 Usage Guide

### Single Model Mode

1. Select model type (FLAN-T5 or CodeGen)
2. Choose version (v1 pretrained or v2 fine-tuned)
3. Adjust parameters (max_length, temperature, etc.)
4. Enter your input text/prompt
5. Click "Generate" to see results

### Comparison Mode

1. Select model type (FLAN-T5 or CodeGen)
2. Enter your input text/prompt
3. Click "Compare Models"
4. View side-by-side results with metrics

### Example Prompts

**T5 (Lexical Simplification):**
- `The weather today is extraordinarily magnificent.`
- `The proliferation of artificial intelligence has revolutionized computational linguistics.`
- `This medication can ameliorate the symptoms significantly.`

**CodeGen:**
- `def binary_search(arr, target):`
- `# Function to check if number is prime`
- `class LinkedList:`

## 🔧 Configuration

### Model Paths

By default, the app uses:
- **T5 v1**: `t5-base` (loaded from Hugging Face)
- **T5 v2**: `../flan-t5-lexical` (your fine-tuned model)
- **CodeGen v1**: Random weights from `Salesforce/codegen-350M-mono` config
- **CodeGen v2**: Pretrained `Salesforce/codegen-350M-mono`

To customize model paths, edit `backend/model_manager.py`:

```python
# In load_flan_t5_v2()
model_path = "/path/to/your/flan-t5-model"
```

### API Configuration

Edit `.env` file (copy from `.env.example`):
```bash
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=8501
DEVICE=cuda  # or 'cpu'
```

## 🧪 API Testing

### Using cURL

```bash
# T5 Inference (Lexical Simplification)
curl -X POST "http://localhost:8000/predict/flan-t5" \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "The weather is extraordinarily magnificent.",
    "model_version": "v1",
    "max_length": 128,
    "temperature": 1.0
  }'

# Compare Models
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "def reverse_string(s):",
    "model_type": "codegen",
    "max_length": 128,
    "temperature": 0.7
  }'
```

### Using Python

```python
import requests

# T5 inference
response = requests.post(
    "http://localhost:8000/predict/flan-t5",
    json={
        "input_text": "The weather is magnificent.",
        "model_version": "v2",
        "max_length": 128
    }
)
print(response.json())
```

## 📊 Model Information

Check loaded models and their specifications:

```bash
curl http://localhost:8000/models
```

Response includes:
- Total parameters
- Trainable parameters
- Model type
- Device (CPU/GPU)

## 🐛 Troubleshooting

### Backend won't start
- **Issue**: Models failing to load
- **Solution**: Check model paths in `model_manager.py`, ensure models exist

### Out of memory errors
- **Solution**: Reduce batch size, use CPU instead of GPU, or reduce max_length

### API connection refused
- **Solution**: Ensure backend is running on port 8000, check firewall settings

### Slow inference
- **Solution**: Use GPU (CUDA), reduce max_length, or use smaller models

## 🎯 Model Training

To train your own models and use them in this demo:

1. **Train FLAN-T5**: See `/T5-model/` for training examples
2. **Train CodeGen**: See `/codegen_demo.ipynb` for training examples
3. **Save Model**: Use `model.save_pretrained("path/to/model")`
4. **Update Path**: Modify `model_manager.py` to point to your trained model

## 📦 Project Structure Details

```
demo-app/
├── backend/
│   ├── api.py                 # FastAPI endpoints
│   │   ├── /predict/flan-t5   # FLAN-T5 inference
│   │   ├── /predict/codegen   # CodeGen inference
│   │   ├── /compare           # V1 vs V2 comparison
│   │   ├── /health            # Health check
│   │   └── /models            # Model info
│   │
│   ├── model_manager.py       # Model loading & inference logic
│   │   ├── ModelManager class
│   │   ├── load_flan_t5_v1/v2()
│   │   ├── load_codegen_v1/v2()
│   │   └── generate_*() methods
│   │
│   └── requirements.txt       # Backend dependencies
│
├── frontend/
│   ├── app.py                 # Streamlit UI
│   │   ├── Single Model Mode
│   │   ├── Comparison Mode
│   │   ├── API health check
│   │   └── Results visualization
│   │
│   └── requirements.txt       # Frontend dependencies
│
├── models/                    # (Optional) Model storage
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── start_backend.sh           # Backend launcher
├── start_frontend.sh          # Frontend launcher
└── README.md                  # This file
```

## 🚀 Deployment

### Local Development
Already covered in Quick Start section above.

### Production Deployment

#### Docker (Recommended)
```dockerfile
# Dockerfile.backend
FROM python:3.10-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "api.py"]
```

```dockerfile
# Dockerfile.frontend
FROM python:3.10-slim
WORKDIR /app
COPY frontend/requirements.txt .
RUN pip install -r requirements.txt
COPY frontend/ .
CMD ["streamlit", "run", "app.py"]
```

#### Cloud Platforms
- **Hugging Face Spaces**: Upload as Streamlit app
- **Render**: Deploy backend as web service
- **Railway**: Deploy both services
- **AWS/GCP/Azure**: Use container services

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

Feel free to fork, modify, and use this demo for your own projects!

## 📧 Contact

For questions or issues, please open an issue in the repository.

---

**Built with:**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for APIs
- [Streamlit](https://streamlit.io/) - Fast way to build ML apps
- [Transformers](https://huggingface.co/transformers/) - State-of-the-art NLP models
- [PyTorch](https://pytorch.org/) - Deep learning framework
