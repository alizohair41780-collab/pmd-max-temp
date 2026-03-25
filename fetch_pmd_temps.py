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
            # Wait for network to settle
            await page.goto(url, wait_until="networkidle", timeout=120000)
            
            print("⏳ Waiting for table data and cookie banner...")
            await asyncio.sleep(5) 

            # --- NEW: CLICK THE "I AGREE" BUTTON ---
            try:
                # This looks for the button and clicks it if it exists
                agree_button = page.get_by_role("button", name="I Agree")
                if await agree_button.is_visible():
                    await agree_button.click()
                    print("✅ Clicked 'I Agree' button.")
                    await asyncio.sleep(2) # Wait for it to fade out
            except Exception as e:
                print(f"⚠️ Could not click button (maybe already gone): {e}")

            print("🧹 Force-clearing any remaining overlays...")
            # This is a backup to remove the dark blur/bar even if the click fails
            await page.evaluate("""
                const selectors = [
                    '.cookie-bar', '.cookie-notice', '#cookie-banner', 
                    '.modal-backdrop', '.modal', '.cc-window', '.cc-banner',
                    '.header', '.footer'
                ];
                selectors.forEach(s => {
                    document.querySelectorAll(s).forEach(el => el.remove());
                });
                // Remove the 'blurred' effect if it exists on the body
                document.body.style.overflow = 'auto';
            """)
            
            # --- PKT TIME CALCULATION ---
            # Using utcnow() + 5 for PKT
            pkt_time = datetime.utcnow() + timedelta(hours=5)
            timestamp_str = pkt_time.strftime("%Y-%m-%d (%I.%M %p PKT)")
            screenshot_name = f"ncm_snapshot_{timestamp_str}.png"
            
            print(f"📸 Capturing screenshot: {screenshot_name}")
            # Focus on the main content area to avoid extra white space
            await page.screenshot(path=screenshot_name, full_page=True)
            
            if os.path.exists(screenshot_name):
                size = os.path.getsize(screenshot_name)
                print(f"✅ Success! Saved as {screenshot_name} ({size/1024:.2f} KB)")
            
        except Exception as e:
            print(f"❌ Error during scrape: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm())
