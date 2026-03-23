"""
Streamlit Frontend for Model Inference Demo
Interactive UI for comparing pretrained vs fine-tuned models
"""

import streamlit as st
import requests
import json
from typing import Dict
import time

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="T5 & CodeGen Model Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .model-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json()
    except:
        return False, None


def get_models_info():
    """Get information about loaded models"""
    try:
        response = requests.get(f"{API_BASE_URL}/models", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def predict_flan_t5(sentence: str, word: str, model_version: str, params: Dict):
    """Call FLAN-T5 prediction endpoint"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/flan-t5",
            json={
                "sentence": sentence,
                "word": word,
                "model_version": model_version,
                **params
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


def predict_codegen(prompt: str, model_version: str, params: Dict):
    """Call CodeGen prediction endpoint"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/codegen",
            json={
                "prompt": prompt,
                "model_version": model_version,
                **params
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


def compare_models(sentence: str, word: str, model_type: str, params: Dict):
    """Call comparison endpoint"""
    try:
        payload = {
            "model_type": model_type,
            **params
        }
        
        if model_type == "flan-t5":
            payload["sentence"] = sentence
            payload["word"] = word
        else:
            payload["input_text"] = sentence  # For codegen, sentence is the prompt
        
        response = requests.post(
            f"{API_BASE_URL}/compare",
            json=payload,
            timeout=120
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


# Main App
def main():
    st.markdown('<div class="main-header">🤖 T5 & CodeGen Model Demo</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Compare Untrained vs Trained Models</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check API status
        is_healthy, health_data = check_api_health()
        
        if is_healthy:
            st.success("✅ API Connected")
            if health_data:
                st.metric("Models Loaded", health_data.get("models_loaded", 0))
        else:
            st.error("❌ API Not Connected")
            st.warning("Please start the backend API first:\n```bash\ncd backend\npython api.py\n```")
            return
        
        st.markdown("---")
        
        # Mode selection
        mode = st.radio(
            "Demo Mode",
            ["🔬 Single Model", "⚖️ Compare V1 vs V2"],
            index=1
        )
        
        st.markdown("---")
        
        # Model info
        if st.button("📊 Show Model Info"):
            models_info = get_models_info()
            if models_info:
                st.json(models_info)
    
    # Main content
    if mode == "🔬 Single Model":
        show_single_model_mode()
    else:
        show_comparison_mode()


def show_single_model_mode():
    """Single model inference mode"""
    st.header("🔬 Single Model Inference")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Model selection
        model_type = st.selectbox(
            "Select Model",
            ["T5", "CodeGen"],
            key="single_model_type"
        )
        
        model_version = st.radio(
            "Model Version",
            ["v1 (Untrained/Base)", "v2 (Trained)"],
            horizontal=True,
            key="single_version"
        )
        version = "v1" if "v1" in model_version else "v2"
    
    with col2:
        # Parameters
        st.subheader("Parameters")
        if model_type == "T5":
            k = st.slider("Top K candidates", 1, 10, 5, key="single_k")
            num_beams = st.slider("Num Beams", 1, 20, 10, key="single_beams")
            max_length = st.slider("Max Length", 10, 512, 128, key="single_max_len")
        else:
            max_length = st.slider("Max Length", 10, 512, 128, key="single_max_len")
            temperature = st.slider("Temperature", 0.1, 2.0, 0.7, 0.1, key="single_temp")
            top_p = st.slider("Top P", 0.0, 1.0, 0.95, 0.05, key="single_top_p")
    
    # Input
    if model_type == "T5":
        st.subheader("Input (Lexical Simplification)")
        
        col_a, col_b = st.columns([3, 1])
        with col_a:
            sentence_input = st.text_area(
                "Sentence",
                placeholder="The weather today is extraordinarily magnificent.",
                height=80,
                key="single_sentence"
            )
        with col_b:
            word_input = st.text_input(
                "Complex Word",
                placeholder="extraordinarily",
                key="single_word"
            )
        
        # Example prompts
        st.markdown("**Example sentences:**")
        examples = [
            ("The weather today is extraordinarily magnificent.", "extraordinarily"),
            ("The proliferation of artificial intelligence has revolutionized linguistics.", "proliferation"),
            ("This medication can ameliorate the symptoms significantly.", "ameliorate")
        ]
        example_buttons = st.columns(3)
        for i, (sent, word) in enumerate(examples):
            if example_buttons[i].button(f"Example {i+1}", key=f"ex_single_{i}"):
                st.session_state.single_sentence = sent
                st.session_state.single_word = word
                st.rerun()
    else:
        st.subheader("Code Prompt")
        input_text = st.text_area(
            "Enter your code prompt",
            placeholder="def calculate_fibonacci(n):",
            height=100,
            key="single_prompt"
        )
        
        # Example prompts
        st.markdown("**Example prompts:**")
        examples = [
            "def reverse_string(s):",
            "# Function to check if number is prime\ndef is_prime(n):",
            "class BinaryTree:"
        ]
        example_buttons = st.columns(3)
        for i, example in enumerate(examples):
            if example_buttons[i].button(f"Example {i+1}", key=f"ex_code_single_{i}"):
                st.session_state.single_prompt = example
                st.rerun()
    
    # Generate button
    if st.button("🚀 Generate", type="primary", key="single_generate"):
        if model_type == "T5":
            if not sentence_input or not word_input:
                st.warning("Please enter both sentence and word")
                return
            
            with st.spinner(f"Generating with {model_type} {version}..."):
                params = {
                    "k": k,
                    "num_beams": num_beams,
                    "max_length": max_length
                }
                result = predict_flan_t5(sentence_input, word_input, version, params)
        else:
            if not input_text:
                st.warning("Please enter input prompt")
                return
            
            with st.spinner(f"Generating with {model_type} {version}..."):
                params = {
                    "max_length": max_length,
                    "temperature": temperature,
                    "top_p": top_p
                }
                result = predict_codegen(input_text, version, params)
        
        # Display result
        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.success("✅ Generation Complete")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader("Output")
                st.code(result["output"], language="python" if model_type == "CodeGen" else None)
            
            with col2:
                st.metric("Inference Time", f"{result['inference_time']}s")
                st.metric("Model Version", result['model_version'])


def show_comparison_mode():
    """Model comparison mode (v1 vs v2)"""
    st.header("⚖️ Compare V1 (Untrained/Base) vs V2 (Trained)")
    
    # Model type selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        model_type = st.selectbox(
            "Select Model Type",
            ["flan-t5", "codegen"],
            format_func=lambda x: "T5" if x == "flan-t5" else "CodeGen",
            key="compare_model"
        )
    
    with col2:
        st.subheader("Parameters")
        if model_type == "flan-t5":
            k = st.slider("Top K candidates", 1, 10, 5, key="compare_k")
            num_beams = st.slider("Num Beams", 1, 20, 10, key="compare_beams")
            max_length = st.slider("Max Length", 10, 512, 128, key="compare_max_len")
        else:
            max_length = st.slider("Max Length", 10, 512, 128, key="compare_max_len")
            temperature = st.slider("Temperature", 0.1, 2.0, 0.7, 0.1, key="compare_temp")
    
    # Input
    if model_type == "flan-t5":
        st.subheader("Input (Lexical Simplification)")
        
        col_a, col_b = st.columns([3, 1])
        with col_a:
            sentence_input = st.text_area(
                "Sentence",
                placeholder="The weather today is extraordinarily magnificent.",
                height=100,
                key="compare_sentence"
            )
        with col_b:
            word_input = st.text_input(
                "Complex Word",
                placeholder="extraordinarily",
                key="compare_word"
            )
        
        # Example prompts
        st.markdown("**Example sentences:**")
        examples = [
            ("The weather today is extraordinarily magnificent.", "extraordinarily"),
            ("Machine learning algorithms are becoming increasingly sophisticated.", "sophisticated"),
            ("This medication can ameliorate the symptoms significantly.", "ameliorate")
        ]
        cols = st.columns(3)
        for i, (sent, word) in enumerate(examples):
            if cols[i].button(f"Example {i+1}", key=f"ex_comp_{i}"):
                st.session_state.compare_sentence = sent
                st.session_state.compare_word = word
                st.rerun()
    else:
        st.subheader("Code Prompt")
        input_text = st.text_area(
            "Enter your code prompt",
            placeholder="def calculate_fibonacci(n):",
            height=120,
            key="compare_prompt"
        )
        
        # Example prompts
        st.markdown("**Example prompts:**")
        examples = [
            "def binary_search(arr, target):",
            "# Merge two sorted arrays\ndef merge_arrays(arr1, arr2):",
            "class Stack:"
        ]
        cols = st.columns(3)
        for i, example in enumerate(examples):
            if cols[i].button(f"Example {i+1}", key=f"ex_comp_code_{i}"):
                st.session_state.compare_prompt = example
                st.rerun()
    
    # Compare button
    if st.button("⚖️ Compare Models", type="primary", key="compare_btn"):
        if model_type == "flan-t5":
            if not sentence_input or not word_input:
                st.warning("Please enter both sentence and word")
                return
        else:
            if not input_text:
                st.warning("Please enter code prompt")
                return
        
        with st.spinner("Comparing v1 (untrained/base) vs v2 (trained)..."):
            if model_type == "flan-t5":
                params = {
                    "k": k,
                    "num_beams": num_beams,
                    "max_length": max_length
                }
                result = compare_models(sentence_input, word_input, model_type, params)
            else:
                params = {
                    "max_length": max_length,
                    "temperature": temperature
                }
                result = compare_models(input_text, "", model_type, params)
        
        # Display results
        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.success("✅ Comparison Complete")
            
            # Metrics row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("V1 Time", f"{result['v1_time']}s")
            with col2:
                st.metric("V2 Time", f"{result['v2_time']}s")
            with col3:
                speedup = ((result['v1_time'] - result['v2_time']) / result['v1_time'] * 100)
                st.metric("Time Difference", f"{speedup:+.1f}%")
            
            st.markdown("---")
            
            # Side-by-side comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔵 V1 - Untrained/Base Model")
                st.info(f"Inference time: {result['v1_time']}s")
                st.code(result["v1_output"], language="python" if model_type == "codegen" else None)
            
            with col2:
                st.subheader("🟢 V2 - Trained Model")
                st.info(f"Inference time: {result['v2_time']}s")
                st.code(result["v2_output"], language="python" if model_type == "codegen" else None)
            
            # Analysis
            st.markdown("---")
            st.subheader("📊 Analysis")
            
            v1_len = len(result["v1_output"])
            v2_len = len(result["v2_output"])
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("V1 Output Length", f"{v1_len} chars")
            col2.metric("V2 Output Length", f"{v2_len} chars")
            col3.metric("Length Difference", f"{v2_len - v1_len:+d} chars")
            col4.metric("Model Type", result['model_type'].upper())


if __name__ == "__main__":
    main()
