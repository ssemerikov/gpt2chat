#!/usr/bin/env python3
"""
Verify the top 5 additional models have correct ONNX structure
"""

import requests

# Top 5 candidates to add (based on downloads, chat capability, variety)
TOP_5_CANDIDATES = [
    {
        "name": "Xenova/Qwen1.5-0.5B-Chat",
        "reason": "Popular (1,280 downloads), chat-optimized, small & fast",
        "size": "~300MB"
    },
    {
        "name": "Xenova/TinyLlama-1.1B-Chat-v1.0",
        "reason": "Popular (667 downloads), chat-optimized, instruction-tuned",
        "size": "~650MB"
    },
    {
        "name": "Xenova/codegen-350M-mono",
        "reason": "Coding specialist (172 downloads), Python focused",
        "size": "~350MB"
    },
    {
        "name": "Xenova/Qwen1.5-1.8B-Chat",
        "reason": "Better quality (1.8B), chat-optimized, balanced",
        "size": "~1.2GB"
    },
    {
        "name": "Xenova/llama2.c-stories15M",
        "reason": "Ultra-light (1,484 downloads), fastest option",
        "size": "~30MB"
    }
]

def verify_model(model_info):
    """Verify a model has correct ONNX structure"""
    model_name = model_info['name']
    print(f"\n{'='*80}")
    print(f"🔍 Verifying: {model_name}")
    print(f"{'='*80}")
    print(f"Reason: {model_info['reason']}")
    print(f"Size: {model_info['size']}")
    print()

    try:
        url = f"https://huggingface.co/api/models/{model_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check siblings for ONNX files
        siblings = data.get('siblings', [])
        onnx_files = [s['rfilename'] for s in siblings if '.onnx' in s['rfilename']]

        # Check for required files
        has_decoder_merged = any('decoder_model_merged' in f for f in onnx_files)
        has_quantized = any('quantized.onnx' in f for f in onnx_files)

        print(f"Total ONNX files: {len(onnx_files)}")
        print(f"Has decoder_model_merged: {'✅' if has_decoder_merged else '❌'}")
        print(f"Has quantized version: {'✅' if has_quantized else '❌'}")

        if len(onnx_files) > 0 and len(onnx_files) <= 15:
            print(f"\nONNX Files:")
            for f in onnx_files:
                indicator = "  ✅" if 'decoder_model_merged' in f else "   -"
                print(f"{indicator} {f}")

        # Verify config
        config_url = f"https://huggingface.co/{model_name}/resolve/main/config.json"
        config_response = requests.head(config_url, timeout=5)
        has_config = config_response.status_code == 200

        print(f"\nConfig.json exists: {'✅' if has_config else '❌'}")

        # Overall verdict
        is_compatible = has_decoder_merged and has_config
        print(f"\n{'✅ COMPATIBLE' if is_compatible else '❌ NOT COMPATIBLE'}")

        return {
            "model": model_name,
            "compatible": is_compatible,
            "has_decoder_merged": has_decoder_merged,
            "has_config": has_config,
            "onnx_file_count": len(onnx_files),
            **model_info
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "model": model_name,
            "compatible": False,
            "error": str(e),
            **model_info
        }

def main():
    print("=" * 80)
    print("🧪 VERIFYING TOP 5 ADDITIONAL MODELS")
    print("=" * 80)
    print(f"Testing {len(TOP_5_CANDIDATES)} models...")
    print()

    results = []
    for model_info in TOP_5_CANDIDATES:
        result = verify_model(model_info)
        results.append(result)

    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    compatible_models = [r for r in results if r.get('compatible', False)]
    print(f"\n✅ Compatible models: {len(compatible_models)}/{len(results)}")

    for r in compatible_models:
        print(f"\n{r['model']}")
        print(f"  Size: {r['size']}")
        print(f"  Reason: {r['reason']}")

    if len(compatible_models) < 5:
        print(f"\n⚠️  Only {len(compatible_models)} out of 5 are compatible")
        print("   Incompatible models:")
        for r in results:
            if not r.get('compatible', False):
                print(f"   ❌ {r['model']}")

    return results

if __name__ == "__main__":
    results = main()
