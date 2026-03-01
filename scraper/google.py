import requests
from config import SERPAPI_KEY, MAX_RESULTS_PER_COMPANY

# Domains we do NOT want (financial noise / stock blogs)
BLACKLIST_DOMAINS = [
    "marketbeat.com",
    "finviz.com",
    "seekingalpha.com",
    "zacks.com",
    "hdinresearch.com",
    "benzinga.com",
    "investing.com"
]


def search_google(company):

    # Strong corporate-event focused query
    query = f'"{company}" (expansion OR funding OR acquisition OR merger OR CEO OR CFO OR tender OR partnership OR joint venture OR plant opening OR new facility)'

    url = "https://serpapi.com/search.json"

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": MAX_RESULTS_PER_COMPANY,
        "tbs": "qdr:d",  # Only results from today
        "hl": "en"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        results = []
        seen_links = set()

        if "organic_results" in data:

            for r in data["organic_results"]:

                link = r.get("link")
                title = r.get("title")
                date = r.get("date", "")

                # Skip missing data
                if not link or not title:
                    continue

                # Remove blacklisted financial blog sites
                if any(bad_domain in link for bad_domain in BLACKLIST_DOMAINS):
                    continue

                # Remove duplicates within same response
                if link in seen_links:
                    continue

                seen_links.add(link)

                results.append({
                    "title": title,
                    "link": link,
                    "date": date
                })

        return results

    except Exception as e:
        print("SerpAPI error:", e)
        return []