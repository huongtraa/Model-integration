#!/usr/bin/env python3
"""
Model Setup Verification Script
Checks if all models are accessible and provides setup information
"""

import os
import sys
from pathlib import Path

def check_emoji(condition):
    return "✅" if condition else "❌"

def check_file_size(path):
    """Return human-readable file size"""
    if not os.path.exists(path):
        return "Not found"
    size = os.path.getsize(path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def check_directory_size(path):
    """Return total size of directory"""
    if not os.path.exists(path):
        return "Not found"
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total += os.path.getsize(filepath)
    
    size = total
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

print("=" * 70)
print("🔍 Model Setup Verification")
print("=" * 70)
print()

# Check project structure
print("📁 Project Structure:")
project_root = Path(__file__).parent
backend_path = project_root / "backend"
frontend_path = project_root / "frontend"
models_path = project_root / "models"

print(f"  {check_emoji(backend_path.exists())} Backend directory: {backend_path}")
print(f"  {check_emoji(frontend_path.exists())} Frontend directory: {frontend_path}")
print(f"  {check_emoji(models_path.exists())} Models directory: {models_path}")
print()

# Check Python files
print("🐍 Python Files:")
api_file = backend_path / "api.py"
model_manager_file = backend_path / "model_manager.py"
app_file = frontend_path / "app.py"

print(f"  {check_emoji(api_file.exists())} api.py: {check_file_size(api_file)}")
print(f"  {check_emoji(model_manager_file.exists())} model_manager.py: {check_file_size(model_manager_file)}")
print(f"  {check_emoji(app_file.exists())} app.py: {check_file_size(app_file)}")
print()

# Check dependencies
print("📦 Dependencies:")
backend_pyproject = backend_path / "pyproject.toml"
frontend_pyproject = frontend_path / "pyproject.toml"
backend_requirements = backend_path / "requirements.txt"
frontend_requirements = frontend_path / "requirements.txt"

print(f"  {check_emoji(backend_pyproject.exists())} backend/pyproject.toml: {check_file_size(backend_pyproject)}")
print(f"  {check_emoji(frontend_pyproject.exists())} frontend/pyproject.toml: {check_file_size(frontend_pyproject)}")
print(f"  {check_emoji(backend_requirements.exists())} backend/requirements.txt: {check_file_size(backend_requirements)}")
print(f"  {check_emoji(frontend_requirements.exists())} frontend/requirements.txt: {check_file_size(frontend_requirements)}")
print()

# Check T5 V2 model (flan-t5-lexical)
print("🤖 T5 Models:")
flan_t5_path = project_root.parent / "flan-t5-lexical"
flan_t5_model = flan_t5_path / "model.safetensors"
flan_t5_config = flan_t5_path / "config.json"

print(f"  T5 V1 (t5-base):")
print(f"    - Will download from Hugging Face on first run")
print(f"    - Size: ~900 MB")
print()
print(f"  T5 V2 (flan-t5-lexical):")
print(f"    {check_emoji(flan_t5_path.exists())} Path: {flan_t5_path}")
if flan_t5_path.exists():
    print(f"    {check_emoji(flan_t5_model.exists())} model.safetensors: {check_file_size(flan_t5_model)}")
    print(f"    {check_emoji(flan_t5_config.exists())} config.json: {check_file_size(flan_t5_config)}")
    print(f"    📊 Total size: {check_directory_size(flan_t5_path)}")
else:
    print(f"    ⚠️  Model directory not found!")
    print(f"    Expected at: {flan_t5_path}")
print()

# Check CodeGen models
print("💻 CodeGen Models:")
print(f"  CodeGen V1 (random weights):")
print(f"    - Created at runtime from config")
print(f"    - No download needed")
print()
print(f"  CodeGen V2 (pretrained):")
print(f"    - Will download from Hugging Face on first run")
print(f"    - Model: Salesforce/codegen-350M-mono")
print(f"    - Size: ~700 MB")
print()

# Check Hugging Face cache
print("💾 Hugging Face Cache:")
hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
print(f"  {check_emoji(hf_cache.exists())} Cache directory: {hf_cache}")
if hf_cache.exists():
    cache_size = check_directory_size(hf_cache)
    print(f"  📊 Cache size: {cache_size}")
    
    # List cached models
    cached_models = list(hf_cache.glob("models--*"))
    if cached_models:
        print(f"  📦 Cached models ({len(cached_models)}):")
        for model in cached_models[:5]:  # Show first 5
            model_name = model.name.replace("models--", "").replace("--", "/")
            print(f"    - {model_name}")
        if len(cached_models) > 5:
            print(f"    ... and {len(cached_models) - 5} more")
else:
    print(f"  ℹ️  Cache will be created on first model download")
print()

# Check startup scripts
print("🚀 Startup Scripts:")
start_backend = project_root / "start_backend.sh"
start_frontend = project_root / "start_frontend.sh"

print(f"  {check_emoji(start_backend.exists())} start_backend.sh: {check_file_size(start_backend)}")
if start_backend.exists():
    is_executable = os.access(start_backend, os.X_OK)
    print(f"    {check_emoji(is_executable)} Executable: {is_executable}")
    
print(f"  {check_emoji(start_frontend.exists())} start_frontend.sh: {check_file_size(start_frontend)}")
if start_frontend.exists():
    is_executable = os.access(start_frontend, os.X_OK)
    print(f"    {check_emoji(is_executable)} Executable: {is_executable}")
print()

# Check documentation
print("📚 Documentation:")
docs = [
    "README.md",
    "SETUP_GUIDE.md",
    "MODEL_CONFIG.md",
    "ARCHITECTURE.md",
    "UV_GUIDE.md",
    "UV_QUICKREF.md",
    "COMPLETION_SUMMARY.md"
]

for doc in docs:
    doc_path = project_root / doc
    print(f"  {check_emoji(doc_path.exists())} {doc}: {check_file_size(doc_path)}")
print()

# Summary
print("=" * 70)
print("📊 Summary")
print("=" * 70)

issues = []
if not backend_path.exists():
    issues.append("Backend directory missing")
if not frontend_path.exists():
    issues.append("Frontend directory missing")
if not flan_t5_path.exists():
    issues.append(f"T5 V2 model not found at {flan_t5_path}")
if not start_backend.exists() or not os.access(start_backend, os.X_OK):
    issues.append("start_backend.sh missing or not executable")
if not start_frontend.exists() or not os.access(start_frontend, os.X_OK):
    issues.append("start_frontend.sh missing or not executable")

if issues:
    print("⚠️  Issues found:")
    for issue in issues:
        print(f"  - {issue}")
    print()
    print("❌ Setup incomplete. Please fix the issues above.")
else:
    print("✅ All checks passed!")
    print()
    print("🎯 Next Steps:")
    print("  1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
    print("  2. Install dependencies:")
    print("     cd backend && uv sync")
    print("     cd ../frontend && uv sync")
    print("  3. Start the app:")
    print("     ./start_backend.sh   (Terminal 1)")
    print("     ./start_frontend.sh  (Terminal 2)")
    print()
    print("📝 Note: T5 V1 and CodeGen V2 will download automatically on first run")
    print("   Total download: ~1.6 GB | Time: 2-5 minutes")

print("=" * 70)
