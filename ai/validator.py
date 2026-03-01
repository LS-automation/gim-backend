import requests
import json
from config import GROQ_API_KEY


def validate_with_ai(company, content):

    prompt = f"""
Return ONLY valid JSON.

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

STRICT RULES:

1. Only mark relevant=true if this article announces a NEW, concrete company action.
2. Ignore stock price commentary.
3. Ignore analyst opinions.
4. Ignore shareholder filings.
5. Ignore financial audit commentary.
6. Ignore market speculation.
7. Ignore general strategy discussion.
8. If unsure → relevant=false.
9. Do NOT guess.

Article:
"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "user",
                "content": prompt + content[:2000]
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
            return json.loads(response.json()["choices"][0]["message"]["content"])

    except Exception as e:
        print("Groq API error:", e)

    return None