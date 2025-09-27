from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic_models import Offer, Lead
import pandas as pd
from pydantic import ValidationError

app = FastAPI()

current_offer: Offer | None = None
leads_data = []

# Accept JSON with product/offer details
@app.post('/offer')
def accept_offer_info(offer: Offer):
    global current_offer
    try:
        current_offer = offer
        return {"detail": "New offer set"}
    except:
        raise HTTPException(status_code=400, detail="Invalid data/format")


# Accept csv with columns: <name,role,company,industry,location,linkedin_bio>
@app.post('/leads/upload')
def upload_leads_csv(file: UploadFile = File(...)):
    global leads_data

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only csv files accepted")

    try:
        # read csv
        df = pd.read_csv(file.file)

        required_columns = ["name", "role", "company", "industry", "location", "linkedin_bio"]

        # check if any required columns are missing from the df
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            raise HTTPException(status_code=400, detail=f"Missing column(s): {missing_cols}")
        
        # replace missing values with ""
        df = df.fillna("")

        validated_leads = []
        validation_errors = [] # to store error details of rows that failed validation against 'Lead'

        for index, row in df.iterrows():
            try:
                lead_dict = {col: row[col] for col in required_columns} # build dict out of row Pandas Series
                lead = Lead(**lead_dict) #pydantic
                validated_leads.append(lead.model_dump())
            except ValidationError as e:
                validation_errors.append({"row": index + 1, "error": str(e), "data": row.to_dict()})

        leads_data = validated_leads #global variable

        if validation_errors:
            warnings = f"Ignored {len(validation_errors)} rows having missing/invalid data"
        
        return {"detail": f"{len(leads_data)} new leads uploaded", "warnings": warnings}
    except:
        raise HTTPException(status_code=400, detail="Error reading/parsing csv OR file empty")

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