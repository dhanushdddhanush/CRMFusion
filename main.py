from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from zoho_service import (
    generate_auth_url, exchange_code_for_token,
    get_access_token, get_leads, create_lead
)
from storage_service import store_refresh_token, get_refresh_token, delete_refresh_token
from fastapi.responses import HTMLResponse
from salesforce_service import (
    generate_auth_url as sf_auth_url,
    exchange_code_for_token as sf_exchange,
    get_access_token as sf_get_token,
    get_leads as sf_get_leads,
    create_lead as sf_create_lead
)
from hubspot_service import (
    generate_auth_url as hubspot_auth_url,
    exchange_code_for_token as hubspot_exchange,
    get_access_token as hubspot_get_token,
    get_leads as hubspot_get_leads,
    create_lead as hubspot_create_lead
)



app = FastAPI()

@app.get("/")
def root():
    return {"status": "Zoho Multi-Account API Running"}

@app.get("/zoho/generate-auth-url")
def auth_url(user_id: str):
    url = generate_auth_url(user_id)
    return {"auth_url": url}

@app.get("/zoho/callback")
def oauth_callback(code: str, state: str):
    refresh_token = exchange_code_for_token(code)
    store_refresh_token(state, refresh_token)

    html_content = """
    <html>
        <head>
            <title>Authentication Complete</title>
        </head>
        <body>
            <h3>✅ Authentication successful!</h3>
            <p>You may now return to the app.</p>
            <p><strong>You can close this tab.</strong></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)  
@app.get("/zoho/auth-status")
def check_auth_status(user_id: str):
    
    refresh_token = get_refresh_token(user_id)
    if refresh_token:
        return {"auth_done": True}
    return {"auth_done": False}
@app.get("/zoho/get_leads")
def get_user_leads(user_id: str):
    refresh_token = get_refresh_token(user_id)
    if not refresh_token:
        raise HTTPException(status_code=400, detail="User not authorized.")
    access_token = get_access_token(refresh_token)
    leads = get_leads(access_token)
    return JSONResponse(content=leads)
@app.delete("/zoho/delete_token")
def delete_token(user_id: str):
    try:
        delete_refresh_token(user_id)
        return JSONResponse(content={"status": f"Refresh token for user {user_id} deleted."}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting token: {e}")
@app.post("/zoho/create_lead")
async def create_user_lead(user_id: str, request: Request):
    lead_data = await request.json()
    refresh_token = get_refresh_token(user_id)
    if not refresh_token:
        raise HTTPException(status_code=400, detail="User not authorized.")
    access_token = get_access_token(refresh_token)
    created = create_lead(access_token, lead_data)
    return JSONResponse(content=created)


# Generate Auth URL
@app.get("/salesforce/generate-auth-url")
def sf_generate_auth(user_id: str):
    return {"auth_url": sf_auth_url(user_id)}

# OAuth Callback
@app.get("/salesforce/callback")
def sf_callback(code: str, state: str):
    tokens = sf_exchange(code)
    store_refresh_token(state, tokens["refresh_token"], partition_key="salesforce", extra_data={"instance_url": tokens["instance_url"]})
    return HTMLResponse(content="<h3>✅ Salesforce Authentication Successful</h3>")

# Auth Status
@app.get("/salesforce/auth-status")
def sf_auth_status(user_id: str):
    data = get_refresh_token(user_id, partition_key="salesforce")
    return {"auth_done": bool(data)}

# Get Leads
@app.get("/salesforce/get_leads")
def sf_get_leads_api(user_id: str):
    data = get_refresh_token(user_id, partition_key="salesforce")
    if not data:
        raise HTTPException(status_code=400, detail="User not authorized.")
    token, instance = sf_get_token(data["refresh_token"])
    leads = sf_get_leads(token, instance)
    return JSONResponse(content=leads)
@app.delete("/salesforce/delete_token")
def sf_delete_token(user_id: str):
    try:
        delete_refresh_token(user_id, partition_key="salesforce")
        return JSONResponse(content={"status": f"Refresh token for user {user_id} deleted from Salesforce."}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting token: {e}")

# Create Lead
@app.post("/salesforce/create_lead")
async def sf_create_lead_api(user_id: str, request: Request):
    data = get_refresh_token(user_id, partition_key="salesforce")
    if not data:
        raise HTTPException(status_code=400, detail="User not authorized.")
    access_token, instance_url = sf_get_token(data["refresh_token"])
    lead_data = await request.json()
    created = sf_create_lead(access_token, instance_url, lead_data)
    return JSONResponse(content=created)
@app.get("/hubspot/generate-auth-url")
def hubspot_generate_auth(user_id: str):
    return {"auth_url": hubspot_auth_url(user_id)}

@app.get("/hubspot/callback")
def hubspot_callback(code: str, state: str):
    tokens = hubspot_exchange(code)
    store_refresh_token(state, tokens["refresh_token"], partition_key="hubspot")
    return HTMLResponse(content="<h3>✅ HubSpot Authentication Successful</h3>")

@app.get("/hubspot/auth-status")
def hubspot_auth_status(user_id: str):
    data = get_refresh_token(user_id, partition_key="hubspot")
    return {"auth_done": bool(data)}

@app.get("/hubspot/get_leads")
def hubspot_get_leads_api(user_id: str):
    data = get_refresh_token(user_id, partition_key="hubspot")
    if not data:
        raise HTTPException(status_code=400, detail="User not authorized.")
    token = hubspot_get_token(data["refresh_token"])
    leads = hubspot_get_leads(token)
    return JSONResponse(content=leads)

@app.post("/hubspot/create_lead")
async def hubspot_create_lead_api(user_id: str, request: Request):
    data = get_refresh_token(user_id, partition_key="hubspot")
    if not data:
        raise HTTPException(status_code=400, detail="User not authorized.")
    access_token = hubspot_get_token(data["refresh_token"])
    lead_data = await request.json()
    created = hubspot_create_lead(access_token, lead_data)
    return JSONResponse(content=created)

@app.delete("/hubspot/delete_token")
def hubspot_delete_token(user_id: str):
    try:
        delete_refresh_token(user_id, partition_key="hubspot")
        return JSONResponse(content={"status": f"HubSpot token for {user_id} deleted."}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting token: {e}")    
