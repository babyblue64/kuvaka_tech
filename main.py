from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic_models import Offer, Lead
import pandas as pd
from pydantic import ValidationError
from scoring import calculate_total_score
import io
from fastapi.responses import StreamingResponse

app = FastAPI()

# in-memory data
current_offer: Offer | None = None
validated_leads = []
validation_failed_leads = []
scored_results = []

# Health check
@app.get("/")
def root():
    return {"message": "Working"}

# Accept JSON with product/offer details
@app.post('/offer')
def accept_offer_info(offer: Offer):
    global current_offer
    try:
        current_offer = offer
        return {"detail": "New offer set"}
    except:
        raise HTTPException(status_code=400, detail="Invalid data/format")


# Accept csv with columns: name, role, company, industry, location, linkedin_bio
@app.post('/leads/upload')
async def upload_leads_csv(file: UploadFile = File(...)):
    global validated_leads
    global validation_failed_leads # to store rows that failed validation against 'Lead' pydantic model

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only csv files accepted")

    try:
        #reset
        validated_leads = []
        validation_failed_leads = []

        # read csv
        df = pd.read_csv(file.file)

        required_columns = ["name", "role", "company", "industry", "location", "linkedin_bio"]

        # check if any required columns are missing from the df
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            raise HTTPException(status_code=400, detail=f"Missing column(s): {missing_cols}")
        
        # replace missing values with None
        df = df.replace({pd.NA: None, '': None})
        df = df.where(pd.notnull(df), None)

        for index, row in df.iterrows():
            try:
                lead_dict = {col: row[col] for col in required_columns} # build dict out of 'row' Pandas Series
                lead = Lead(**lead_dict) # create pydantic obj
                validated_leads.append(lead.model_dump()) # back to dict
            except ValidationError as e:
                missing_values_count = len(e.errors()) # find missing value count from pydantic validation error
                validation_failed_leads.append({ "row_data": row.to_dict(), "missing_values_count": missing_values_count })

        warnings = "Nil"
        if validation_failed_leads:
            warnings = f"{len(validation_failed_leads)} row(s) have missing/invalid data"
        
        return { "total processed": len(validated_leads) + len(validation_failed_leads), "detail": f"{len(validated_leads)} new validated leads uploaded", "warnings": warnings }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error reading/parsing csv: {str(e)}")

# Trigger score-generation process on leads
@app.post('/score')
def trigger_scoring():
    global scored_results

    if current_offer is None:
        raise HTTPException(status_code=400, detail="No offer provided to /offer POST endpoint")
    
    if not validated_leads and not validation_failed_leads:
        raise HTTPException(status_code=400, detail="No leads uploaded. Please POST CSV to /leads/upload")
    
    try:
        scored_results = [] # to reset
        offer_dict = current_offer.model_dump() # convert pydantic obj to dict

        # score validated leads
        for lead_entry in validated_leads:
            scored_lead = calculate_total_score(lead_entry, offer_dict, is_validated=True)
            scored_results.append(scored_lead)

        # score validation-failed leads
        for failed_lead_entry in validation_failed_leads:
            lead_data = failed_lead_entry["row_data"]
            missing_count = failed_lead_entry["missing_values_count"]

            # clean up data
            cleaned_lead = {}
            for key, value in lead_data.items():
                if value == 'nan' or pd.isna(value):
                    cleaned_lead[key] = None
                else:
                    cleaned_lead[key] = value

            scored_lead = calculate_total_score(cleaned_lead, offer_dict, is_validated=False, missing_value_count=missing_count)
            scored_results.append(scored_lead)

        # sort scored results by score
        scored_results.sort(key=lambda x: x['score'], reverse=True)

        return { "detail": f"Successfully scored {len(scored_results)} leads" }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Return scored lead JSONs in an array
@app.get('/results')
def return_scored_leads():
    if not scored_results:
        raise HTTPException(status_code=404, detail="No results available. Run POST /score to generate results")
    
    return {
        "total_leads": len(scored_results),
        "results": scored_results
    }

# Return results as csv
@app.post('/csvresults')
def return_results_csv():
    if not scored_results:
        raise HTTPException(status_code=404, detail="No results available. Run POST /score to generate results")
    
    try:
        df = pd.DataFrame(scored_results) # convert list of dict to dataframe

        csv_buffer = io.StringIO() # create file like object
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()

        return StreamingResponse( # return as downloadable csv file
            io.BytesIO(csv_content.encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=scored_leads.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating CSV: {str(e)}")