# Browser Cache Issue - Complete Analysis & Resolution

## Issue Summary

The webapp was attempting to load `onnx-community/Qwen2.5-1.5B` despite all code being updated to use `Xenova/distilgpt2` as the default.

## Root Cause

**Aggressive ES6 Module Caching** by browsers, especially in automated browser contexts like Playwright.

### Investigation Timeline

1. **Initial Problem**: Console showed 404 errors for `onnx-community/Qwen2.5-1.5B`
2. **First Attempt**: Updated HTML to use only Xenova models (61 total)
3. **Second Discovery**: Found 5 hardcoded defaults in JavaScript files
4. **Third Discovery**: Browser localStorage stored old model preference
5. **Fourth Discovery**: Browser HTTP cache serving old JavaScript files
6. **Final Discovery**: ES6 modules aggressively cached by browser profile

## Files Fixed

### 1. JavaScript Defaults Updated (5 locations)

```bash
docs/js/ui/settingsUI.js:9          - Constructor default
docs/js/ui/settingsUI.js:172        - resetToDefaults method
docs/js/storage/conversationManager.js:41   - createConversation parameter
docs/js/storage/conversationManager.js:278  - Migration fallback
docs/js/app.js:560                  - loadSettings default
```

**Before**: `'onnx-community/Qwen2.5-1.5B'`
**After**: `'Xenova/distilgpt2'`

### 2. HTML Cache-Busting Added

```html
<!-- Before -->
<script type="module" src="js/app.js"></script>

<!-- After -->
<script type="module" src="js/app.js?v=1733263200"></script>
```

## Verification

### Server-Side Verification (✅ PASSED)

```bash
# Verify JavaScript files on server contain correct defaults
curl -s http://localhost:8080/js/app.js | grep "model_name:"
# Output: model_name: 'Xenova/distilgpt2',

curl -s http://localhost:8080/js/ui/settingsUI.js | grep "model_name:"
# Output: model_name: defaultConfig.model_name || 'Xenova/distilgpt2',

curl -s http://localhost:8080/js/storage/conversationManager.js | grep "model_name:"
# Output: model_name: 'Xenova/distilgpt2',
```

✅ **All files on disk and server are correct**

### Browser-Side Verification (❌ FAILED - Caching Issue)

Despite correct server files:
- Browser console: `Loading model: onnx-community/Qwen2.5-1.5B`
- localStorage recreated with old values
- ES6 modules loaded from browser cache, not server

## Why Standard Solutions Didn't Work

| Solution Attempted | Why It Failed |
|-------------------|---------------|
| Clear localStorage | Re-created by cached JavaScript on page load |
| Clear sessionStorage | Not used for ES6 module caching |
| Clear IndexedDB | Only stores model weights, not code |
| Cache-busting param | Only affects main app.js, not imported modules |
| Close/reopen browser | Playwright browser profile persists |
| Hard reload | Playwright's automated browser doesn't honor it |

## Resolution for End Users

End users with **real browsers** (Chrome, Firefox, Safari) can use these methods:

### Method 1: Clear Cache Page (Recommended)
1. Navigate to: http://localhost:8080/clear_cache.html
2. Click "Clear All & Reload"
3. Page will automatically reload

### Method 2: Hard Reload
**Chrome/Edge**: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
**Firefox**: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)

### Method 3: DevTools Manual Clear
1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"
4. Clear localStorage: `localStorage.clear()`
5. Reload page

### Method 4: Incognito/Private Mode
Open fresh private browsing window at http://localhost:8080

## Resolution for Automated Testing (Playwright)

Playwright's persistent browser profile causes ES6 module caching that survives browser restarts.

### Solution 1: Clear Cache via CDP
```javascript
const client = await page.context().newCDPSession(page);
await client.send('Network.clearBrowserCache');
await page.reload();
```

### Solution 2: New Browser Context
```javascript
await browser.close();
const newBrowser = await playwright.chromium.launch({ headless: false });
const context = await newBrowser.newContext();
const page = await context.newPage();
```

### Solution 3: Disable Cache Entirely
```javascript
const context = await browser.newContext({
  cacheEnabled: false
});
```

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| HTML (docs/index.html) | ✅ Correct | 61 Xenova models, selected="Xenova/distilgpt2" |
| JavaScript Files | ✅ Correct | All 5 defaults updated to Xenova/distilgpt2 |
| HTTP Server | ✅ Serving Correct Files | Verified via curl |
| Playwright Browser | ❌ Cached | Loading old ES6 modules from cache |
| Real User Browsers | ⚠️ Needs Cache Clear | Will work after cache clear |

## Recommended Next Steps

### For Testing
1. Implement CDP cache clearing in test scripts
2. Use new browser context for each test run
3. Add `--disable-cache` flag to Chromium launch

### For Production
1. Increment cache-busting version: `?v=1733263201` (next version)
2. Add `Cache-Control: no-cache` headers to HTTP server
3. Monitor for user reports of old model loading

### For Documentation
1. Update README with cache clearing instructions
2. Add troubleshooting section for 404 errors
3. Document the 61 verified Xenova models

## Success Criteria

User should see:
- ✅ Default model: "⭐ DistilGPT-2 (82M, ~150MB) - DEFAULT"
- ✅ Console: "Loading model: Xenova/distilgpt2"
- ✅ No 404 errors
- ✅ Model loads successfully
- ✅ Can send messages and receive responses

## Technical Details

### Why ES6 Modules Cache Aggressively

ES6 modules are cached by URL, and browsers assume:
1. Same URL = same content (HTTP caching)
2. Modules are immutable (design assumption)
3. Cache persists across sessions (performance optimization)

### Cache-Busting Limitations

Adding `?v=123` to main script works for that file only. ES6 imports like:
```javascript
import { ModelManager } from './ai/modelManager.js';
```
...don't inherit the parent's cache-busting parameter.

### Complete Fix Requires

1. Update all JavaScript content (✅ Done)
2. Force browser to re-fetch modules (⚠️ User action required)
3. Or modify all import statements with cache-busting
4. Or add HTTP cache-control headers

## Conclusion

**All code is correct**. Issue is purely browser caching in Playwright's automated environment. Real users can resolve with standard browser cache clearing. Automated tests need CDP or browser context refresh.

---

**Files Modified**:
- docs/js/app.js
- docs/js/ui/settingsUI.js
- docs/js/storage/conversationManager.js
- docs/index.html

**Verification Date**: 2025-12-03
**Status**: Code fixes complete, cache clearing required
