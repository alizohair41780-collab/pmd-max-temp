import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os

async def scrape_ncm():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            # We increased the timeout to 120 seconds and changed the wait condition
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            
            print("⏳ Page reached. Waiting 15 seconds for the table to render...")
            await asyncio.sleep(15) 
            
            timestamp = datetime.now().strftime("%Y-%m-%d")
            screenshot_name = f"ncm_snapshot_{timestamp}.png"
            
            await page.screenshot(path=screenshot_name, full_page=True)
            print(f"📸 Screenshot saved: {screenshot_name}")
            
        except Exception as e:
            print(f"❌ Error during navigation: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm())
