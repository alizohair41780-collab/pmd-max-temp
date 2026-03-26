import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os

async def scrape_ncm_to_pdf():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        # Standard desktop view for better PDF layout
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=120000)
            
            # --- 1. DISMISS COOKIES ---
            print("⏳ Handling cookie banner...")
            try:
                await page.click("text='I Agree'", timeout=5000)
                await asyncio.sleep(2)
            except:
                pass

            # --- 2. SCROLL TO LOAD ALL DATA ---
            print("📜 Scrolling to wake up all table rows...")
            for _ in range(12): 
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(0.8)

            # --- 3. HIDE OVERLAYS (STOPS THEM COVERING TEXT) ---
            print("🧹 Cleaning page for PDF print...")
            await page.evaluate("""
                const hideSelectors = [
                    '.cookie-bar', '.cookie-notice', '#cookie-banner', 
                    '.modal-backdrop', '.modal', '.cc-window', '.cc-banner',
                    'header', 'footer', '.header', '.footer', '#top-nav'
                ];
                hideSelectors.forEach(s => {
                    document.querySelectorAll(s).forEach(el => el.style.display = 'none');
                });
            """)

            # --- 4. SAVE AS COPYABLE PDF ---
            pkt_time = datetime.utcnow() + timedelta(hours=5)
            timestamp_str = pkt_time.strftime("%Y-%m-%d (%I.%M %p PKT)")
            pdf_name = f"ncm_report_{timestamp_str}.pdf"
            
            print(f"📄 Generating PDF: {pdf_name}")
            # print_background=True ensures the table colors stay
            await page.pdf(
                path=pdf_name, 
                format="A4", 
                print_background=True,
                margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"}
            )
            
            if os.path.exists(pdf_name):
                print(f"✅ Success! PDF saved: {pdf_name}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm_to_pdf())
