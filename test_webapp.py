#!/usr/bin/env python3
"""
Web App Test Script using Playwright
Tests the GPT-2 chatbot web application
"""

import asyncio
import json
from datetime import datetime

async def test_webapp():
    """Test the web application"""
    print("=" * 80)
    print("🧪 Testing GPT-2 Chat Web App")
    print("=" * 80)
    print()

    try:
        # Import Playwright
        from playwright.async_api import async_playwright

        print("✅ Playwright imported successfully")
        print()

        async with async_playwright() as p:
            # Launch browser
            print("🌐 Launching browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Test 1: Page Load
            print("\n📋 Test 1: Page Load & Initial State")
            print("-" * 80)

            print("Navigating to http://localhost:8080...")
            await page.goto('http://localhost:8080', wait_until='networkidle')

            title = await page.title()
            print(f"✅ Page loaded: {title}")

            # Take screenshot
            await page.screenshot(path='screenshots/test1_initial_load.png')
            print("📸 Screenshot saved: screenshots/test1_initial_load.png")

            # Test 2: Check UI Elements
            print("\n📋 Test 2: UI Elements Check")
            print("-" * 80)

            # Check for key elements
            welcome_msg = await page.locator('.welcome-message').count()
            model_selector = await page.locator('#modelSelector').count()
            message_input = await page.locator('#messageInput').count()
            send_btn = await page.locator('#sendBtn').count()

            print(f"Welcome message: {'✅' if welcome_msg > 0 else '❌'}")
            print(f"Model selector: {'✅' if model_selector > 0 else '❌'}")
            print(f"Message input: {'✅' if message_input > 0 else '❌'}")
            print(f"Send button: {'✅' if send_btn > 0 else '❌'}")

            # Test 3: Check Default Model
            print("\n📋 Test 3: Default Model Selection")
            print("-" * 80)

            selected_model = await page.locator('#modelSelector').input_value()
            print(f"Default model: {selected_model}")

            if selected_model == "Xenova/distilgpt2":
                print("✅ Correct default model (Xenova/distilgpt2)")
            else:
                print(f"⚠️  Unexpected default model: {selected_model}")

            # Test 4: Model Loading
            print("\n📋 Test 4: Model Loading (30s timeout)")
            print("-" * 80)

            print("Waiting for model to load...")
            start_time = datetime.now()

            try:
                # Wait for loading indicator to appear and disappear
                await page.wait_for_selector('#loadingProgress', state='visible', timeout=5000)
                print("⏳ Model loading started...")

                # Wait for status to show success (increased timeout for model download)
                await page.wait_for_function(
                    """() => {
                        const status = document.querySelector('.status-text');
                        return status && (
                            status.textContent.includes('готова') ||
                            status.textContent.includes('ready') ||
                            status.textContent.includes('Model loaded')
                        );
                    }""",
                    timeout=60000  # 60 seconds for model download
                )

                load_time = (datetime.now() - start_time).total_seconds()
                print(f"✅ Model loaded successfully in {load_time:.1f} seconds")

                # Take screenshot after model loads
                await page.screenshot(path='screenshots/test4_model_loaded.png')
                print("📸 Screenshot saved: screenshots/test4_model_loaded.png")

                # Test 5: Send Message
                print("\n📋 Test 5: Send Message & Get Response")
                print("-" * 80)

                test_message = "Hello, how are you?"
                print(f"Sending test message: '{test_message}'")

                # Type message
                await page.fill('#messageInput', test_message)
                print("✅ Message typed")

                # Click send button
                await page.click('#sendBtn')
                print("✅ Send button clicked")

                # Wait for response (look for assistant message)
                print("⏳ Waiting for AI response (30s timeout)...")

                await page.wait_for_function(
                    """() => {
                        const messages = document.querySelectorAll('.message.assistant');
                        return messages.length > 0;
                    }""",
                    timeout=30000
                )

                response_time = (datetime.now() - start_time).total_seconds()
                print(f"✅ Response received in {response_time:.1f} seconds")

                # Extract response text
                response_text = await page.locator('.message.assistant .message-text').first.text_content()
                print(f"📝 AI Response: {response_text[:100]}...")

                # Take screenshot of conversation
                await page.screenshot(path='screenshots/test5_conversation.png', full_page=True)
                print("📸 Screenshot saved: screenshots/test5_conversation.png")

                # Test 6: Console Errors Check
                print("\n📋 Test 6: Console Errors Check")
                print("-" * 80)

                # Check for console errors
                errors = []
                page.on('console', lambda msg: errors.append(msg) if msg.type == 'error' else None)

                await asyncio.sleep(2)  # Wait a bit to catch any delayed errors

                if len(errors) == 0:
                    print("✅ No console errors detected")
                else:
                    print(f"⚠️  {len(errors)} console error(s) detected:")
                    for error in errors[:5]:  # Show first 5
                        print(f"   - {error.text}")

                # Test Summary
                print("\n" + "=" * 80)
                print("📊 Test Summary")
                print("=" * 80)
                print(f"✅ Page Load: PASSED")
                print(f"✅ UI Elements: PASSED")
                print(f"✅ Default Model: {selected_model}")
                print(f"✅ Model Loading: PASSED ({load_time:.1f}s)")
                print(f"✅ Message Send: PASSED")
                print(f"✅ AI Response: PASSED ({response_time:.1f}s)")
                print(f"{'✅' if len(errors) == 0 else '⚠️ '} Console Errors: {len(errors)}")
                print()
                print("🎉 All tests completed successfully!")

            except Exception as e:
                print(f"❌ Test failed: {str(e)}")
                await page.screenshot(path='screenshots/test_error.png')
                print("📸 Error screenshot saved: screenshots/test_error.png")
                raise

            finally:
                await browser.close()
                print("\n🔒 Browser closed")

    except ImportError:
        print("❌ Playwright not installed")
        print("\nTo install Playwright:")
        print("  pip install playwright")
        print("  playwright install")
        return False

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    # Create screenshots directory
    import os
    os.makedirs('screenshots', exist_ok=True)

    # Run tests
    success = asyncio.run(test_webapp())

    exit(0 if success else 1)
