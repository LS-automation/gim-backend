from scraper.google import search_google
from scraper.website import extract_content
from ai.validator import validate_with_ai
from database.db import (
    get_active_companies,
    get_existing_urls,
    save_signals_batch,
    log_message,
    update_last_scanned_bulk
)
from config import CONFIDENCE_THRESHOLD
from datetime import datetime

def run_engine():

    log_message("Engine Started")

    companies = get_active_companies()
    existing_urls = get_existing_urls()

    all_signals = []
    scanned_companies = []

    for company_data in companies:

        company = company_data["Company Name"]
        scanned_companies.append(company)

        log_message(f"Scanning {company}")

        results = search_google(company)

        for article in results:

            if article["link"] in existing_urls:
                continue

            content = extract_content(article["link"])
            if not content:
                continue

            ai_result = validate_with_ai(company, content)
            if not ai_result:
                continue

            if not ai_result["relevant"]:
                continue

            if float(ai_result["confidence"]) < CONFIDENCE_THRESHOLD:
                continue

            signal_row = [
                company,
                article["title"],
                article["link"],
                article.get("date", ""),
                ai_result["event_type"],
                float(ai_result["confidence"]),
                ai_result["summary"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "No"
            ]

            all_signals.append(signal_row)

    # 🔥 SAVE EVERYTHING AT ONCE
    save_signals_batch(all_signals)

    # 🔥 UPDATE LAST SCANNED ONCE
    update_last_scanned_bulk(scanned_companies)

    log_message("Engine Finished")