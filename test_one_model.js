const { chromium } = require('playwright');

(async () => {
    const modelName = process.argv[2] || 'Xenova/pythia-14m';
    const timeout = 120000;

    console.log(`Testing model: ${modelName}`);

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();

    let result = {
        model: modelName,
        status: 'unknown',
        error: null,
        loadTime: null,
        generateTime: null,
        output: null
    };

    try {
        page.setDefaultTimeout(timeout);

        // Listen to console logs (only errors to stderr)
        page.on('console', msg => {
            if (msg.type() === 'error') {
                console.error(`[ERROR] ${msg.text()}`);
            }
        });

        // Navigate to test page
        await page.goto('http://localhost:8080/test_single_model.html');

        // Set model name
        await page.fill('#modelName', modelName);

        // Start test
        await page.click('#startTest');

        // Wait for actual result (not just "Testing...")
        await page.waitForFunction(() => {
            const resultEl = document.getElementById('result');
            const text = resultEl ? resultEl.textContent : '';
            return text && text !== 'Testing...' && (text.includes('SUCCESS') || text.includes('FAILED'));
        }, { timeout: timeout });

        // Get result
        const resultText = await page.textContent('#result');
        const loadTime = await page.textContent('#loadTime');
        const generateTime = await page.textContent('#generateTime');
        const output = await page.textContent('#output');

        if (resultText.includes('SUCCESS')) {
            result.status = 'success';
            result.loadTime = loadTime;
            result.generateTime = generateTime;
            result.output = output;
        } else {
            result.status = 'failed';
            result.error = resultText;
        }

    } catch (error) {
        result.status = 'error';
        result.error = error.message;
    } finally {
        await browser.close();
        // Output only JSON on the last line for easy parsing
        console.log('__JSON_START__');
        console.log(JSON.stringify(result));
        console.log('__JSON_END__');
    }
})();
