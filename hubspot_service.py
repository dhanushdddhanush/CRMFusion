import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
HUBSPOT_REDIRECT_URI = os.getenv("HUBSPOT_REDIRECT_URI")

AUTH_URL = "https://app.hubspot.com/oauth/authorize"
TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"

def generate_auth_url(user_id):
    return (
        f"{AUTH_URL}?"
        f"client_id={HUBSPOT_CLIENT_ID}&"
        f"redirect_uri={HUBSPOT_REDIRECT_URI}&"
        f"scope=crm.objects.contacts.read%20crm.objects.contacts.write&"
        f"response_type=code&"
        f"state={user_id}"
    )

def exchange_code_for_token(code):
    payload = {
        "grant_type": "authorization_code",
        "client_id": HUBSPOT_CLIENT_ID,
        "client_secret": HUBSPOT_CLIENT_SECRET,
        "redirect_uri": HUBSPOT_REDIRECT_URI,
        "code": code
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(TOKEN_URL, headers=headers, data=payload)
    response.raise_for_status()
    data = response.json()
    return {
        "refresh_token": data["refresh_token"],
        "access_token": data["access_token"]
    }

def get_access_token(refresh_token):
    payload = {
        "grant_type": "refresh_token",
        "client_id": HUBSPOT_CLIENT_ID,
        "client_secret": HUBSPOT_CLIENT_SECRET,
        "refresh_token": refresh_token
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(TOKEN_URL, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def get_leads(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_lead(access_token, lead_data):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    payload = {
        "properties": lead_data
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
