import pandas as pd
from datetime import datetime
from database.db import connect_sheet
from scraper.google import search_google
from ai.validator import validate_with_ai


def run_engine():

    sheet = connect_sheet()
    now = datetime.utcnow()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        # =============================
        # LOAD COMPANIES
        # =============================
        companies_data = sheet.worksheet("Companies").get_all_records()
        companies_df = pd.DataFrame(companies_data)

        if companies_df.empty:
            log(sheet, "INFO", "No companies found.")
            return

        companies_df["Active"] = (
            companies_df["Active"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        active_companies = companies_df[
            companies_df["Active"] == "yes"
        ]

        if active_companies.empty:
            log(sheet, "INFO", "No active companies to scan.")
            return

        # =============================
        # LOAD EXISTING SIGNALS
        # =============================
        signals_data = sheet.worksheet("Signals").get_all_records()
        signals_df = pd.DataFrame(signals_data)

        existing_urls = set()

        if not signals_df.empty and "Source URL" in signals_df.columns:
            existing_urls = set(signals_df["Source URL"].tolist())

        # =============================
        # SCAN ACTIVE COMPANIES
        # =============================
        for index, row in active_companies.iterrows():

            company = row["Company Name"]
            geography = row.get("Geography", "")
            official_domain = row.get("Official Domain", "")

            log(sheet, "INFO", f"Scanning {company}")

            query = f"{company} expansion OR acquisition OR funding OR tender OR leadership in {geography}"

            results = search_google(query)

            if not results:
                continue

            for article in results:

                url = article.get("link")

                if not url or url in existing_urls:
                    continue

                title = article.get("title", "")
                snippet = article.get("snippet", "")
                content = article.get("content", "")
                published_date = article.get("date", "")

                ai_result = validate_with_ai(company, title, snippet, content)

                if not ai_result:
                    continue

                if not ai_result.get("relevant"):
                    continue

                confidence = ai_result.get("confidence", 0)

                if confidence < 0.8:
                    continue

                event_type = ai_result.get("event_type", "")
                summary = ai_result.get("summary", "")

                # =============================
                # SAVE SIGNAL (CORRECT ORDER)
                # =============================
                row_to_save = [
                    company,               # Company Name
                    title,                 # Event Title
                    url,                   # Source URL
                    published_date,        # Published Date
                    event_type,            # Event Type
                    confidence,            # AI Confidence
                    summary,               # Event Summary
                    now_str,               # Detection Timestamp
                    "No"                   # Processed
                ]

                sheet.worksheet("Signals").append_row(row_to_save)

                existing_urls.add(url)

                log(sheet, "SUCCESS", f"Saved signal for {company}")

            # =============================
            # UPDATE LAST SCANNED
            # =============================
            update_last_scanned(sheet, company, now_str)

        log(sheet, "SUCCESS", "Scan completed successfully.")

    except Exception as e:
        log(sheet, "ERROR", str(e))


# =============================
# UPDATE LAST SCANNED
# =============================
def update_last_scanned(sheet, company_name, timestamp):

    companies_ws = sheet.worksheet("Companies")
    data = companies_ws.get_all_records()

    for idx, row in enumerate(data, start=2):  # row 1 is header
        if row["Company Name"] == company_name:
            companies_ws.update(f"F{idx}", timestamp)
            break


# =============================
# LOGGING FUNCTION
# =============================
def log(sheet, status, message):

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log_row = [
        timestamp,
        status,
        message
    ]

    sheet.worksheet("Logs").append_row(log_row)