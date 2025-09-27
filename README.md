## Live link

Render: https://kuvaka-tech-3jnl.onrender.com/

## Setup Steps

Step 1: Save .env in project directory.
Sample .env:
```bash
OPENAI_API_KEY=90784c4666b608888f85fb1e2ad5b6cc
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

Health check endpoint

_request_
```bash
curl -X GET "localhost:8000/"
```

_response_
```bash
{"message":"Working"}
```

---

Endpoint to add Offer/Product

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

Endpoint to upload leads csv

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

Endpoint to trigger score calculation

_request_
```bash
curl -X POST "localhost:8000/score"
```

_response_
```bash
{"detail":"Successfully scored 20 leads"}
```

---

Endpoint to get list of result JSONs

_request_
```bash
curl -X GET "localhost:8000/results"
```

_response_
```bash
{"total_leads":20,"results":[{"name":"John Smith","role":"CEO","company":"TechFlow Inc","industry":"Software","intent":"High","score":75,"reasoning":"Rules: Decision maker role detected (+20) | Exact ICP match (+20) | Complete profile (+10) | AI: AI analysis unavailable; You exceeded your current quota ;Using default Medium intent and 25 score","data_completeness":"Complete"}, ... ]}
```

---

Endpoint to download results csv

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

## Prompt used

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

ChatGPT is very good when it comes to analysis tasks such as this one. Unlike other models like Claude, which are focused on programming, Openai provides good responses in text-based tasks. 