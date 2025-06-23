import os
import requests
from dotenv import load_dotenv
load_dotenv()
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

def generate_auth_url(user_id):
    return (
        f"https://accounts.zoho.in/oauth/v2/auth?"
        f"scope=ZohoCRM.modules.ALL&"
        f"client_id={ZOHO_CLIENT_ID}&"
        f"response_type=code&"
        f"access_type=offline&"
        f"redirect_uri={REDIRECT_URI}&"
        f"state={user_id}"
    )

def exchange_code_for_token(code):
    payload = {
        "grant_type": "authorization_code",
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    response = requests.post("https://accounts.zoho.in/oauth/v2/token", data=payload)
    response.raise_for_status()
    return response.json()["refresh_token"]

def get_access_token(refresh_token):
    payload = {
        "grant_type": "refresh_token",
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "refresh_token": refresh_token
    }
    response = requests.post("https://accounts.zoho.in/oauth/v2/token", data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def get_leads(access_token):
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    response = requests.get("https://www.zohoapis.in/crm/v2/Leads", headers=headers)
    response.raise_for_status()
    return response.json()

def create_lead(access_token, lead_data):
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        "https://www.zohoapis.in/crm/v2/Leads",
        headers=headers,
        json={"data": [lead_data]}
    )
    response.raise_for_status()
    return response.json()
