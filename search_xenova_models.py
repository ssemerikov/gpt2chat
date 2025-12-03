#!/usr/bin/env python3
"""
Search HuggingFace for all Xenova text-generation models
"""

import requests
import json

def search_xenova_models():
    """Search for all Xenova text-generation models"""

    print("=" * 80)
    print("🔍 Searching HuggingFace for Xenova text-generation models")
    print("=" * 80)
    print()

    # Search for Xenova models
    url = "https://huggingface.co/api/models"
    params = {
        "author": "Xenova",
        "pipeline_tag": "text-generation",
        "limit": 100
    }

    print(f"Querying: {url}")
    print(f"Parameters: {params}")
    print()

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        models = response.json()

        print(f"✅ Found {len(models)} text-generation models\n")

        text_gen_models = []

        for model in models:
            model_id = model.get('id', '')
            downloads = model.get('downloads', 0)
            likes = model.get('likes', 0)

            # Get more details
            try:
                model_url = f"https://huggingface.co/api/models/{model_id}"
                model_response = requests.get(model_url, timeout=10)
                model_data = model_response.json()

                # Check if it has ONNX files
                siblings = model_data.get('siblings', [])
                onnx_files = [s['rfilename'] for s in siblings if '.onnx' in s['rfilename']]
                has_decoder_merged = any('decoder_model_merged' in f for f in onnx_files)

                model_info = {
                    'id': model_id,
                    'downloads': downloads,
                    'likes': likes,
                    'onnx_files': len(onnx_files),
                    'has_decoder_merged': has_decoder_merged,
                    'tags': model_data.get('tags', [])
                }

                text_gen_models.append(model_info)

                status = "✅" if has_decoder_merged else "⚠️"
                print(f"{status} {model_id}")
                print(f"   Downloads: {downloads:,} | Likes: {likes}")
                print(f"   ONNX files: {len(onnx_files)} | Has decoder_merged: {has_decoder_merged}")

                if len(onnx_files) > 0 and len(onnx_files) <= 5:
                    for f in onnx_files[:5]:
                        print(f"   - {f}")
                print()

            except Exception as e:
                print(f"   Error fetching details: {e}")

        # Sort by downloads
        text_gen_models.sort(key=lambda x: x['downloads'], reverse=True)

        # Print summary
        print("=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Total text-generation models: {len(text_gen_models)}")
        print(f"With decoder_merged files: {sum(1 for m in text_gen_models if m['has_decoder_merged'])}")
        print()

        print("🏆 TOP MODELS BY DOWNLOADS:")
        for i, m in enumerate(text_gen_models[:10], 1):
            status = "✅" if m['has_decoder_merged'] else "⚠️"
            print(f"{i}. {status} {m['id']} - {m['downloads']:,} downloads")

        # Save results
        with open('xenova_text_gen_models.json', 'w') as f:
            json.dump(text_gen_models, f, indent=2)
        print(f"\n💾 Full results saved to: xenova_text_gen_models.json")

        return text_gen_models

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    models = search_xenova_models()
