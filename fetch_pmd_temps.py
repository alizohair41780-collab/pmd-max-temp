import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os

async def scrape_ncm():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set a very tall window for the full table
        await page.set_viewport_size({"width": 1366, "height": 4500})
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            
            print("⏳ Page reached. Waiting 20 seconds for data...")
            await asyncio.sleep(20) 

            print("🧹 Erasing cookie banners and sticky overlays...")
            await page.evaluate("""
                const selectors = ['.cookie-bar', '.cookie-notice', '#cookie-banner', '.modal-backdrop', '.modal'];
                selectors.forEach(s => {
                    const elements = document.querySelectorAll(s);
                    elements.forEach(el => el.remove());
                });

                const allDivs = document.querySelectorAll('div');
                allDivs.forEach(div => {
                    const style = window.getComputedStyle(div);
                    if (style.position === 'fixed' || style.position === 'sticky') {
                        div.remove();
                    }
                });
            """)
            
            await asyncio.sleep(2) 

            # --- PAKISTAN TIME CALCULATION ---
            # GitHub runs on UTC. PKT is UTC + 5 hours.
            pkt_time = datetime.now() + timedelta(hours=5)
            
            # This creates a name like: ncm_snapshot_2026-03-24 (03.00 PM PKT).png
            timestamp_str = pkt_time.strftime("%Y-%m-%d (%I.%M %p PKT)")
            screenshot_name = f"ncm_snapshot_{timestamp_str}.png"
            
            print(f"📸 Taking screenshot: {screenshot_name}")
            await page.screenshot(path=screenshot_name, full_page=True)
            
            if os.path.exists(screenshot_name):
                print(f"✅ Success! Saved as {screenshot_name}")
            
        except Exception as e:
            print(f"❌ Error during scrape: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm())
