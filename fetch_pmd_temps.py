import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os

async def scrape_ncm():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 1366, "height": 3000})
        page = await context.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            # 1. Go to the URL
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            
            # 2. Wait for the button to exist and click it
            print("⏳ Searching for cookie button...")
            try:
                # This waits up to 10 seconds for the button to appear
                agree_selector = "text='I Agree'"
                await page.wait_for_selector(agree_selector, timeout=10000)
                await page.click(agree_selector)
                print("✅ Button clicked successfully.")
            except:
                print("⚠️ Button didn't appear in time, proceeding to manual hide.")

            # 3. Extra manual cleaning of the page
            print("🧹 Hiding all potential overlays...")
            await page.evaluate("""
                const hideSelectors = [
                    '.cookie-bar', '.cookie-notice', '#cookie-banner', 
                    '.modal-backdrop', '.modal', '.cc-window', '.cc-banner',
                    'div[class*="cookie"]', 'div[id*="cookie"]', '.header', '.footer'
                ];
                hideSelectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                    });
                });
                // Force the body to be scrollable and remove blur
                document.body.style.overflow = 'auto';
                document.documentElement.style.overflow = 'auto';
            """)

            # Small wait to let the animations finish
            await asyncio.sleep(3) 
            
            # 4. Save the file
            pkt_time = datetime.utcnow() + timedelta(hours=5)
            timestamp_str = pkt_time.strftime("%Y-%m-%d (%I.%M %p PKT)")
            screenshot_name = f"ncm_snapshot_{timestamp_str}.png"
            
            print(f"📸 Capturing screenshot: {screenshot_name}")
            await page.screenshot(path=screenshot_name, full_page=True)
            
            if os.path.exists(screenshot_name):
                print(f"✅ Success! Saved as {screenshot_name}")
            
        except Exception as e:
            print(f"❌ Error during scrape: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm())
