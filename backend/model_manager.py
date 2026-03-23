"""
Model Manager - Load and manage FLAN-T5 and CodeGen models
Handles both pretrained (v1) and fine-tuned (v2) versions
"""

import torch
from transformers import (
    T5Tokenizer, 
    T5ForConditionalGeneration,
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoConfig
)
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelManager:
    def __init__(self, models_dir: str = "../models"):
        """Initialize model manager with base directory for models"""
        self.models_dir = Path(models_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Model storage
        self.models = {}
        self.tokenizers = {}
        
    def load_flan_t5_v1(self):
        """Load pretrained T5-base (v1) from Hugging Face - like after.ipynb"""
        try:
            model_name = "t5-base"
            logger.info(f"Loading T5 v1 (pretrained from Hugging Face): {model_name}")
            
            tokenizer = T5Tokenizer.from_pretrained(model_name)
            model = T5ForConditionalGeneration.from_pretrained(model_name).to(self.device)
            model.eval()
            
            self.tokenizers['flan-t5-v1'] = tokenizer
            self.models['flan-t5-v1'] = model
            
            logger.info("✓ T5 v1 (pretrained) loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load T5 v1: {e}")
            return False
    
    def load_flan_t5_v2(self, model_path: str = None):
        """Load fine-tuned T5 (v2) from flan-t5-lexical - like before.ipynb"""
        try:
            # Use provided path or default to ../../flan-t5-lexical
            if model_path is None:
                model_path = str(Path(__file__).parent.parent.parent / "flan-t5-lexical")
            
            logger.info(f"Loading T5 v2 (fine-tuned): {model_path}")
            
            tokenizer = T5Tokenizer.from_pretrained(model_path)
            model = T5ForConditionalGeneration.from_pretrained(model_path).to(self.device)
            model.eval()
            
            self.tokenizers['flan-t5-v2'] = tokenizer
            self.models['flan-t5-v2'] = model
            
            logger.info("✓ T5 v2 (fine-tuned) loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load T5 v2: {e}")
            return False
    
    def load_codegen_v1(self):
        """Load CodeGen with random config (v1 - untrained) like codegen_demo.ipynb"""
        try:
            model_name = "Salesforce/codegen-350M-mono"
            logger.info(f"Loading CodeGen v1 (random weights - untrained): {model_name}")
            
            # Load config and tokenizer from pretrained
            config = AutoConfig.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            tokenizer.pad_token = tokenizer.eos_token
            
            # Create model with random weights (from_config instead of from_pretrained)
            model = AutoModelForCausalLM.from_config(config).to(self.device)
            model.eval()
            
            self.tokenizers['codegen-v1'] = tokenizer
            self.models['codegen-v1'] = model
            
            total_params = sum(p.numel() for p in model.parameters()) / 1e6
            logger.info(f"✓ CodeGen v1 (untrained, random weights) loaded: {total_params:.0f}M params")
            return True
        except Exception as e:
            logger.error(f"Failed to load CodeGen v1: {e}")
            return False
    
    def load_codegen_v2(self, model_path: str = None):
        """Load CodeGen with standard pretrained weights (v2 - trained) like codegen_demo.ipynb"""
        try:
            model_name = "Salesforce/codegen-350M-mono"
            logger.info(f"Loading CodeGen v2 (pretrained with standard weights): {model_name}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            tokenizer.pad_token = tokenizer.eos_token
            
            # Load model with pretrained weights (from_pretrained)
            model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)
            model.eval()
            
            self.tokenizers['codegen-v2'] = tokenizer
            self.models['codegen-v2'] = model
            
            total_params = sum(p.numel() for p in model.parameters()) / 1e6
            logger.info(f"✓ CodeGen v2 (pretrained, standard weights) loaded: {total_params:.0f}M params")
            return True
        except Exception as e:
            logger.error(f"Failed to load CodeGen v2: {e}")
            return False
    
    def load_all_models(self):
        """Load all available models"""
        results = {
            'flan-t5-v1': self.load_flan_t5_v1(),
            'flan-t5-v2': self.load_flan_t5_v2(),
            'codegen-v1': self.load_codegen_v1(),
            'codegen-v2': self.load_codegen_v2()
        }
        return results
    
    def build_input(self, sentence: str, word: str) -> str:
        """Build input format for lexical simplification (from after.ipynb)"""
        import re
        marked = re.sub(
            rf"\b{re.escape(word)}\b", f"[{word}]",
            sentence, count=1, flags=re.IGNORECASE
        )
        return f"simplify word: {word}\nsentence: {marked}"
    
    def generate_flan_t5(self, model_key: str, sentence: str, word: str, 
                         k: int = 5, num_beams: int = 10, max_length: int = 128):
        """Generate lexical simplification candidates using T5 model (from after.ipynb)"""
        if model_key not in self.models or model_key not in self.tokenizers:
            raise ValueError(f"Model {model_key} not loaded")
        
        import re
        tokenizer = self.tokenizers[model_key]
        model = self.models[model_key]
        
        # Build input using the format from after.ipynb
        input_text = self.build_input(sentence, word)
        
        inputs = tokenizer(
            input_text,
            return_tensors="pt",
            max_length=max_length,
            truncation=True,
        ).to(self.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                num_beams=num_beams,
                num_return_sequences=num_beams,
                max_new_tokens=16,
                early_stopping=True,
            )
        
        # Decode and filter candidates (from after.ipynb)
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        candidates, seen = [], set()
        for raw in decoded:
            w = re.sub(r"[^a-zA-Z]", "", raw.strip().lower().split()[0] if raw.strip() else "")
            if w and w != word.lower() and w not in seen and len(w) > 1:
                seen.add(w)
                candidates.append(w)
        
        return candidates[:k]
    
    def generate_codegen(self, model_key: str, prompt: str, max_length: int = 128, 
                         temperature: float = 0.7, top_p: float = 0.95):
        """Generate code using CodeGen model (parameters from codegen_demo.ipynb)"""
        if model_key not in self.models or model_key not in self.tokenizers:
            raise ValueError(f"Model {model_key} not loaded")
        
        tokenizer = self.tokenizers[model_key]
        model = self.models[model_key]
        
        inputs = tokenizer(prompt, return_tensors="pt", padding=True).to(self.device)
        input_ids = inputs['input_ids']
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                max_new_tokens=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                repetition_penalty=1.3,
                no_repeat_ngram_size=3,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Return only the generated part (excluding the prompt)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result
    
    def get_model_info(self, model_key: str):
        """Get information about a loaded model"""
        if model_key not in self.models:
            return {"error": "Model not loaded"}
        
        model = self.models[model_key]
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        return {
            "model_key": model_key,
            "device": str(self.device),
            "total_parameters": f"{total_params:,}",
            "trainable_parameters": f"{trainable_params:,}",
            "model_type": model.__class__.__name__
        }
    
    def get_loaded_models(self):
        """Return list of loaded model keys"""
        return list(self.models.keys())


# Singleton instance
_model_manager = None

def get_model_manager():
    """Get or create model manager singleton"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
