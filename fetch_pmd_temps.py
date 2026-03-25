import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os

async def scrape_ncm():
    async with async_playwright() as p:
        # Added --disable-dev-shm-usage for stable runs in Linux/GitHub environments
        browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 1366, "height": 3000})
        page = await context.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            # Changed to networkidle to ensure data finishes loading
            await page.goto(url, wait_until="networkidle", timeout=120000)
            
            print("⏳ Waiting for table data to render...")
            await asyncio.sleep(15) 

            print("🧹 Clearing overlays...")
            await page.evaluate("""
                const selectors = ['.cookie-bar', '.cookie-notice', '#cookie-banner', '.modal-backdrop', '.modal', '.header', '.footer'];
                selectors.forEach(s => {
                    document.querySelectorAll(s).forEach(el => el.remove());
                });
            """)
            
            # --- ROBUST PAKISTAN TIME CALCULATION ---
            # We use UTC as a fixed baseline
            pkt_time = datetime.utcnow() + timedelta(hours=5)
            timestamp_str = pkt_time.strftime("%Y-%m-%d (%I.%M %p PKT)")
            screenshot_name = f"ncm_snapshot_{timestamp_str}.png"
            
            print(f"📸 Capturing screenshot: {screenshot_name}")
            # full_page=True can sometimes fail on very long pages; 
            # we use the set viewport height as a fallback
            await page.screenshot(path=screenshot_name, full_page=True)
            
            if os.path.exists(screenshot_name):
                file_size = os.path.getsize(screenshot_name)
                if file_size > 1000: # Ensure it's not an empty file
                    print(f"✅ Success! Saved as {screenshot_name} ({file_size} bytes)")
                else:
                    print("⚠️ Screenshot was captured but file size is suspiciously small.")
            
        except Exception as e:
            print(f"❌ Error during scrape: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm())
