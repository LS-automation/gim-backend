import requests
import json
from config import GROQ_API_KEY


def validate_with_ai(company, title, snippet, content):

    prompt = f"""
You are a corporate intelligence analyst.

Return ONLY valid JSON in this exact structure:

{{
"relevant": true/false,
"event_type": "",
"confidence": 0.0-1.0,
"summary": ""
}}

Company: {company}

Allowed Event Types:
Expansion
Funding
Acquisition
Leadership Appointment
Leadership Interview
Tender

Strict Rules:

1. Only mark relevant=true if this article announces a NEW, concrete corporate action.
2. Ignore:
   - Stock price commentary
   - Analyst opinions
   - Market speculation
   - Financial audits
   - General business commentary
   - Shareholder filings
3. The action must be officially announced.
4. If unsure → relevant=false.
5. Summary must be plain text only.
6. Summary must be one short executive sentence.
7. Do NOT include HTML or formatting.
8. Do NOT guess.

Article Information:
Title: {title}
Snippet: {snippet}
Content: {content[:2000]}
"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)

        if response.status_code == 200:
            result = json.loads(response.json()["choices"][0]["message"]["content"])

            # Safety fallback
            if "relevant" not in result:
                return None

            return result

    except Exception as e:
        print("Groq API error:", e)

    return None