# Browser Cache Fix Guide

## ⚠️ Issue Identified

The error shows an attempt to load `onnx-community/Qwen2.5-1.5B`, which is **NOT** in our webapp. This is caused by:
1. **Browser cache** - Old HTML cached
2. **localStorage** - Old model selection saved
3. **IndexedDB** - Old Transformers.js cache

## ✅ Solution: Clear All Cache

### Option 1: Use Clear Cache Page (Recommended)

1. **Navigate to**: http://localhost:8080/clear_cache.html
2. **Click**: "Clear All & Reload" button
3. **Wait**: Page will auto-reload with fresh data
4. **Verify**: Default model should be "Xenova/distilgpt2 ⭐"

### Option 2: Manual Browser Clear (Chrome)

1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"
4. Go to Application tab
5. Clear:
   - localStorage
   - sessionStorage
   - IndexedDB
   - Cache Storage
6. Reload page

### Option 3: Incognito/Private Mode

1. Open **Incognito/Private window**
2. Navigate to: http://localhost:8080
3. Fresh session with no cache

### Option 4: Command Line Cache Bust

```bash
# Add cache-busting parameter
curl "http://localhost:8080/?nocache=$(date +%s)" > /tmp/test.html
cat /tmp/test.html | grep -c "Xenova/"
# Should show: 61
```

## 🔍 Verification Steps

After clearing cache:

### 1. Check HTML Source
```bash
curl -s http://localhost:8080 | grep "onnx-community"
# Should output: (nothing - no matches)

curl -s http://localhost:8080 | grep -c "Xenova/"
# Should output: 61
```

### 2. Check Default Model
Open http://localhost:8080 and verify:
- Default selected: "⭐ DistilGPT-2 (82M, ~150MB) - DEFAULT"
- Model ID: "Xenova/distilgpt2"
- Category: "⚡ Ultra Fast"

### 3. Check Model Count
- Open model dropdown
- Should see **16 categories**
- Should see **61 total models**
- Should see **0 onnx-community models**

### 4. Load Test
1. Wait for default model to load (5-10 seconds)
2. Should see: "Model loaded successfully!" or similar
3. Send test message: "Hello"
4. Should get response

## 🚫 What's NOT in the Webapp

These models are **EXCLUDED** because they don't have the correct ONNX structure:

- ❌ onnx-community/Qwen2.5-1.5B
- ❌ onnx-community/Qwen2.5-0.5B-Instruct
- ❌ onnx-community/Llama-3.2-1B-Instruct-ONNX
- ❌ onnx-community/TinyLlama-1.1B-Chat-v1.0-ONNX
- ❌ All other onnx-community/* models

## ✅ What's IN the Webapp

**All 61 Xenova models** with verified `decoder_model_merged_quantized.onnx` files:

- ✅ Xenova/distilgpt2 (DEFAULT)
- ✅ Xenova/gpt2
- ✅ Xenova/Qwen1.5-0.5B-Chat
- ✅ Xenova/TinyLlama-1.1B-Chat-v1.0
- ✅ Xenova/stablelm-2-zephyr-1_6b
- ✅ ... 56 more Xenova models

## 🔧 If Still Having Issues

### Check Server is Serving Latest HTML

```bash
# Check file timestamp
ls -lh docs/index.html

# Check content
grep -A 5 'modelSelector' docs/index.html | head -20

# Restart server
pkill -f "http.server 8080"
cd docs && python3 -m http.server 8080 > /dev/null 2>&1 &

# Verify it's running
curl -s http://localhost:8080 | head -5
```

### Check for Cached JavaScript

The webapp uses:
```html
<script type="module" src="js/app.js"></script>
```

Clear browser's JavaScript cache:
1. DevTools → Network tab
2. Check "Disable cache" while DevTools is open
3. Reload

### Check localStorage Model Setting

Open DevTools Console and run:
```javascript
// Check saved model
console.log(localStorage.getItem('currentModel'));

// Clear saved model
localStorage.removeItem('currentModel');
localStorage.clear();

// Reload
location.reload();
```

## 📊 Expected Behavior

### On First Load:
1. Page loads with "⭐ DistilGPT-2" selected
2. Model starts downloading (~150MB)
3. Progress bar shows 0-100%
4. "Model loaded successfully!" appears
5. Ready to chat

### Model Dropdown:
- **16 categories** visible
- **61 models** total
- **All start with "Xenova/"**
- **None start with "onnx-community/"**

## ✅ Success Criteria

You know it's working when:
- ✅ No 404 errors in console
- ✅ Default model is Xenova/distilgpt2
- ✅ Model loads successfully
- ✅ Can send messages and get responses
- ✅ All 61 models are Xenova models

## 🎯 Final Check Command

```bash
# Verify HTML is correct
echo "Checking webapp HTML..."
curl -s http://localhost:8080 | grep -o 'value="[^"]*"' | sort | uniq | head -10

# Should show ONLY Xenova models like:
# value="Xenova/distilgpt2"
# value="Xenova/gpt2"
# etc.
```

## 🚀 Quick Recovery Script

```bash
#!/bin/bash
echo "🧹 Clearing all caches..."

# Kill old server
pkill -f "http.server 8080"

# Restart fresh server
cd /home/cc/claude_code/gpt2chat/docs
python3 -m http.server 8080 > /dev/null 2>&1 &

sleep 2

# Test
echo "✅ Server restarted"
echo "📊 Model count:"
curl -s http://localhost:8080 | grep -c "Xenova/"
echo "🚫 onnx-community count:"
curl -s http://localhost:8080 | grep -c "onnx-community" || echo "0"

echo ""
echo "✅ Open http://localhost:8080/clear_cache.html to clear browser cache"
echo "✅ Or use Incognito mode: http://localhost:8080"
```

Save as `fix_cache.sh` and run with `bash fix_cache.sh`
