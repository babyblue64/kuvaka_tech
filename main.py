from fastapi import FastAPI

app = FastAPI()

# Accept JSON with product/offer details
@app.post('/offer')
def accept_product_offer_info():
    pass

# Accept csv with columns: <name,role,company,industry,location,linkedin_bio>
@app.post('/leads/upload')
def accept_leads_csv():
    pass

# Trigger score-generation process on leads
@app.post('/score')
def trigger_scoring():
    pass

# Return scored lead JSONs in an array
@app.post('/results')
def return_scored_leads():
    pass

# Return results as csv
@app.post('/csvresults')
def return_results_csv():
    pass