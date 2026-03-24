name: PMD Temperature Scraper

on:
  schedule:
    - cron: '0 3 * * *'     # Runs every day at 3:00 AM UTC (adjust as needed)
  workflow_dispatch:        # Allows manual trigger from GitHub

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 10     # Safety timeout

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        run: |
          pip install playwright pandas openpyxl

      - name: Install Playwright Browsers (Chromium + system deps)
        run: |
          python -m playwright install chromium --with-deps

      - name: Run the scraper
        run: python your_script_name.py     # ← Change to your actual filename (e.g. scrape_max_temp.py)

      - name: Commit and push updated Excel (optional but useful)
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add PMD_Max_Temperatures.xlsx
          git commit -m "Update PMD Max Temperatures - $(date)" || echo "No changes to commit"
          git push
        continue-on-error: true
