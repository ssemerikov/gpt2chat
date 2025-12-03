#!/usr/bin/env python3
"""
Comprehensive Model Testing Script
Tests all candidate models to find which ones actually work in the browser
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

# Candidate models to test
CANDIDATE_MODELS = [
    # Verified Working (should pass)
    {"name": "Xenova/distilgpt2", "expected": "✅"},
    {"name": "Xenova/gpt2", "expected": "✅"},
    {"name": "Xenova/stablelm-2-zephyr-1_6b", "expected": "✅"},

    # onnx-community models (to be tested)
    {"name": "onnx-community/Qwen2.5-1.5B", "expected": "⚠️"},
    {"name": "onnx-community/Qwen2.5-0.5B-Instruct", "expected": "⚠️"},
    {"name": "onnx-community/Llama-3.2-1B-Instruct-ONNX", "expected": "⚠️"},
    {"name": "onnx-community/TinyLlama-1.1B-Chat-v1.0-ONNX", "expected": "⚠️"},
    {"name": "onnx-community/Llama-3.2-3B-Instruct-ONNX", "expected": "⚠️"},
    {"name": "onnx-community/gemma-3-270m-it-ONNX", "expected": "⚠️"},
    {"name": "onnx-community/gemma-3-1b-it-ONNX", "expected": "⚠️"},
    {"name": "onnx-community/MobileLLM-125M", "expected": "⚠️"},
    {"name": "onnx-community/MobileLLM-1B", "expected": "⚠️"},
    {"name": "onnx-community/Qwen2.5-Coder-0.5B-Instruct", "expected": "⚠️"},
]

TEST_MESSAGE = "Hello"

async def test_single_model(page, model_name, test_num, total):
    """Test a single model"""
    print(f"\n{'='*80}")
    print(f"🧪 [{test_num}/{total}] Testing: {model_name}")
    print(f"{'='*80}")

    result = {
        "model": model_name,
        "success": False,
        "load_time": None,
        "response_time": None,
        "response_text": None,
        "error": None,
        "screenshot": None
    }

    try:
        start_time = datetime.now()

        # Select model from dropdown
        print(f"📝 Selecting model...")
        await page.select_option('#modelSelector', model_name)
        await asyncio.sleep(1)

        # Check if loading starts
        print(f"⏳ Waiting for model to load (max 90s)...")

        try:
            # Wait for status to show model is loaded
            await page.wait_for_function(
                """() => {
                    const status = document.querySelector('.status-text');
                    if (status) {
                        const text = status.textContent.toLowerCase();
                        console.log('Status text:', text);
                        return text.includes('ready') ||
                               text.includes('loaded') ||
                               text.includes('готова');
                    }
                    return false;
                }""",
                timeout=90000  # 90 seconds for model download
            )

            load_time = (datetime.now() - start_time).total_seconds()
            result["load_time"] = load_time
            print(f"✅ Model loaded in {load_time:.1f}s")

            # Clear any existing messages
            await page.evaluate("""() => {
                const messages = document.querySelector('#messagesContainer');
                if (messages) {
                    const msgs = messages.querySelectorAll('.message');
                    msgs.forEach(m => m.remove());
                }
            }""")

            # Send test message
            print(f"📤 Sending test message: '{TEST_MESSAGE}'")
            await page.fill('#messageInput', TEST_MESSAGE)
            await page.click('#sendBtn')

            # Wait for response
            print(f"⏳ Waiting for AI response (max 45s)...")
            response_start = datetime.now()

            await page.wait_for_function(
                """() => {
                    const assistantMsgs = document.querySelectorAll('.message.assistant');
                    return assistantMsgs.length > 0;
                }""",
                timeout=45000
            )

            response_time = (datetime.now() - response_start).total_seconds()
            result["response_time"] = response_time

            # Extract response text
            response_text = await page.locator('.message.assistant .message-text').first.text_content()
            response_text = response_text.strip()
            result["response_text"] = response_text

            print(f"✅ Response received in {response_time:.1f}s")
            print(f"📝 Response: {response_text[:80]}{'...' if len(response_text) > 80 else ''}")

            # Take screenshot
            screenshot_path = f'screenshots/model_{test_num}_{model_name.replace("/", "_")}.png'
            await page.screenshot(path=screenshot_path, full_page=True)
            result["screenshot"] = screenshot_path
            print(f"📸 Screenshot: {screenshot_path}")

            result["success"] = True
            print(f"🎉 {model_name} - TEST PASSED")

        except Exception as e:
            error_msg = str(e)

            # Check for specific error messages in console
            console_errors = await page.evaluate("""() => {
                const errors = window.__testErrors || [];
                return errors.join('; ');
            }""")

            if console_errors:
                error_msg = f"{error_msg} | Console: {console_errors}"

            result["error"] = error_msg

            # Take error screenshot
            screenshot_path = f'screenshots/model_{test_num}_{model_name.replace("/", "_")}_ERROR.png'
            await page.screenshot(path=screenshot_path)
            result["screenshot"] = screenshot_path

            if "Timeout" in error_msg:
                print(f"❌ TIMEOUT - Model took too long to load or respond")
            elif "Could not locate file" in error_msg:
                print(f"❌ MODEL NOT FOUND - ONNX files missing or incompatible")
            else:
                print(f"❌ ERROR: {error_msg[:100]}")

    except Exception as e:
        result["error"] = str(e)
        print(f"❌ CRITICAL ERROR: {str(e)[:100]}")

    return result

async def test_all_models():
    """Test all candidate models"""
    print("=" * 80)
    print("🚀 COMPREHENSIVE MODEL TESTING")
    print("=" * 80)
    print(f"Testing {len(CANDIDATE_MODELS)} models...")
    print(f"Server: http://localhost:8080")
    print()

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright not installed")
        return []

    results = []

    async with async_playwright() as p:
        print("🌐 Launching browser...")
        browser = await p.chromium.launch(headless=True)

        # Inject console error capture
        context = await browser.new_context()
        page = await context.new_page()

        # Capture console errors
        await page.add_init_script("""() => {
            window.__testErrors = [];
            const oldError = console.error;
            console.error = function(...args) {
                window.__testErrors.push(args.join(' '));
                oldError.apply(console, args);
            };
        }""")

        print("📄 Loading webapp...")
        await page.goto('http://localhost:8080', wait_until='networkidle')
        await asyncio.sleep(2)

        # Test each model
        for i, model_info in enumerate(CANDIDATE_MODELS, 1):
            model_name = model_info["name"]
            result = await test_single_model(page, model_name, i, len(CANDIDATE_MODELS))
            results.append(result)

            # Small delay between tests
            await asyncio.sleep(2)

        await browser.close()

    # Generate report
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)

    working_models = [r for r in results if r["success"]]
    failed_models = [r for r in results if not r["success"]]

    print(f"\n✅ WORKING MODELS: {len(working_models)}/{len(results)}")
    for r in working_models:
        print(f"   • {r['model']}")
        print(f"     Load: {r['load_time']:.1f}s | Response: {r['response_time']:.1f}s")

    print(f"\n❌ FAILED MODELS: {len(failed_models)}/{len(results)}")
    for r in failed_models:
        error_short = r['error'][:80] if r['error'] else "Unknown"
        print(f"   • {r['model']}")
        print(f"     Error: {error_short}")

    # Save results to JSON
    results_file = 'model_test_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total_tested": len(results),
            "working": len(working_models),
            "failed": len(failed_models),
            "results": results
        }, f, indent=2)

    print(f"\n💾 Full results saved to: {results_file}")

    return results

if __name__ == "__main__":
    Path('screenshots').mkdir(exist_ok=True)
    results = asyncio.run(test_all_models())

    working_count = sum(1 for r in results if r["success"])
    exit(0 if working_count > 0 else 1)
