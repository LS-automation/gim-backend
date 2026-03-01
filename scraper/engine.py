from datetime import datetime
from scraper.google import search_google
from database.db import (
    get_active_companies,
    get_existing_urls,
    save_signal,
    save_log,
)
from ai.validator import validate_with_ai


def run_engine():

    try:
        companies = get_active_companies()
        existing_urls = get_existing_urls()

        for company in companies:
            company_name = company["company_name"]

            results = search_google(company_name)

            for article in results:

                if not article["link"]:
                    continue

                # Skip duplicates
                if article["link"] in existing_urls:
                    continue

                ai_result = validate_with_ai(
                    company_name,
                    article["title"],
                    article["snippet"]
                )

                if not ai_result["is_valid"]:
                    continue

                signal_row = [
                    company_name,
                    article["title"],
                    article["link"],
                    article["date"],
                    ai_result["event_type"],
                    ai_result["confidence"],
                    ai_result["summary"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "No"
                ]

                save_signal(signal_row)

        save_log([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "SUCCESS",
            "Engine run completed"
        ])

    except Exception as e:
        save_log([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ERROR",
            str(e)
        ])