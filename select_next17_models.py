#!/usr/bin/env python3
"""
Select and verify the next 17 best models from remaining verified models
"""

import json

# Already added (8 models)
EXISTING_MODELS = [
    "Xenova/distilgpt2",
    "Xenova/gpt2",
    "Xenova/llama2.c-stories15M",
    "Xenova/Qwen1.5-0.5B-Chat",
    "Xenova/TinyLlama-1.1B-Chat-v1.0",
    "Xenova/codegen-350M-mono",
    "Xenova/Qwen1.5-1.8B-Chat",
    "Xenova/stablelm-2-zephyr-1_6b"
]

# Load the full search results
with open('xenova_text_gen_models.json', 'r') as f:
    all_models = json.load(f)

# Filter to only models with decoder_merged that we haven't added
remaining_models = [
    m for m in all_models
    if m['has_decoder_merged'] and m['id'] not in EXISTING_MODELS
]

# Sort by downloads
remaining_models.sort(key=lambda x: x['downloads'], reverse=True)

print("=" * 80)
print("🎯 SELECTING NEXT 17 MODELS")
print("=" * 80)
print(f"Total remaining with decoder_merged: {len(remaining_models)}")
print(f"Selecting top 17 by downloads and variety...\n")

# Select top 17, ensuring variety
selected = []

# Priority 1: Story models (small, fast)
story_models = [m for m in remaining_models if 'stories' in m['id'].lower() or 'llama-' in m['id'].lower() and int(m.get('downloads', 0)) > 20]
selected.extend(story_models[:2])

# Priority 2: Code models
code_models = [m for m in remaining_models if any(x in m['id'].lower() for x in ['codegen', 'starcoder', 'wizard', 'coder', 'deepseek']) and m not in selected]
selected.extend(code_models[:3])

# Priority 3: GPT-Neo family
neo_models = [m for m in remaining_models if 'neo' in m['id'].lower() and m not in selected]
selected.extend(neo_models[:2])

# Priority 4: LaMini family (instruction-tuned)
lamini_models = [m for m in remaining_models if 'lamini' in m['id'].lower() and m not in selected]
selected.extend(lamini_models[:3])

# Priority 5: Pythia family (research models)
pythia_models = [m for m in remaining_models if 'pythia' in m['id'].lower() and m not in selected]
selected.extend(pythia_models[:2])

# Priority 6: OPT family (Meta)
opt_models = [m for m in remaining_models if 'opt-' in m['id'].lower() and m not in selected]
selected.extend(opt_models[:2])

# Priority 7: Multilingual (BLOOM)
bloom_models = [m for m in remaining_models if 'bloom' in m['id'].lower() and m not in selected]
selected.extend(bloom_models[:1])

# Priority 8: Other popular models
other_models = [m for m in remaining_models if m not in selected]
other_models.sort(key=lambda x: x['downloads'], reverse=True)
selected.extend(other_models[:2])

# Ensure we have exactly 17
selected = selected[:17]

print(f"✅ Selected {len(selected)} models\n")

# Print selections by category
categories = {
    "📚 Story & Tiny Models": [],
    "💻 Code Specialists": [],
    "🔬 Research Models (Pythia)": [],
    "🎓 Instruction-Tuned (LaMini)": [],
    "🏛️ Meta Models (OPT)": [],
    "🧠 Neo Family": [],
    "🌍 Multilingual (BLOOM)": [],
    "⭐ Other Popular": []
}

for m in selected:
    mid = m['id'].lower()
    if 'stories' in mid or 'llama-' in mid:
        categories["📚 Story & Tiny Models"].append(m)
    elif any(x in mid for x in ['codegen', 'starcoder', 'wizard', 'coder', 'deepseek']):
        categories["💻 Code Specialists"].append(m)
    elif 'pythia' in mid:
        categories["🔬 Research Models (Pythia)"].append(m)
    elif 'lamini' in mid:
        categories["🎓 Instruction-Tuned (LaMini)"].append(m)
    elif 'opt-' in mid:
        categories["🏛️ Meta Models (OPT)"].append(m)
    elif 'neo' in mid:
        categories["🧠 Neo Family"].append(m)
    elif 'bloom' in mid:
        categories["🌍 Multilingual (BLOOM)"].append(m)
    else:
        categories["⭐ Other Popular"].append(m)

for category, models in categories.items():
    if models:
        print(f"\n{category} ({len(models)} models)")
        print("-" * 80)
        for i, m in enumerate(models, 1):
            print(f"{i}. {m['id']}")
            print(f"   Downloads: {m['downloads']:,} | ONNX files: {m['onnx_files']}")

print("\n" + "=" * 80)
print("📋 SUMMARY")
print("=" * 80)
print(f"Total models to add: {len(selected)}")
print(f"Total models after addition: {len(EXISTING_MODELS) + len(selected)} (8 + 17)")
print()

# Generate model list for webapp
print("📝 Models for webapp dropdown:")
print()
for i, m in enumerate(selected, 1):
    model_id = m['id']
    # Estimate size based on parameters (rough)
    size_mb = "~" + str(int(m.get('onnx_files', 5) * 50)) + "MB"
    print(f'<option value="{model_id}">')
    print(f'    {model_id.split("/")[1]} ({size_mb})')
    print(f'</option>')
    if i % 3 == 0:
        print()

# Save selection
with open('next_17_models.json', 'w') as f:
    json.dump(selected, f, indent=2)

print(f"\n💾 Selection saved to: next_17_models.json")
