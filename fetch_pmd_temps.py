import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os

async def scrape_ncm():
    async with async_playwright() as p:
        # Optimized for GitHub Actions resource limits
        browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 1366, "height": 3000})
        page = await context.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            # Wait for network to settle to ensure the table data loads
            await page.goto(url, wait_until="networkidle", timeout=120000)
            
            print("⏳ Waiting for table data to render...")
            await asyncio.sleep(15) 

            print("🧹 Clearing overlays and sticky headers...")
            await page.evaluate("""
                const selectors = ['.cookie-bar', '.cookie-notice', '#cookie-banner', '.modal-backdrop', '.modal', '.header', '.footer'];
                selectors.forEach(s => {
                    document.querySelectorAll(s).forEach(el => el.remove());
                });
            """)
            
            # --- PKT TIME CALCULATION ---
            # Baseline from UTC to ensure accuracy regardless of runner location
            pkt_time = datetime.utcnow() + timedelta(hours=5)
            timestamp_str = pkt_time.strftime("%Y-%m-%d (%I.%M %p PKT)")
            screenshot_name = f"ncm_snapshot_{timestamp_str}.png"
            
            print(f"📸 Capturing screenshot: {screenshot_name}")
            await page.screenshot(path=screenshot_name, full_page=True)
            
            if os.path.exists(screenshot_name):
                size = os.path.getsize(screenshot_name)
                print(f"✅ Success! Saved as {screenshot_name} ({size} bytes)")
            
        except Exception as e:
            print(f"❌ Error during scrape: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm())
