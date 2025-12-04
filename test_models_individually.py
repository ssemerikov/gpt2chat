#!/usr/bin/env python3
"""
Individual Model Testing Script
Tests each model in a fresh browser session to isolate crashes
"""

import json
import time
import subprocess
import os
from datetime import datetime

# All 61 models from the HTML
ALL_MODELS = [
    "Xenova/pythia-14m",
    "Xenova/llama2.c-stories15M",
    "Xenova/distilgpt2",
    "Xenova/llama2.c-stories110M",
    "Xenova/Qwen1.5-0.5B-Chat",
    "Xenova/TinyLlama-1.1B-Chat-v1.0",
    "Xenova/Qwen1.5-1.8B-Chat",
    "Xenova/LaMini-GPT-124M",
    "Xenova/LaMini-Neo-125M",
    "Xenova/LaMini-Cerebras-256M",
    "Xenova/LaMini-GPT-774M",
    "Xenova/gpt-neo-125M",
    "Xenova/gpt2",
    "Xenova/llama-160m",
    "Xenova/stablelm-2-zephyr-1_6b",
    "Xenova/codegen-350M-mono",
    "Xenova/tiny_starcoder_py",
    "Xenova/WizardCoder-1B-V1.0",
    "Xenova/deepseek-coder-1.3b-instruct",
    "Xenova/opt-125m",
    "Xenova/opt-350m",
    "Xenova/pythia-410m",
    "Xenova/bloomz-560m",
    "Xenova/bloom-560m",
    "Xenova/phi-1_5_dev",
    "Xenova/pygmalion-350m",
    "Xenova/gpt2-large-conversational",
    "Xenova/slovak-gpt-j-405M",
    "Xenova/gpt-neo-romanian-125m",
    "Xenova/kogpt-j-350m",
    "Xenova/tamillama_tiny_30m",
    "Xenova/J-350M",
    "Xenova/llama2.c-stories42M",
    "Xenova/llama-68m",
    "Xenova/pythia-31m",
    "Xenova/pythia-70m",
    "Xenova/pythia-70m-deduped",
    "Xenova/pythia-160m",
    "Xenova/pythia-160m-deduped",
    "Xenova/pythia-410m-deduped",
    "Xenova/codegen-350M-multi",
    "Xenova/codegen-350M-nl",
    "Xenova/starcoderbase-1b",
    "Xenova/starcoderbase-1b-sft",
    "Xenova/deepseek-coder-1.3b-base",
    "Xenova/LaMini-Cerebras-111M",
    "Xenova/LaMini-Cerebras-590M",
    "Xenova/falcon-rw-1b",
    "Xenova/tiny-random-falcon-7b",
    "Xenova/really-tiny-falcon-testing",
    "Xenova/TinyLLama-v0",
    "Xenova/LiteLlama-460M-1T",
    "Xenova/stablelm-2-1_6b",
    "Xenova/tiny-random-StableLmForCausalLM",
    "Xenova/Qwen1.5-0.5B",
    "Xenova/Qwen1.5-1.8B",
    "Xenova/tiny-random-mistral",
    "Xenova/tiny-random-PhiForCausalLM",
    "Xenova/tiny-random-Starcoder2ForCausalLM",
    "Xenova/ipt-350m",
    "Xenova/dlite-v2-774m",
]

# Results file
RESULTS_FILE = "individual_test_results.json"

def load_results():
    """Load existing results if available"""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return {
        "started_at": datetime.now().isoformat(),
        "completed": [],
        "results": {}
    }

def save_results(results):
    """Save results to file"""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

def test_single_model(model_name, timeout=120):
    """
    Test a single model using Node.js and Playwright
    Returns: dict with status, error, timing, etc.
    """
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print(f"{'='*60}")

    # Run the test using the existing test_one_model.js script
    try:
        proc = subprocess.run(
            ['node', 'test_one_model.js', model_name],
            capture_output=True,
            text=True,
            timeout=timeout + 30
        )

        # Parse result - look for JSON between markers
        try:
            output = proc.stdout
            if '__JSON_START__' in output and '__JSON_END__' in output:
                # Extract JSON between markers
                json_start = output.find('__JSON_START__') + len('__JSON_START__\n')
                json_end = output.find('__JSON_END__')
                json_str = output[json_start:json_end].strip()
                result = json.loads(json_str)
            else:
                # Fallback: try last line
                result = json.loads(output.strip().split('\n')[-1])

            print(f"✓ Result: {result['status']}")
            if result['status'] == 'success':
                print(f"  Load: {result['loadTime']}, Generate: {result['generateTime']}")
            elif result.get('error'):
                print(f"  Error: {result['error'][:100]}")
            return result
        except Exception as e:
            print(f"✗ Failed to parse result: {e}")
            return {
                "model": model_name,
                "status": "parse_error",
                "error": f"Could not parse output: {proc.stdout[:200]}"
            }

    except subprocess.TimeoutExpired:
        print(f"✗ Timeout after {timeout}s")
        return {
            "model": model_name,
            "status": "timeout",
            "error": f"Test exceeded {timeout} seconds"
        }
    except Exception as e:
        print(f"✗ Exception: {e}")
        return {
            "model": model_name,
            "status": "exception",
            "error": str(e)
        }

def main():
    print("="*60)
    print("INDIVIDUAL MODEL TESTING")
    print("="*60)
    print(f"Total models: {len(ALL_MODELS)}")
    print()

    # Load existing results
    results = load_results()
    completed = set(results['completed'])

    print(f"Already tested: {len(completed)}")
    print(f"Remaining: {len(ALL_MODELS) - len(completed)}")
    print()

    # Test each model
    for i, model in enumerate(ALL_MODELS):
        if model in completed:
            print(f"[{i+1}/{len(ALL_MODELS)}] Skipping {model} (already tested)")
            continue

        print(f"\n[{i+1}/{len(ALL_MODELS)}] Testing {model}")

        # Test model with 120 second timeout
        result = test_single_model(model, timeout=120)

        # Save result
        results['results'][model] = result
        results['completed'].append(model)
        save_results(results)

        # Small delay between tests
        time.sleep(2)

    # Print summary
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)

    successes = sum(1 for r in results['results'].values() if r['status'] == 'success')
    failures = len(results['results']) - successes

    print(f"Total: {len(results['results'])}")
    print(f"Success: {successes}")
    print(f"Failed: {failures}")
    print(f"\nResults saved to: {RESULTS_FILE}")

if __name__ == '__main__':
    main()
