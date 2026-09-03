import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# YOUR PERSONAL EMAIL (kept for reference; not used for ownership transfer anymore)
USER_EMAIL = "alizohair3173@gmail.com"

# The Google Drive folder ID that is shared with the service account (Editor access)
FOLDER_ID = "1wN8BNnwAYOLspRmlBGnxfH5vaUsMfbWL"


def upload_to_drive(file_path):
    print(f"🚀 Initializing Simple Stream Upload...")
    try:
        service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_KEY"])
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=credentials)

        # Upload directly into the shared folder so storage is charged to YOUR account,
        # not the service account (which has 0 storage quota of its own).
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [FOLDER_ID]
        }

        media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=False)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        file_id = file.get('id')
        print(f"✅ File Created! ID: {file_id}")
        print(f"📧 File is now in your shared Drive folder. Check Google Drive!")

    except Exception as e:
        print(f"❌ DRIVE ERROR: {e}")
        if "storageQuotaExceeded" in str(e):
            print("💡 QUOTA ALERT: Make sure FOLDER_ID points to a folder YOU own,")
            print("   and that it's shared with the service account's email as Editor.")


async def scrape_ncm_to_pdf():
    async with async_playwright() as p:
        # Optimized for GitHub Actions
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 1280, "height": 1000})
        page = await context.new_page()

        url = "https://www.ncm.gov.ae/services/climate-reports-daily?lang=en"
        print(f"🔗 Connecting to NCM UAE...")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=180000)
            await asyncio.sleep(15)  # Wait for table data

            # Clean the page
            await page.evaluate("document.querySelectorAll('header, footer, .cookie-bar').forEach(el => el.remove())")

            # PKT Timestamp
            pkt_now = datetime.utcnow() + timedelta(hours=5)
            pdf_name = f"ncm_report_{pkt_now.strftime('%Y-%m-%d_%H-%M')}_PKT.pdf"

            print(f"📄 Creating PDF...")
            await page.pdf(path=pdf_name, format="A4", print_background=True)

            if os.path.exists(pdf_name):
                upload_to_drive(pdf_name)

        except Exception as e:
            print(f"❌ SCRAPE ERROR: {e}")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(scrape_ncm_to_pdf())
