import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- TARGETING YOUR 2026 FOLDER ---
# This ID matches your URL: https://drive.google.com/drive/folders/1LtTNFcK85lDexO9ZQjGArlIdhUaeFBy5
FOLDER_ID = "1LtTNFcK85lDexO9ZQjGArlIdhUaeFBy5" 

def upload_to_drive(file_path):
    print(f"🚀 Initializing Google Drive Upload...")
    try:
        if "GDRIVE_SERVICE_ACCOUNT_KEY" not in os.environ:
            print("❌ ERROR: GDRIVE_SERVICE_ACCOUNT_KEY not found in GitHub Secrets!")
            return

        service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_KEY"])
        
        # SCOPES: Explicitly requesting full Drive access to see folders shared with the account
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
        
        # supportsAllDrives=True: CRITICAL for folders shared with the Service Account
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, parents',
            supportsAllDrives=True 
        ).execute()
        
        print(f"✅ SUCCESS: {file.get('name')} is now in your 2026 folder.")
        print(f"🆔 File ID: {file.get('id')}")

    except Exception as e:
        print(f"❌ DRIVE ERROR: {e}")

async def scrape_ncm_to_pdf():
    async with async_playwright() as p:
        # Stability arguments for running in a GitHub Actions environment
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()
        
        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Connecting to NCM UAE Weather Portal...")
        
        try:
            # domcontentloaded helps avoid timeouts on slow government servers
            await page.goto(url, wait_until="domcontentloaded", timeout=180000)
            
            print("⏳ Waiting for weather data table to render...")
            await asyncio.sleep(15) 

            # Clean the page by removing headers/footers for a better PDF
            await page.evaluate("""
                document.querySelectorAll('header, footer, .cookie-bar, .header, .footer, #top-nav').forEach(el => el.remove());
            """)

            # Filename with Pakistan Standard Time (PKT)
            pkt_now = datetime.utcnow() + timedelta(hours=5)
            timestamp = pkt_now.strftime('%Y-%m-%d_%H-%M-%S')
            pdf_name = f"ncm_report_{timestamp}_PKT.pdf"
            
            print(f"📄 Creating PDF: {pdf_name}")
            await page.pdf(
                path=pdf_name, 
                format="A4", 
                print_background=True,
                margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
            )
            
            if os.path.exists(pdf_name):
                upload_to_drive(pdf_name)
            else:
                print("❌ PDF creation failed locally on the GitHub server.")
            
        except Exception as e:
            print(f"❌ SCRAPE ERROR: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ncm_to_pdf())
