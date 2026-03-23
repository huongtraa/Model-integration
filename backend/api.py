"""
FastAPI Backend for Model Inference Demo
Serves FLAN-T5 and CodeGen models (v1 pretrained & v2 fine-tuned)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import time
import uvicorn
from model_manager import get_model_manager

# Initialize FastAPI app
app = FastAPI(
    title="T5 & CodeGen Model API",
    description="API for T5 (lexical simplification) and CodeGen (code generation) - comparing untrained vs trained models",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class FLANT5Request(BaseModel):
    input_text: str = Field(..., description="Input sentence for T5 lexical simplification")
    model_version: str = Field("v1", description="Model version: 'v1' (t5-base untrained) or 'v2' (flan-t5-lexical trained)")
    max_length: int = Field(128, ge=10, le=512, description="Maximum output length")
    temperature: float = Field(1.0, ge=0.1, le=2.0, description="Sampling temperature")
    num_beams: int = Field(4, ge=1, le=10, description="Number of beams for beam search")

class CodeGenRequest(BaseModel):
    prompt: str = Field(..., description="Code prompt for CodeGen model")
    model_version: str = Field("v1", description="Model version: 'v1' (random weights untrained) or 'v2' (pretrained trained)")
    max_length: int = Field(128, ge=10, le=512, description="Maximum tokens to generate")
    temperature: float = Field(0.7, ge=0.1, le=2.0, description="Sampling temperature")
    top_p: float = Field(0.95, ge=0.0, le=1.0, description="Nucleus sampling probability")

class CompareRequest(BaseModel):
    input_text: str = Field(..., description="Input text/prompt to compare")
    model_type: str = Field(..., description="Model type: 'flan-t5' or 'codegen'")
    max_length: int = Field(128, ge=10, le=512)
    temperature: float = Field(1.0, ge=0.1, le=2.0)

# Response models
class InferenceResponse(BaseModel):
    output: str
    model_version: str
    inference_time: float
    parameters: Dict

class CompareResponse(BaseModel):
    v1_output: str
    v2_output: str
    v1_time: float
    v2_time: float
    model_type: str


# Model manager instance
model_manager = get_model_manager()


@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    print("🚀 Starting Model Inference API...")
    print("📦 Loading models (this may take a while)...")
    
    results = model_manager.load_all_models()
    
    print("\n📊 Model Loading Status:")
    for model_key, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {model_key}: {'Loaded' if success else 'Failed'}")
    
    loaded = model_manager.get_loaded_models()
    print(f"\n✅ API ready with {len(loaded)} models loaded")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "T5 & CodeGen Model API",
        "description": "Compare untrained vs trained models",
        "endpoints": {
            "health": "/health",
            "models": "/models",
            "flan-t5": "/predict/flan-t5",
            "codegen": "/predict/codegen",
            "compare": "/compare",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    loaded_models = model_manager.get_loaded_models()
    return {
        "status": "healthy",
        "models_loaded": len(loaded_models),
        "available_models": loaded_models
    }


@app.get("/models")
async def get_models_info():
    """Get information about all loaded models"""
    loaded_models = model_manager.get_loaded_models()
    models_info = {}
    
    for model_key in loaded_models:
        models_info[model_key] = model_manager.get_model_info(model_key)
    
    return {
        "total_models": len(loaded_models),
        "models": models_info
    }


@app.post("/predict/flan-t5", response_model=InferenceResponse)
async def predict_flan_t5(request: FLANT5Request):
    """Generate text using T5 model for lexical simplification"""
    try:
        model_key = f"flan-t5-{request.model_version}"
        
        if model_key not in model_manager.get_loaded_models():
            raise HTTPException(status_code=404, detail=f"Model {model_key} not loaded")
        
        start_time = time.time()
        
        output = model_manager.generate_flan_t5(
            model_key=model_key,
            input_text=request.input_text,
            max_length=request.max_length,
            temperature=request.temperature,
            num_beams=request.num_beams
        )
        
        inference_time = time.time() - start_time
        
        return InferenceResponse(
            output=output,
            model_version=request.model_version,
            inference_time=round(inference_time, 3),
            parameters={
                "max_length": request.max_length,
                "temperature": request.temperature,
                "num_beams": request.num_beams
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/codegen", response_model=InferenceResponse)
async def predict_codegen(request: CodeGenRequest):
    """Generate code using CodeGen model"""
    try:
        model_key = f"codegen-{request.model_version}"
        
        if model_key not in model_manager.get_loaded_models():
            raise HTTPException(status_code=404, detail=f"Model {model_key} not loaded")
        
        start_time = time.time()
        
        output = model_manager.generate_codegen(
            model_key=model_key,
            prompt=request.prompt,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p
        )
        
        inference_time = time.time() - start_time
        
        return InferenceResponse(
            output=output,
            model_version=request.model_version,
            inference_time=round(inference_time, 3),
            parameters={
                "max_length": request.max_length,
                "temperature": request.temperature,
                "top_p": request.top_p
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare", response_model=CompareResponse)
async def compare_models(request: CompareRequest):
    """Compare v1 (untrained/base) vs v2 (trained) models side-by-side"""
    try:
        if request.model_type not in ["flan-t5", "codegen"]:
            raise HTTPException(status_code=400, detail="model_type must be 'flan-t5' or 'codegen'")
        
        v1_key = f"{request.model_type}-v1"
        v2_key = f"{request.model_type}-v2"
        
        loaded = model_manager.get_loaded_models()
        if v1_key not in loaded or v2_key not in loaded:
            raise HTTPException(status_code=404, detail=f"Both {v1_key} and {v2_key} must be loaded")
        
        # Generate with v1
        start_v1 = time.time()
        if request.model_type == "flan-t5":
            v1_output = model_manager.generate_flan_t5(
                model_key=v1_key,
                input_text=request.input_text,
                max_length=request.max_length,
                temperature=request.temperature
            )
        else:
            v1_output = model_manager.generate_codegen(
                model_key=v1_key,
                prompt=request.input_text,
                max_length=request.max_length,
                temperature=request.temperature
            )
        v1_time = time.time() - start_v1
        
        # Generate with v2
        start_v2 = time.time()
        if request.model_type == "flan-t5":
            v2_output = model_manager.generate_flan_t5(
                model_key=v2_key,
                input_text=request.input_text,
                max_length=request.max_length,
                temperature=request.temperature
            )
        else:
            v2_output = model_manager.generate_codegen(
                model_key=v2_key,
                prompt=request.input_text,
                max_length=request.max_length,
                temperature=request.temperature
            )
        v2_time = time.time() - start_v2
        
        return CompareResponse(
            v1_output=v1_output,
            v2_output=v2_output,
            v1_time=round(v1_time, 3),
            v2_time=round(v2_time, 3),
            model_type=request.model_type
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
