#!/usr/bin/env python3
"""
Test which models are actually available on HuggingFace
by checking for config.json files
"""

import requests
import time
from typing import List, Dict

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

models = [
    # Tier 1: Best for Chat
    {"name": "onnx-community/Qwen2.5-1.5B", "tier": "Tier 1: Best for Chat", "size": "~900MB"},
    {"name": "onnx-community/Phi-3.5-mini-instruct-onnx-web", "tier": "Tier 1: Best for Chat", "size": "~2.3GB"},
    {"name": "onnx-community/Llama-3.2-1B-Instruct-ONNX", "tier": "Tier 1: Best for Chat", "size": "~650MB"},
    {"name": "onnx-community/TinyLlama-1.1B-Chat-v1.0-ONNX", "tier": "Tier 1: Best for Chat", "size": "~650MB"},

    # Tier 2: Fast & Efficient
    {"name": "onnx-community/Qwen2.5-0.5B-Instruct", "tier": "Tier 2: Fast & Efficient", "size": "~300MB"},
    {"name": "onnx-community/gemma-3-270m-it-ONNX", "tier": "Tier 2: Fast & Efficient", "size": "~150MB"},
    {"name": "onnx-community/MobileLLM-125M", "tier": "Tier 2: Fast & Efficient", "size": "~70MB"},
    {"name": "Xenova/distilgpt2", "tier": "Tier 2: Fast & Efficient", "size": "~150MB"},

    # Tier 3: Advanced
    {"name": "onnx-community/Llama-3.2-3B-Instruct-ONNX", "tier": "Tier 3: Advanced", "size": "~1.8GB"},
    {"name": "onnx-community/gemma-3-1b-it-ONNX", "tier": "Tier 3: Advanced", "size": "~600MB"},
    {"name": "onnx-community/MobileLLM-1B", "tier": "Tier 3: Advanced", "size": "~600MB"},
    {"name": "Xenova/stablelm-2-zephyr-1_6b", "tier": "Tier 3: Advanced", "size": "~1GB"},

    # Coding
    {"name": "onnx-community/Qwen2.5-Coder-0.5B-Instruct", "tier": "Coding Specialist", "size": "~300MB"},

    # Classic
    {"name": "Xenova/gpt2", "tier": "GPT-2 Family", "size": "~250MB"},
    {"name": "Xenova/gpt2-medium", "tier": "GPT-2 Family", "size": "~700MB"},
]

def test_model(model: Dict) -> Dict:
    """Test if a model is available on HuggingFace"""
    name = model['name']
    config_url = f"https://huggingface.co/{name}/resolve/main/config.json"

    try:
        response = requests.head(config_url, timeout=10, allow_redirects=True)

        if response.status_code == 200:
            return {
                "name": name,
                "success": True,
                "url": config_url
            }
        else:
            return {
                "name": name,
                "success": False,
                "error": f"HTTP {response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "name": name,
            "success": False,
            "error": str(e)
        }

def main():
    print(f"{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}🧪 Testing Model Availability on HuggingFace{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    results = []
    success_count = 0
    fail_count = 0

    for i, model in enumerate(models, 1):
        print(f"{YELLOW}[{i}/{len(models)}] Testing: {model['name']}{RESET}")
        print(f"  Tier: {model['tier']}")
        print(f"  Size: {model['size']}")

        result = test_model(model)
        results.append(result)

        if result['success']:
            print(f"  {GREEN}✅ AVAILABLE{RESET}")
            success_count += 1
        else:
            print(f"  {RED}❌ NOT AVAILABLE{RESET}")
            print(f"  {RED}Error: {result['error']}{RESET}")
            fail_count += 1

        print()

        # Small delay to avoid rate limiting
        if i < len(models):
            time.sleep(0.5)

    # Summary
    print(f"{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}📊 Summary{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    print(f"{GREEN}✅ Available: {success_count}/{len(models)} models{RESET}")
    print(f"{RED}❌ Unavailable: {fail_count}/{len(models)} models{RESET}")
    print()

    # List successful models
    if success_count > 0:
        print(f"{GREEN}Working models:{RESET}")
        for result in results:
            if result['success']:
                print(f"  • {result['name']}")
        print()

    # List failed models
    if fail_count > 0:
        print(f"{RED}Failed models:{RESET}")
        for result in results:
            if not result['success']:
                print(f"  • {result['name']} - {result['error']}")

if __name__ == "__main__":
    main()
