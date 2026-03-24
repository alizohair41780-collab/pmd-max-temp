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
        
        # Wait for the page to load
        await page.goto(url, wait_until="networkidle")
        
        # Give the table 10 seconds to fully appear
        print("⏳ Waiting for data to stabilize...")
        await asyncio.sleep(10) 
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        screenshot_name = f"ncm_snapshot_{timestamp}.png"
        
        # Take the screenshot
        await page.screenshot(path=screenshot_name, full_page=True)
        print(f"📸 Screenshot saved: {screenshot_name}")
        
        # Ensure the file actually exists on the disk before closing
        if os.path.exists(screenshot_name):
            print("✅ File confirmed on disk.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm())
