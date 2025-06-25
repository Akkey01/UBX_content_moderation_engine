#!/usr/bin/env python3
"""
LLM Provider Setup Script for GuardianAI Content Generation
Helps configure and test various LLM providers for content generation.
Prioritizes API-based providers over local models for better performance and ease of use.
"""

import argparse
import logging
import sys
import os
import subprocess
import requests
from typing import Dict, List

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.llm_generator import GeminiProvider, OpenAIProvider, HuggingFaceProvider, OllamaProvider

def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level),
        format='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def setup_gemini():
    """Setup Google Gemini API (Recommended)"""
    print("\n🤖 GOOGLE GEMINI SETUP (RECOMMENDED)")
    print("="*50)
    print("✅ Best quality content generation")
    print("✅ Free tier: 15 requests/minute, 1M characters/month")
    print("✅ No local storage or GPU required")
    print("✅ Fast and reliable")
    
    print("\n📋 Setup Steps:")
    print("1. Visit: https://makersuite.google.com/app/apikey")
    print("2. Create a new API key (free)")
    print("3. Set environment variable:")
    print("   export GEMINI_API_KEY=your_api_key_here")
    print("   # or on Windows:")
    print("   set GEMINI_API_KEY=your_api_key_here")
    
    token = input("\nEnter your Gemini API key (or press Enter to skip): ").strip()
    if token:
        os.environ['GEMINI_API_KEY'] = token
        print("✅ Gemini API key set for this session")
        return True
    else:
        print("⚠️ Skipping Gemini setup")
        return False

def test_gemini_generation():
    """Test Gemini content generation"""
    print("\n🧪 Testing Gemini generation...")
    
    token = os.getenv("GEMINI_API_KEY")
    if not token:
        print("❌ GEMINI_API_KEY not set")
        return False
    
    provider = GeminiProvider(api_key=token)
    
    if not provider.is_available():
        print("❌ Gemini provider not available")
        return False
    
    try:
        test_prompt = "Write a short finance tip about investing in index funds."
        content = provider.generate_content(test_prompt, max_tokens=50)
        
        if content:
            print("✅ Gemini generation successful!")
            print(f"   Generated: {content[:100]}...")
            return True
        else:
            print("❌ Gemini generation failed - no content returned")
            return False
    except Exception as e:
        print(f"❌ Gemini generation failed: {e}")
        return False

def setup_openai():
    """Setup OpenAI API"""
    print("\n🤖 OPENAI SETUP")
    print("="*30)
    print("✅ Reliable and well-documented")
    print("✅ Good quality content generation")
    print("✅ Reasonable pricing for small scale")
    
    print("\n📋 Setup Steps:")
    print("1. Visit: https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Set environment variable:")
    print("   export OPENAI_API_KEY=your_api_key_here")
    print("   # or on Windows:")
    print("   set OPENAI_API_KEY=your_api_key_here")
    
    token = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()
    if token:
        os.environ['OPENAI_API_KEY'] = token
        print("✅ OpenAI API key set for this session")
        return True
    else:
        print("⚠️ Skipping OpenAI setup")
        return False

def test_openai_generation():
    """Test OpenAI content generation"""
    print("\n🧪 Testing OpenAI generation...")
    
    token = os.getenv("OPENAI_API_KEY")
    if not token:
        print("❌ OPENAI_API_KEY not set")
        return False
    
    provider = OpenAIProvider(api_key=token)
    
    if not provider.is_available():
        print("❌ OpenAI provider not available")
        return False
    
    try:
        test_prompt = "Write a short finance tip about investing in index funds."
        content = provider.generate_content(test_prompt, max_tokens=50)
        
        if content:
            print("✅ OpenAI generation successful!")
            print(f"   Generated: {content[:100]}...")
            return True
        else:
            print("❌ OpenAI generation failed - no content returned")
            return False
    except Exception as e:
        print(f"❌ OpenAI generation failed: {e}")
        return False

def setup_huggingface():
    """Setup HuggingFace API token"""
    print("\n🤗 HUGGINGFACE SETUP")
    print("="*30)
    print("✅ Free tier available")
    print("✅ Many models to choose from")
    print("✅ Open source models")
    
    print("\n📋 Setup Steps:")
    print("1. Visit: https://huggingface.co/settings/tokens")
    print("2. Create a new token (free tier available)")
    print("3. Set environment variable:")
    print("   export HUGGINGFACE_TOKEN=your_token_here")
    print("   # or on Windows:")
    print("   set HUGGINGFACE_TOKEN=your_token_here")
    
    token = input("\nEnter your HuggingFace token (or press Enter to skip): ").strip()
    if token:
        os.environ['HUGGINGFACE_TOKEN'] = token
        print("✅ HuggingFace token set for this session")
        return True
    else:
        print("⚠️ Skipping HuggingFace setup")
        return False

def test_huggingface_generation():
    """Test HuggingFace content generation"""
    print("\n🧪 Testing HuggingFace generation...")
    
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        print("❌ HUGGINGFACE_TOKEN not set")
        return False
    
    provider = HuggingFaceProvider(api_token=token)
    
    if not provider.is_available():
        print("❌ HuggingFace provider not available")
        return False
    
    try:
        test_prompt = "Write a short finance tip about investing in index funds."
        content = provider.generate_content(test_prompt, max_tokens=50)
        
        if content:
            print("✅ HuggingFace generation successful!")
            print(f"   Generated: {content[:100]}...")
            return True
        else:
            print("❌ HuggingFace generation failed - no content returned")
            return False
    except Exception as e:
        print(f"❌ HuggingFace generation failed: {e}")
        return False

def check_ollama_installation():
    """Check if Ollama is installed and provide installation instructions"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False

def install_ollama():
    """Provide Ollama installation instructions"""
    print("\n📦 Installing Ollama (Local Fallback):")
    print("⚠️ Only recommended if no API providers are available")
    print("1. Visit: https://ollama.ai/download")
    print("2. Download and install for your operating system")
    print("3. After installation, run: ollama pull llama3.1:8b")
    print("4. Start Ollama service: ollama serve")
    print("\nAlternative (macOS/Linux):")
    print("   curl -fsSL https://ollama.ai/install.sh | sh")

def check_ollama_models():
    """Check available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("📋 Available Ollama models:")
                for model in models:
                    print(f"   • {model.get('name', 'Unknown')}")
                return True
            else:
                print("⚠️ No models found. Run: ollama pull llama3.1:8b")
                return False
        else:
            print("❌ Ollama service not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def test_ollama_generation():
    """Test Ollama content generation"""
    print("\n🧪 Testing Ollama generation...")
    provider = OllamaProvider()
    
    if not provider.is_available():
        print("❌ Ollama provider not available")
        return False
    
    try:
        test_prompt = "Write a short finance tip about investing in index funds."
        content = provider.generate_content(test_prompt, max_tokens=50)
        
        if content:
            print("✅ Ollama generation successful!")
            print(f"   Generated: {content[:100]}...")
            return True
        else:
            print("❌ Ollama generation failed - no content returned")
            return False
    except Exception as e:
        print(f"❌ Ollama generation failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive test of all available providers in priority order"""
    print("\n" + "="*60)
    print("🔍 COMPREHENSIVE LLM PROVIDER TEST (API-FIRST)")
    print("="*60)
    
    results = {}
    
    # Test providers in priority order
    print("\n1️⃣ Testing Gemini (Recommended)...")
    token = os.getenv("GEMINI_API_KEY")
    if token:
        results['gemini'] = test_gemini_generation()
    else:
        print("⚠️ GEMINI_API_KEY not set, skipping test")
        results['gemini'] = False
    
    print("\n2️⃣ Testing OpenAI...")
    token = os.getenv("OPENAI_API_KEY")
    if token:
        results['openai'] = test_openai_generation()
    else:
        print("⚠️ OPENAI_API_KEY not set, skipping test")
        results['openai'] = False
    
    print("\n3️⃣ Testing HuggingFace...")
    token = os.getenv("HUGGINGFACE_TOKEN")
    if token:
        results['huggingface'] = test_huggingface_generation()
    else:
        print("⚠️ HUGGINGFACE_TOKEN not set, skipping test")
        results['huggingface'] = False
    
    print("\n4️⃣ Testing Ollama (Local Fallback)...")
    if check_ollama_installation():
        if check_ollama_models():
            results['ollama'] = test_ollama_generation()
        else:
            results['ollama'] = False
    else:
        results['ollama'] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    available_providers = []
    for provider, success in results.items():
        status = "✅ Available" if success else "❌ Not Available"
        print(f"{provider.title()}: {status}")
        if success:
            available_providers.append(provider)
    
    if available_providers:
        print(f"\n🎉 {len(available_providers)} provider(s) available for content generation!")
        print("Priority order: Gemini > OpenAI > HuggingFace > Ollama")
        print("You can now use: python scripts/generate_posts.py --use-llm")
    else:
        print("\n⚠️ No LLM providers available. Using template-based generation only.")
        print("You can still use: python scripts/generate_posts.py --no-llm")

def main():
    parser = argparse.ArgumentParser(description="Setup and test LLM providers for content generation (API-first approach)")
    parser.add_argument('--test-only', action='store_true', help='Only run tests, skip setup')
    parser.add_argument('--setup-only', action='store_true', help='Only run setup, skip tests')
    parser.add_argument('--provider', choices=['gemini', 'openai', 'huggingface', 'ollama'], 
                       help='Setup specific provider only')
    parser.add_argument('--loglevel', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    setup_logging(args.loglevel)
    logger = logging.getLogger(__name__)
    
    print("🚀 LLM Provider Setup for GuardianAI Content Generation")
    print("🎯 API-First Approach: Better performance, no local storage required")
    print("="*60)
    
    if args.test_only:
        run_comprehensive_test()
        return
    
    if args.provider:
        # Setup specific provider
        if args.provider == 'gemini':
            setup_gemini()
            if not args.setup_only:
                test_gemini_generation()
        elif args.provider == 'openai':
            setup_openai()
            if not args.setup_only:
                test_openai_generation()
        elif args.provider == 'huggingface':
            setup_huggingface()
            if not args.setup_only:
                test_huggingface_generation()
        elif args.provider == 'ollama':
            if not check_ollama_installation():
                install_ollama()
            if not args.setup_only:
                test_ollama_generation()
    else:
        # Setup all providers in priority order
        print("Setting up all available LLM providers (API-first)...")
        
        # 1. Gemini (Recommended)
        print("\n" + "-"*40)
        setup_gemini()
        
        # 2. OpenAI
        print("\n" + "-"*40)
        setup_openai()
        
        # 3. HuggingFace
        print("\n" + "-"*40)
        setup_huggingface()
        
        # 4. Ollama (Local fallback)
        print("\n" + "-"*40)
        print("🦙 OLLAMA SETUP (LOCAL FALLBACK)")
        print("-"*40)
        if not check_ollama_installation():
            install_ollama()
        else:
            check_ollama_models()
        
        if not args.setup_only:
            run_comprehensive_test()
    
    print("\n✨ Setup complete! You can now generate content with LLMs.")
    print("💡 Recommendation: Use Gemini API for best quality and free tier!")

if __name__ == "__main__":
    main() 