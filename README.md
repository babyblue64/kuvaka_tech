## Live link

Render: https://kuvaka-tech-3jnl.onrender.com/

## Setup Steps

Step 1: Save .env in project directory.
Sample .env:
```bash
GEMINI_API_KEY=90784c4666b608888f85fb1e2ad5b6cc
9c82415e458c59fe20c6f90697c3f98a
43d7b16c05376544c29fccae8f26e584
58d51565d69c85fbd375cf3bcd6eb56e
9545afabd6962ebdea9373d4e29ffe3d
```

---

Step 2: Build from Dockerfile
```bash
docker build -t my-fastapi-app .
```

---

Step 3: Run container
```bash
docker run --name fastapi_container -d -p 8000:8000 --env-file .env my-fastapi-app
```

Server will be running at `http://localhost:8000`

---

## API Curl Requests & Responses

1. ) Health check endpoint

_request_
```bash
curl -X GET "localhost:8000/"
```

_response_
```bash
{"message":"Working"}
```

---

2. ) Endpoint to add Offer/Product

_request_
```bash
curl -X POST "localhost:8000/offer"   -H "Content-Type: application/json"   -d '{
    "name": "AI Outreach Automation",
    "value_props": ["24/7 automated outreach", "6x more meetings booked", "Personalized messaging at scale"],
    "ideal_use_cases": ["B2B SaaS mid-market", "Sales teams 10-50 people", "Companies doing $1M-10M ARR"]
  }'
```

_response_
```bash
{"detail":"New offer set"}
```

---

3. ) Endpoint to upload leads csv

_request_
```bash
curl -X POST "localhost:8000/leads/upload" \
  -F "file=@sample_leads.csv"
```

_response_
```bash
{"total processed":20,"detail":"13 new validated leads uploaded","warnings":"7 row(s) have missing/invalid data"}
```

---

4. ) Endpoint to trigger score calculation

_request_
```bash
curl -X POST "localhost:8000/score"
```

_response_
```bash
{"detail":"Successfully scored 20 leads"}
```

---

5. ) Endpoint to get list of result JSONs

_request_
```bash
curl -X GET "localhost:8000/results"
```

_response_
```bash
{"total_leads":20,"results":[{
    "name": "John Smith",
    "role": "CEO",
    "company": "TechFlow Inc",
    "industry": "Software",
    "intent": "High",
    "score": 100,
    "reasoning": (
        "Rules: Decision maker role detected (+20) | Exact ICP match (+20) | Complete profile (+10) | "
        "AI: AI analysis: INTENT: High | REASONING: As CEO of a B2B SaaS company in a related space "
        "(workflow automation), John likely understands the importance of sales efficiency and growth – "
        "our AI outreach automation directly addresses those needs, especially given his company size likely "
        "benefits from scaling outreach"
    ),
    "data_completeness": "Complete"
}
, ... ]}
```

---

6. ) Endpoint to download results csv

_request_
```bash
curl -X POST "localhost:8000/csvresults"   -o "scored_leads_results.csv"
```

_response_
```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  5108    0  5108    0     0   449k      0 --:--:-- --:--:-- --:--:--  498k
```

---

## Prompt

```Python
Product/Offer: {offer['name']}
            Value Props: {', '.join(offer['value_props'])}
            Ideal Use Cases: {', '.join(offer['ideal_use_cases'])}
            
            Prospect:
            - Name: {lead.get('name', 'Unknown')}
            - Role: {lead.get('role', 'Unknown')}
            - Company: {lead.get('company', 'Unknown')}
            - Industry: {lead.get('industry', 'Unknown')}
            - LinkedIn Bio: {lead.get('linkedin_bio', 'Unknown')}

            Based on the prospect's profile and the product offering, classify their buying intent as High, Medium, or Low.
            Explain your reasoning in 1-2 sentences focusing on role fit, industry alignment, and potential need.
            
            Format: INTENT: [High/Medium/Low] | REASONING: [explanation]
```

## Model

_gemma-3-27b-it_

From Google.

Trying openai and hugginface, I had to struggle over depracated methods and quota limits. Google's Gemini's mini version Gemma is light-weight but responsive. It helped me integrate AI scoring in this project

## Navigation Video

Loom: https://www.loom.com/share/131c8acdd32d4877a3945e1db123864d?sid=d0106c6f-11e4-4467-b82d-1bd1fa8c2647