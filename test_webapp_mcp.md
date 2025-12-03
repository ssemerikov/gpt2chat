# Web App Testing with MCP Playwright

## MCP Setup Status ✅

**Playwright MCP Server**: ✅ Connected
- **Command**: `npx -y @playwright/mcp@latest`
- **Transport**: stdio
- **Status**: Active and ready

## Configuration Files

### 1. Local Configuration
- **Location**: `/home/cc/.claude.json`
- **Scope**: User-specific settings for this project
- **Auto-created**: Yes

### 2. Project Configuration (Team Sharing)
- **Location**: `/home/cc/claude_code/gpt2chat/.mcp.json`
- **Purpose**: Track in git for team collaboration
- **Created**: Yes ✅

## Available Testing Capabilities

With Playwright MCP, you can now:

### 🌐 Browser Automation
- Navigate to web pages
- Click buttons and interact with elements
- Fill forms and input fields
- Take screenshots
- Execute JavaScript in browser context

### 🧪 Testing Features
- Automated UI testing
- E2E (End-to-End) testing
- Web scraping and data extraction
- Performance monitoring
- Accessibility audits

### 📸 Visual Testing
- Capture full-page screenshots
- Element-specific screenshots
- Visual regression testing
- Error state documentation

## Test Cases for GPT-2 Chat App

### Test 1: Page Load & Initial State
**Objective**: Verify the app loads correctly

**Steps**:
1. Navigate to http://localhost:8080
2. Wait for page load
3. Take screenshot of initial state
4. Verify welcome message is visible
5. Check model selector is present
6. Verify default model is Xenova/distilgpt2

**Expected Result**: Page loads, all UI elements present

---

### Test 2: Model Loading (Verified Model)
**Objective**: Test loading a confirmed working model

**Steps**:
1. Navigate to http://localhost:8080
2. Wait for model selector to be ready
3. Verify "Xenova/distilgpt2" is selected by default
4. Wait for "Model loaded successfully!" message (up to 30s)
5. Check console for errors
6. Take screenshot after model loads

**Expected Result**: Model loads without errors in 5-15 seconds

---

### Test 3: Send Message & Get Response
**Objective**: Verify end-to-end chat functionality

**Steps**:
1. Ensure model is loaded (Test 2)
2. Locate message input textarea
3. Type test message: "Hello, how are you?"
4. Click send button
5. Wait for response (up to 15s)
6. Verify response appears in chat
7. Take screenshot of conversation
8. Extract response text

**Expected Result**: AI responds with coherent text

---

### Test 4: Test All Verified Models
**Objective**: Verify all 3 verified models work

**Models to Test**:
- Xenova/distilgpt2 (default)
- Xenova/gpt2
- Xenova/stablelm-2-zephyr-1_6b

**Steps for Each**:
1. Select model from dropdown
2. Wait for loading progress bar
3. Wait for "Model loaded successfully!"
4. Send test message: "What is 2+2?"
5. Verify response
6. Take screenshot
7. Record load time and response quality

**Expected Result**: All 3 models load and respond correctly

---

### Test 5: Test onnx-community Models (New)
**Objective**: Test if latest Transformers.js supports new models

**Models to Test**:
- onnx-community/Qwen2.5-1.5B
- onnx-community/Llama-3.2-1B-Instruct-ONNX
- onnx-community/Qwen2.5-0.5B-Instruct

**Steps for Each**:
1. Select model from dropdown
2. Watch loading progress
3. Check console for "Could not locate file" errors
4. If loads: Send test message and verify response
5. If fails: Document exact error message
6. Take screenshot of success or error state

**Expected Result**: Document which models work with latest Transformers.js

---

### Test 6: UI Responsiveness
**Objective**: Test UI elements and interactions

**Steps**:
1. Test sidebar toggle
2. Create new chat
3. Test language toggle (EN/UK)
4. Adjust temperature slider (verify value updates)
5. Adjust max length slider
6. Test download JSON button
7. Test download TXT button
8. Test upload conversation button

**Expected Result**: All UI controls work as expected

---

### Test 7: Conversation Persistence
**Objective**: Verify localStorage conversation saving

**Steps**:
1. Send 3 messages in a chat
2. Extract conversation from localStorage
3. Refresh page
4. Verify conversation reappears
5. Create new chat
6. Verify conversations list updates
7. Switch between conversations

**Expected Result**: Conversations persist across page reloads

---

### Test 8: Error Handling
**Objective**: Test error scenarios

**Steps**:
1. Try to send empty message (should be prevented)
2. Try to send message before model loads
3. Disconnect internet and try to load new model
4. Test with very long input (>2000 chars)
5. Test rapid-fire message sending

**Expected Result**: Graceful error handling, user-friendly messages

---

### Test 9: Mobile Responsiveness
**Objective**: Test on mobile viewport

**Steps**:
1. Set viewport to mobile (375x667)
2. Verify sidebar behavior
3. Test mobile menu toggle
4. Verify chat input is usable
5. Test scrolling behavior
6. Take mobile screenshots

**Expected Result**: UI adapts to mobile screen size

---

### Test 10: Performance Monitoring
**Objective**: Measure app performance

**Metrics to Capture**:
- Initial page load time
- Model download time (per model)
- Model initialization time
- First response time
- Subsequent response times
- Memory usage
- Network requests

**Expected Result**: Document performance baseline for each model

---

## How to Run Tests with MCP

### Manual Testing (Using Claude Code)

You can now ask Claude Code to run these tests using natural language:

```
Use Playwright to test the web app at http://localhost:8080:
1. Take a screenshot of the initial page
2. Wait for the model to load
3. Send a test message
4. Capture the response
```

### Example Test Commands

**Basic Screenshot**:
```
Use Playwright MCP to navigate to http://localhost:8080 and take a screenshot
```

**Interactive Test**:
```
Use Playwright to:
1. Open http://localhost:8080
2. Wait for model to load (look for "Model loaded successfully")
3. Type "Hello world" in the message input
4. Click send button
5. Wait for response
6. Take a screenshot and show me the response
```

**Model Comparison Test**:
```
Test all 3 verified models (distilgpt2, gpt2, stablelm):
- For each model, send the same test prompt
- Measure response time
- Compare response quality
- Create a comparison table
```

**Bug Hunting**:
```
Test the onnx-community/Qwen2.5-1.5B model:
- Select it from dropdown
- Watch console for errors
- Document if it loads successfully with latest Transformers.js
- If it fails, capture the exact error message
```

---

## Verification Commands

### Check MCP Status
```bash
claude mcp list
```

### View Configuration
```bash
claude mcp get playwright
```

### View Tools Available
MCP tools will appear in Claude Code's tool list with `mcp__playwright__` prefix once Playwright is active.

---

## Advanced Testing

### Console Log Monitoring
```javascript
// Playwright can capture console logs
page.on('console', msg => console.log(msg.text()));
```

### Network Traffic Analysis
```javascript
// Monitor network requests
page.on('request', request => console.log(request.url()));
page.on('response', response => console.log(response.status()));
```

### JavaScript Execution
```javascript
// Execute custom JS in browser
await page.evaluate(() => {
  return document.querySelector('#statusIndicator').textContent;
});
```

---

## Expected Outcomes

### Verified Working Models (Should Pass)
✅ **Xenova/distilgpt2** - Loads in 5-10s, fast responses
✅ **Xenova/gpt2** - Loads in 10-15s, good quality
✅ **Xenova/stablelm-2-zephyr-1_6b** - Loads in 30-60s, best quality

### onnx-community Models (To Be Tested)
⚠️ **Need testing with latest Transformers.js**:
- Qwen2.5-1.5B
- Llama-3.2-1B-Instruct-ONNX
- Qwen2.5-0.5B-Instruct
- TinyLlama-1.1B-Chat-v1.0-ONNX
- All other onnx-community models

---

## Troubleshooting

### MCP Server Not Responding
```bash
# Restart MCP connection
claude mcp remove playwright
claude mcp add --transport stdio playwright -- npx -y @playwright/mcp@latest
```

### Browser Not Launching
- Ensure Playwright browsers are installed: `npx playwright install`
- Check system dependencies: `npx playwright install-deps`

### Timeout Errors
```bash
# Increase timeout (in milliseconds)
export MCP_TIMEOUT=60000
```

### Permission Issues
```bash
# Fix npm permissions
sudo chown -R $USER:$USER ~/.npm
```

---

## Next Steps

1. ✅ **MCP Setup Complete** - Playwright is configured and ready
2. 🧪 **Run Test Suite** - Use Claude Code to execute the test cases above
3. 📊 **Document Results** - Record which models work/fail
4. 🔄 **Update TESTING.md** - Add confirmed working models
5. 🐛 **Fix Issues** - Address any bugs found during testing

---

## Server Information

- **Web App URL**: http://localhost:8080
- **Server Process**: Running on port 8080 (python3 -m http.server)
- **Default Model**: Xenova/distilgpt2
- **Transformers.js Version**: @latest (upgraded from 2.17.2)

---

## Test Results Template

```markdown
## Test Results - [Date]

### Model: [Model Name]
- **Load Time**: [X] seconds
- **Status**: ✅ Success / ❌ Failed
- **Error**: [If failed, error message]
- **Test Message**: "Hello, how are you?"
- **Response**: [AI response text]
- **Response Time**: [X] seconds
- **Quality**: [Good/Acceptable/Poor]
- **Screenshot**: [Link to screenshot]
- **Notes**: [Any observations]
```

---

Ready to start testing! Just ask Claude Code to run any of the test cases above using Playwright MCP.
