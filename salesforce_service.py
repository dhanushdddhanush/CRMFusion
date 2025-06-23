import os
import requests
from dotenv import load_dotenv
load_dotenv()

SF_CLIENT_ID = os.getenv("SF_CLIENT_ID")
SF_CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")
SF_REDIRECT_URI = os.getenv("SF_REDIRECT_URI")

AUTH_URL = "https://login.salesforce.com/services/oauth2/authorize"
TOKEN_URL = "https://login.salesforce.com/services/oauth2/token"

def generate_auth_url(user_id):
    return (
        f"{AUTH_URL}?"
        f"response_type=code&client_id={SF_CLIENT_ID}"
        f"&redirect_uri={SF_REDIRECT_URI}&state={user_id}"
    )

def exchange_code_for_token(code):
    payload = {
        "grant_type": "authorization_code",
        "client_id": SF_CLIENT_ID,
        "client_secret": SF_CLIENT_SECRET,
        "redirect_uri": SF_REDIRECT_URI,
        "code": code
    }
    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    data = response.json()
    return {
        "refresh_token": data["refresh_token"],
        "instance_url": data["instance_url"]
    }

def get_access_token(refresh_token):
    payload = {
        "grant_type": "refresh_token",
        "client_id": SF_CLIENT_ID,
        "client_secret": SF_CLIENT_SECRET,
        "refresh_token": refresh_token
    }
    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()
    return response.json()["access_token"], response.json()["instance_url"]

def get_leads(access_token, instance_url):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{instance_url}/services/data/v52.0/query?q=SELECT+Id,FirstName,LastName,Company+FROM+Lead"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_lead(access_token, instance_url, lead_data):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = f"{instance_url}/services/data/v52.0/sobjects/Lead"
    response = requests.post(url, headers=headers, json=lead_data)
    response.raise_for_status()
    return response.json()
