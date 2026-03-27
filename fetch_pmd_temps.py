import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# YOUR PERSONAL EMAIL
USER_EMAIL = "alizohair3173@gmail.com"

def upload_to_drive(file_path):
    print(f"🚀 Initializing Hand-off Upload...")
    try:
        service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_KEY"])
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, 
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {'name': os.path.basename(file_path)}
        media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=False)
        
        # Step 1: Create the file in the service account's space
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = file.get('id')
        print(f"✅ Created File ID: {file_id}")

        # Step 2: Share it with your personal email immediately
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': USER_EMAIL
        }
        service.permissions().create(fileId=file_id, body=permission).execute()
        print(f"📧 Permission granted to {USER_EMAIL}. Check 'Shared with me'!")

    except Exception as e:
        print(f"❌ DRIVE ERROR: {e}")

async def scrape_ncm_to_pdf():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        try:
            url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
            await page.goto(url, wait_until="domcontentloaded", timeout=120000)
            await asyncio.sleep(15)
            await page.evaluate("document.querySelectorAll('header, footer, .cookie-bar').forEach(el => el.remove())")
            
            pkt_now = datetime.utcnow() + timedelta(hours=5)
            pdf_name = f"ncm_report_{pkt_now.strftime('%Y-%m-%d_%H-%M')}_PKT.pdf"
            await page.pdf(path=pdf_name, format="A4", print_background=True)
            
            if os.path.exists(pdf_name):
                upload_to_drive(pdf_name)
        except Exception as e:
            print(f"❌ SCRAPE ERROR: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm_to_pdf())
