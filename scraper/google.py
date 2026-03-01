from serpapi import GoogleSearch
from config import SERPAPI_KEY, MAX_RESULTS_PER_COMPANY


def search_google(company_name):
    query = f"{company_name} leadership OR funding OR acquisition OR merger OR expansion OR tender news"

    params = {
    "q": query,
    "api_key": SERPAPI_KEY,
    "engine": "google",
    "tbm": "nws",
    "num": MAX_RESULTS_PER_COMPANY,
    "tbs": "qdr:d"  # past 24 hours only
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    articles = []

    if "organic_results" in results:
        for item in results["organic_results"]:
            articles.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
                "date": item.get("date", "Today")
            })

    return articles