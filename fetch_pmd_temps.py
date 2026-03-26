import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- TARGETING YOUR 2026 FOLDER ---
FOLDER_ID = "1LtTNFcK85IDexO9ZQjGArlldhUaeFBy5"

def upload_to_drive(file_path):
    print(f"🚀 Starting Drive upload process...")
    try:
        service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_KEY"])
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [FOLDER_ID]
        }
        
        media = MediaFileUpload(file_path, mimetype='application/pdf')
        
        # We add 'supportsAllDrives=True' to ensure it can write to shared folders
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, parents',
            supportsAllDrives=True 
        ).execute()
        
        print(f"✅ Success! File ID: {file.get('id')}")
        
    except Exception as e:
        print(f"❌ DRIVE ERROR: {e}")

async def scrape_ncm_to_pdf():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to NCM...")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=180000)
            await asyncio.sleep(15) # Allow data to load

            # Remove clutter for clean PDF
            await page.evaluate("document.querySelectorAll('header, footer, .cookie-bar').forEach(el => el.remove())")

            # Filename with PKT time
            pkt_now = datetime.utcnow() + timedelta(hours=5)
            pdf_name = f"ncm_report_{pkt_now.strftime('%Y-%m-%d_%H-%M')}.pdf"
            
            print(f"📄 Generating PDF...")
            await page.pdf(path=pdf_name, format="A4", print_background=True)
            
            if os.path.exists(pdf_name):
                upload_to_drive(pdf_name)
            
        except Exception as e:
            print(f"❌ SCRAPE ERROR: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm_to_pdf())
