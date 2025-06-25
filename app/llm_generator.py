import requests
import json
import logging
import time
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import random
import os

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_content(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate content using the LLM provider"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available"""
        pass

class GeminiProvider(LLMProvider):
    """Google Gemini API provider (Recommended)"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        if not self.api_key:
            self.logger.debug("GEMINI_API_KEY not set")
            return False
        
        try:
            # Simple test request
            test_prompt = "Hello"
            response = requests.post(
                f"{self.base_url}/{self.model}:generateContent",
                params={"key": self.api_key},
                json={"contents": [{"parts": [{"text": test_prompt}]}]},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.debug(f"Gemini not available: {e}")
            return False
    
    def generate_content(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate content using Gemini API"""
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }
            
            response = requests.post(
                f"{self.base_url}/{self.model}:generateContent",
                params={"key": self.api_key},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    return content.strip()
                else:
                    self.logger.warning("No content in Gemini response")
                    return ""
            else:
                self.logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Gemini generation failed: {e}")
            return ""

class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        if not self.api_key:
            self.logger.debug("OPENAI_API_KEY not set")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.debug(f"OpenAI not available: {e}")
            return False
    
    def generate_content(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate content using OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                self.logger.error(f"OpenAI API error: {response.status_code}")
                return ""
                
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            return ""

class HuggingFaceProvider(LLMProvider):
    """HuggingFace Inference API provider"""
    
    def __init__(self, model: str = "microsoft/DialoGPT-medium", api_token: Optional[str] = None):
        self.model = model
        self.api_token = api_token or os.getenv("HUGGINGFACE_TOKEN")
        self.base_url = "https://api-inference.huggingface.co/models"
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if HuggingFace API is available"""
        if not self.api_token:
            self.logger.debug("HUGGINGFACE_TOKEN not set")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.api_token}"}
            response = requests.get(f"{self.base_url}/{self.model}", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.debug(f"HuggingFace not available: {e}")
            return False
    
    def generate_content(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate content using HuggingFace Inference API"""
        try:
            headers = {"Authorization": f"Bearer {self.api_token}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").replace(prompt, "").strip()
                return result.get("generated_text", "").replace(prompt, "").strip()
            else:
                self.logger.error(f"HuggingFace API error: {response.status_code}")
                return ""
                
        except Exception as e:
            self.logger.error(f"HuggingFace generation failed: {e}")
            return ""

class OllamaProvider(LLMProvider):
    """Ollama local LLM provider (Fallback option)"""
    
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(self.model in model.get("name", "") for model in models)
            return False
        except Exception as e:
            self.logger.debug(f"Ollama not available: {e}")
            return False
    
    def generate_content(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate content using Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                self.logger.error(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Ollama generation failed: {e}")
            return ""

class LLMContentGenerator:
    """Enhanced content generator using multiple LLM providers (API-first approach)"""
    
    def __init__(self, use_llm: bool = True, fallback_to_templates: bool = True):
        self.use_llm = use_llm
        self.fallback_to_templates = fallback_to_templates
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM providers (API-first order)
        self.providers = []
        if use_llm:
            self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers in priority order"""
        # 1. Google Gemini (Recommended - Best quality, free tier)
        gemini = GeminiProvider()
        if gemini.is_available():
            self.providers.append(gemini)
            self.logger.info("✅ Gemini provider available (Recommended)")
        
        # 2. OpenAI (Reliable, good quality)
        openai = OpenAIProvider()
        if openai.is_available():
            self.providers.append(openai)
            self.logger.info("✅ OpenAI provider available")
        
        # 3. HuggingFace (Free tier, many models)
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        if hf_token:
            hf = HuggingFaceProvider(api_token=hf_token)
            if hf.is_available():
                self.providers.append(hf)
                self.logger.info("✅ HuggingFace provider available")
        
        # 4. Ollama (Local fallback - only if no APIs are available)
        if not self.providers:  # Only try Ollama if no APIs are available
            ollama = OllamaProvider()
            if ollama.is_available():
                self.providers.append(ollama)
                self.logger.info("✅ Ollama provider available (Local fallback)")
        
        if not self.providers:
            self.logger.warning("⚠️ No LLM providers available, will use template generation")
        else:
            self.logger.info(f"🎯 Using {len(self.providers)} LLM provider(s) in priority order")
    
    def generate_llm_content(self, category: str, content_type: str) -> str:
        """Generate content using available LLM providers in priority order"""
        if not self.providers:
            return ""
        
        # Create context-aware prompts
        prompts = self._create_prompts(category, content_type)
        
        # Try providers in order (API-first, then local)
        for provider in self.providers:
            for prompt in prompts:
                try:
                    content = provider.generate_content(prompt, max_tokens=150)
                    if content and len(content) > 10:  # Basic validation
                        self.logger.debug(f"Generated content using {provider.__class__.__name__}")
                        return content
                except Exception as e:
                    self.logger.debug(f"Provider {provider.__class__.__name__} failed: {e}")
                    continue
        
        return ""
    
    def _create_prompts(self, category: str, content_type: str) -> List[str]:
        """Create context-aware prompts for different content types"""
        base_prompts = {
            "safe": [
                f"Write a short, professional finance post about {content_type}. Keep it under 100 words and make it sound like a real financial advisor or investor.",
                f"Create a helpful finance tip about {content_type} that would be appropriate for a professional finance community.",
                f"Write a brief, educational post about {content_type} that provides value to readers."
            ],
            "mild_violation": [
                f"Write a finance post that contains mild promotional language about {content_type}. Include some urgency but keep it subtle.",
                f"Create a post about {content_type} that uses some aggressive marketing language but isn't obviously a scam.",
                f"Write a finance post with mild spam indicators about {content_type}."
            ],
            "moderate_violation": [
                f"Write a finance post about {content_type} that contains obvious scam indicators like 'guaranteed returns' or 'no risk'.",
                f"Create a post about {content_type} that suggests insider information or market manipulation.",
                f"Write a finance post with moderate fraud indicators about {content_type}."
            ],
            "severe_violation": [
                f"Write a finance post about {content_type} that contains severe violations like profanity, obvious scams, or illegal activities.",
                f"Create a post about {content_type} that includes multiple serious policy violations.",
                f"Write a finance post with severe fraud, manipulation, or illegal content about {content_type}."
            ]
        }
        
        return base_prompts.get(category, base_prompts["safe"])
    
    def generate_hybrid_content(self, category: str, content_type: str, template_generator) -> str:
        """Generate content using LLM with fallback to templates"""
        if self.use_llm and self.providers:
            llm_content = self.generate_llm_content(category, content_type)
            if llm_content:
                return llm_content
        
        if self.fallback_to_templates:
            # Fallback to original template-based generation
            if category == "safe":
                return template_generator.generate_safe_post()
            elif category == "mild_violation":
                return template_generator.generate_mild_violation_post()
            elif category == "moderate_violation":
                return template_generator.generate_moderate_violation_post()
            elif category == "severe_violation":
                return template_generator.generate_severe_violation_post()
        
        return "" 