import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

async def scrape_ncm():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set a very tall window to capture the entire table
        await page.set_viewport_size({"width": 1366, "height": 4500})
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            
            print("⏳ Page reached. Waiting 20 seconds for table data...")
            await asyncio.sleep(20) 

            print("🧹 Digitally erasing the cookie banner...")
            # This part is now simplified to avoid Syntax Errors
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

            timestamp = datetime.now().strftime("%Y-%m-%d")
            screenshot_name = f"ncm_snapshot_{timestamp}.png"
            
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
