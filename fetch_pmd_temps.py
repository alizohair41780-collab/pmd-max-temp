import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- UPDATED 2026 FOLDER ID ---
FOLDER_ID = "1LtTNFcK85IDexO9ZQjGArlldhUaeFBy5" 

def upload_to_drive(file_path):
    print(f"🚀 Initializing Google Drive Upload...")
    try:
        service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_KEY"])
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        service = build('drive', 'v3', credentials=credentials)
        
        # We target the 2026 folder directly
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [FOLDER_ID]
        }
        
        media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, parents'
        ).execute()
        
        print(f"✅ SUCCESS: {file.get('name')} is now in your 2026 folder.")
        print(f"🆔 File ID: {file.get('id')}")

    except Exception as e:
        print(f"❌ DRIVE ERROR: {e}")

async def scrape_ncm_to_pdf():
    async with async_playwright() as p:
        # Launching with stability args
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Connecting to NCM UAE Weather Portal...")
        
        try:
            # Using domcontentloaded to prevent timeout on slow government servers
            await page.goto(url, wait_until="domcontentloaded", timeout=180000)
            
            print("⏳ Loading weather data table...")
            await asyncio.sleep(15) # Wait for JavaScript to render the rows

            # Clean the page by removing clutter
            await page.evaluate("""
                document.querySelectorAll('header, footer, .cookie-bar, .header, .footer, #top-nav').forEach(el => el.remove());
            """)

            # Time formatting for filename (Pakistan Standard Time)
            pkt_now = datetime.utcnow() + timedelta(hours=5)
            pdf_name = f"ncm_report_{pkt_now.strftime('%Y-%m-%d_%H-%M-%S')}_PKT.pdf"
            
            print(f"📄 Creating publication-ready PDF...")
            await page.pdf(
                path=pdf_name, 
                format="A4", 
                print_background=True,
                margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
            )
            
            if os.path.exists(pdf_name):
                upload_to_drive(pdf_name)
            
        except Exception as e:
            print(f"❌ SCRAPE ERROR: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm_to_pdf())
