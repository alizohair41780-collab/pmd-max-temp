import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- UPDATED FOLDER ID FROM YOUR URL ---
# URL: https://drive.google.com/drive/folders/1LtTNFcK85lDexO9ZQjGArlIdhUaeFBy5
FOLDER_ID = "1LtTNFcK85lDexO9ZQjGArlIdhUaeFBy5" 

def upload_to_drive(file_path):
    print(f"🚀 Initializing Google Drive Upload...")
    try:
        if "GDRIVE_SERVICE_ACCOUNT_KEY" not in os.environ:
            print("❌ ERROR: Secrets not found!")
            return

        service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_KEY"])
        print(f"👤 Acting as Service Account: {service_account_info.get('client_email')}")
        
        scopes = ['https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, 
            scopes=scopes
        )
        
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [FOLDER_ID]
        }
        
        media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
        
        # supportsAllDrives=True is required since the folder is "Shared with me"
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name',
            supportsAllDrives=True 
        ).execute()
        
        print(f"✅ SUCCESS! File is now in Drive.")
        print(f"🆔 File ID: {file.get('id')}")

    except Exception as e:
        print(f"❌ DRIVE ERROR: {e}")

async def scrape_ncm_to_pdf():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Navigating to NCM...")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=180000)
            await asyncio.sleep(15) 

            # Remove website clutter
            await page.evaluate("document.querySelectorAll('header, footer, .cookie-bar').forEach(el => el.remove())")

            # Timestamp for filename (Pakistan Standard Time)
            pkt_now = datetime.utcnow() + timedelta(hours=5)
            pdf_name = f"ncm_report_{pkt_now.strftime('%Y-%m-%d_%H-%M')}_PKT.pdf"
            
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
