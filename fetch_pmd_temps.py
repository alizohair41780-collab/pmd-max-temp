import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

async def scrape_ncm():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set a large viewport to ensure the whole table is rendered properly
        await page.set_viewport_size({"width": 1280, "height": 3000})
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            
            print("🍪 Looking for cookie banner...")
            # We wait up to 10 seconds specifically for the button to be clickable
            cookie_button = page.get_by_role("button", name="I Agree")
            try:
                await cookie_button.wait_for(state="visible", timeout=10000)
                await cookie_button.click()
                print("✅ Cookie banner clicked.")
                # Give it a second to disappear from the screen
                await asyncio.sleep(2) 
            except Exception:
                print("⚠️ Could not find or click cookie button, moving on...")

            print("⏳ Waiting 15 seconds for table data to settle...")
            await asyncio.sleep(15) 
            
            timestamp = datetime.now().strftime("%Y-%m-%d")
            screenshot_name = f"ncm_snapshot_{timestamp}.png"
            
            # Take a full page screenshot
            await page.screenshot(path=screenshot_name, full_page=True)
            print(f"📸 Screenshot saved: {screenshot_name}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm())
