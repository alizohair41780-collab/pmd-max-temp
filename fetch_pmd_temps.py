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
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            
            # --- 1. DISMISS COOKIES ---
            print("⏳ Handling cookie banner...")
            try:
                await page.click("text='I Agree'", timeout=5000)
            except:
                pass

            # --- 2. SCROLL TO LOAD ALL DATA ---
            print("📜 Scrolling to load the full table...")
            # This scrolls down the page in increments to trigger the website's loading
            for i in range(10): 
                await page.mouse.wheel(0, 800)
                await asyncio.sleep(1) # Give it a second to load the next chunk

            # --- 3. HIDE OVERLAYS ---
            print("🧹 Cleaning page elements...")
            await page.evaluate("""
                const hideSelectors = [
                    '.cookie-bar', '.cookie-notice', '#cookie-banner', 
                    '.modal-backdrop', '.modal', '.cc-window', '.cc-banner',
                    'header', 'footer', '.header', '.footer'
                ];
                hideSelectors.forEach(s => {
                    document.querySelectorAll(s).forEach(el => el.style.display = 'none');
                });
            """)

            # --- 4. TAKE SCREENSHOT ---
            pkt_time = datetime.utcnow() + timedelta(hours=5)
            timestamp_str = pkt_time.strftime("%Y-%m-%d (%I.%M %p PKT)")
            screenshot_name = f"ncm_snapshot_{timestamp_str}.png"
            
            print(f"📸 Capturing full page...")
            # full_page=True works better once we have scrolled down manually
            await page.screenshot(path=screenshot_name, full_page=True)
            
            if os.path.exists(screenshot_name):
                print(f"✅ Success! Full table saved as {screenshot_name}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm())
