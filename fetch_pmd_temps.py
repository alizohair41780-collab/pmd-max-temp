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
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            
            # --- NEW: CLICK THE COOKIE BUTTON ---
            print("🍪 Attempting to clear the cookie banner...")
            try:
                # This looks for the "I Agree" button and clicks it
                await page.get_by_role("button", name="I Agree").click(timeout=5000)
                print("✅ Cookie banner dismissed.")
            except Exception:
                print("⚠️ Cookie banner not found or already gone.")

            print("⏳ Waiting 15 seconds for the table to render...")
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
