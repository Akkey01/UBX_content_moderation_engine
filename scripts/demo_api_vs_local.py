#!/usr/bin/env python3
"""
API vs Local Model Demonstration Script
Shows the benefits of API-first approach for content generation.
"""

import time
import os
import sys
import psutil
import requests
from typing import Dict, List, Tuple
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.llm_generator import GeminiProvider, OpenAIProvider, HuggingFaceProvider, OllamaProvider

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_section(title: str):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print("-" * 40)

def measure_memory_usage():
    """Measure current memory usage"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

def test_api_provider(provider_name: str, provider_class, api_key_env: str) -> Dict:
    """Test an API provider and return metrics"""
    print(f"\n🧪 Testing {provider_name}...")
    
    start_time = time.time()
    start_memory = measure_memory_usage()
    
    # Check if API key is available
    api_key = os.getenv(api_key_env)
    if not api_key:
        return {
            "available": False,
            "reason": f"{api_key_env} not set",
            "setup_time": 0,
            "memory_usage": 0,
            "test_time": 0,
            "success": False
        }
    
    # Initialize provider
    provider = provider_class()
    
    if not provider.is_available():
        return {
            "available": False,
            "reason": "Provider not available",
            "setup_time": time.time() - start_time,
            "memory_usage": measure_memory_usage() - start_memory,
            "test_time": 0,
            "success": False
        }
    
    setup_time = time.time() - start_time
    
    # Test generation
    test_start = time.time()
    try:
        content = provider.generate_content(
            "Write a short finance tip about investing in index funds.",
            max_tokens=50
        )
        test_time = time.time() - test_start
        success = bool(content and len(content) > 10)
        
        return {
            "available": True,
            "reason": "Success",
            "setup_time": setup_time,
            "memory_usage": measure_memory_usage() - start_memory,
            "test_time": test_time,
            "success": success,
            "content_preview": content[:100] if content else "No content"
        }
    except Exception as e:
        return {
            "available": True,
            "reason": f"Generation failed: {e}",
            "setup_time": setup_time,
            "memory_usage": measure_memory_usage() - start_memory,
            "test_time": time.time() - test_start,
            "success": False
        }

def test_ollama_provider() -> Dict:
    """Test Ollama local provider"""
    print(f"\n🧪 Testing Ollama (Local)...")
    
    start_time = time.time()
    start_memory = measure_memory_usage()
    
    try:
        provider = OllamaProvider()
        
        if not provider.is_available():
            return {
                "available": False,
                "reason": "Ollama not installed or not running",
                "setup_time": time.time() - start_time,
                "memory_usage": measure_memory_usage() - start_memory,
                "test_time": 0,
                "success": False
            }
        
        setup_time = time.time() - start_time
        
        # Test generation
        test_start = time.time()
        content = provider.generate_content(
            "Write a short finance tip about investing in index funds.",
            max_tokens=50
        )
        test_time = time.time() - test_start
        success = bool(content and len(content) > 10)
        
        return {
            "available": True,
            "reason": "Success",
            "setup_time": setup_time,
            "memory_usage": measure_memory_usage() - start_memory,
            "test_time": test_time,
            "success": success,
            "content_preview": content[:100] if content else "No content"
        }
    except Exception as e:
        return {
            "available": False,
            "reason": f"Ollama error: {e}",
            "setup_time": time.time() - start_time,
            "memory_usage": measure_memory_usage() - start_memory,
            "test_time": 0,
            "success": False
        }

def print_comparison_table(results: Dict[str, Dict]):
    """Print a comparison table of all providers"""
    print_section("PROVIDER COMPARISON TABLE")
    
    # Table header
    print(f"{'Provider':<15} {'Available':<10} {'Setup(s)':<8} {'Memory(MB)':<12} {'Test(s)':<8} {'Success':<8} {'Notes':<20}")
    print("-" * 85)
    
    for provider, result in results.items():
        available = "✅" if result["available"] else "❌"
        success = "✅" if result.get("success", False) else "❌"
        setup_time = f"{result['setup_time']:.2f}"
        memory = f"{result['memory_usage']:.1f}"
        test_time = f"{result['test_time']:.2f}"
        notes = result.get("reason", "")[:18]
        
        print(f"{provider:<15} {available:<10} {setup_time:<8} {memory:<12} {test_time:<8} {success:<8} {notes:<20}")

def print_recommendations(results: Dict[str, Dict]):
    """Print recommendations based on results"""
    print_section("RECOMMENDATIONS")
    
    available_apis = [name for name, result in results.items() 
                     if result["available"] and result.get("success", False) and "API" in name]
    
    if available_apis:
        print("🎯 RECOMMENDED APPROACH: API-First")
        print("✅ Use API providers for content generation:")
        for api in available_apis:
            print(f"   • {api}: Fast setup, low memory, reliable")
        
        print("\n💡 Benefits of API approach:")
        print("   • No large model downloads (8GB+)")
        print("   • No GPU requirements")
        print("   • Instant setup and deployment")
        print("   • Always up-to-date models")
        print("   • Better performance and reliability")
        print("   • Free tiers available")
        
    else:
        print("⚠️ No API providers available")
        print("🔧 Consider setting up API keys for better performance")
        print("   • Gemini API: https://makersuite.google.com/app/apikey")
        print("   • OpenAI API: https://platform.openai.com/api-keys")
        print("   • HuggingFace: https://huggingface.co/settings/tokens")
    
    # Check if Ollama is available as fallback
    ollama_result = results.get("Ollama", {})
    if ollama_result.get("available", False) and ollama_result.get("success", False):
        print("\n🦙 Local Fallback Available:")
        print("   • Ollama can be used when APIs are unavailable")
        print("   • Requires local model download and GPU")
        print("   • Slower setup but works offline")

def print_cost_analysis():
    """Print cost analysis for different approaches"""
    print_section("COST ANALYSIS")
    
    print("💰 API Costs (Monthly estimates for 10K posts):")
    print("   • Gemini API: FREE (1M chars/month)")
    print("   • OpenAI GPT-3.5: ~$2-5")
    print("   • HuggingFace: FREE (limited)")
    
    print("\n💸 Local Model Costs:")
    print("   • GPU: $500-2000+ (one-time)")
    print("   • Electricity: $50-200/month")
    print("   • Maintenance: $100-500/month")
    print("   • Storage: $20-100/month")
    
    print("\n📊 Break-even Analysis:")
    print("   • API approach: ~$10-50/month")
    print("   • Local approach: ~$200-500/month")
    print("   • Break-even: 2-3 years of heavy usage")

def main():
    """Main demonstration function"""
    print_header("API vs LOCAL MODEL COMPARISON")
    print("🎯 Demonstrating the benefits of API-first approach")
    
    # Test all providers
    results = {}
    
    # API Providers
    results["Gemini API"] = test_api_provider("Gemini", GeminiProvider, "GEMINI_API_KEY")
    results["OpenAI API"] = test_api_provider("OpenAI", OpenAIProvider, "OPENAI_API_KEY")
    results["HuggingFace API"] = test_api_provider("HuggingFace", HuggingFaceProvider, "HUGGINGFACE_TOKEN")
    
    # Local Provider
    results["Ollama"] = test_ollama_provider()
    
    # Print results
    print_comparison_table(results)
    print_recommendations(results)
    print_cost_analysis()
    
    # Summary
    print_section("SUMMARY")
    
    api_count = sum(1 for name, result in results.items() 
                   if result["available"] and result.get("success", False) and "API" in name)
    local_count = sum(1 for name, result in results.items() 
                     if result["available"] and result.get("success", False) and "API" not in name)
    
    print(f"📊 Available Providers:")
    print(f"   • API Providers: {api_count}")
    print(f"   • Local Providers: {local_count}")
    
    if api_count > 0:
        print("\n🎉 RECOMMENDATION: Use API-first approach!")
        print("   • Faster setup")
        print("   • Lower resource usage")
        print("   • Better reliability")
        print("   • Cost-effective for most use cases")
    else:
        print("\n⚠️ No API providers available")
        print("   • Consider setting up API keys")
        print("   • Use local models as fallback")
    
    print("\n🚀 Next Steps:")
    print("   1. Set up API keys for preferred providers")
    print("   2. Run: python scripts/setup_llm.py")
    print("   3. Test: python scripts/generate_posts.py --use-llm")

if __name__ == "__main__":
    main() 