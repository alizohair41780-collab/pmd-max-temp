import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

async def scrape_ncm():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set a tall viewport to ensure the full table is rendered
        await page.set_viewport_size({"width": 1366, "height": 4000})
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            # Navigate with a generous timeout for the heavy NCM site
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            
            print("⏳ Page reached. Waiting 20 seconds for table data to fully load...")
            await asyncio.sleep(20) 

            # --- THE FIX: DIGITALLY ERASE THE COOKIE BANNER AND OVERLAYS ---
            print("🧹 Cleaning up the page (removing cookie banners and overlays)...")
            await page.evaluate("""
                // Identify common selectors for the NCM cookie bar and general overlays
                const selectors = [
                    '.cookie-bar', 
                    '.cookie-notice', 
                    '#cookie-banner', 
                    '.modal-backdrop', 
                    '.modal'
                ];
                
                selectors.forEach(s => {
                    const elements = document.querySelectorAll(s);
                    elements.forEach(el => el.remove());
                });

                # This specifically targets the "Sticky" bar hiding your data
                const allDivs = document.querySelectorAll('div');
                allDivs.forEach(div => {
                    const style = window.getComputedStyle(div);
                    if (style.position === 'fixed' || style.position === 'sticky') {
                        div.remove();
                    }
                });
            """)
            
            # Short pause to let the layout settle after removal
            await asyncio.sleep(2) 

            # Generate filename with date
            timestamp = datetime.now().strftime("%Y-%m-%d")
            screenshot_name = f"ncm_snapshot_{timestamp}.png"
            
            # Take the full-page screenshot
            print(f"📸 Taking screenshot: {screenshot_name}")
            await page.screenshot(path=screenshot_name, full_page=True)
            
            if os.path.exists(screenshot_name):
                print(f"✅ Success! Screenshot saved and verified.")
            
        except Exception as e:
            print(f"❌ Error during scrape: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm())
