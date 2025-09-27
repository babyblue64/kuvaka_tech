## API Curl Requests & Responses

_request_
```bash
curl -X GET "localhost:8000/"
```

_response_
```bash
{"message":"Working"}
```

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

_request_
```bash
curl -X POST "localhost:8000/leads/upload" \
  -F "file=@sample_leads.csv"
```

_response_
```bash
{"total processed":20,"detail":"13 new validated leads uploaded","warnings":"7 row(s) have missing/invalid data"}
```

_request_
```bash
curl -X POST "localhost:8000/score"
```

_response_
```bash
{"detail":"Successfully scored 20 leads"}
```

_request_
```bash
curl -X GET "localhost:8000/results"
```

_response_
```bash
{"total_leads":20,"results":[{"name":"John Smith","role":"CEO","company":"TechFlow Inc","industry":"Software","intent":"High","score":75,"reasoning":"Rules: Decision maker role detected (+20) | Exact ICP match (+20) | Complete profile (+10) | AI: AI analysis unavailable; You exceeded your current quota ;Using default Medium intent and 25 score","data_completeness":"Complete"}, ... ]}
```

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