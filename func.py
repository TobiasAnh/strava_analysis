import webbrowser
import requests
import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Strava API ids
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    logger.error("Missing CLIENT_ID or CLIENT_SECRET in environment variables")
    raise ValueError("Missing CLIENT_ID or CLIENT_SECRET in environment variables")


BASE_URL = "https://www.strava.com/api/v3/"


def get_tokens():
    authorization_url = get_strava_authorization_url(CLIENT_ID)
    webbrowser.open(authorization_url)

    code = input(
        "Look at your browser. Enter the code you received after authorization: "
    ).strip()
    access_token, refresh_token = exchange_code_for_token(
        CLIENT_ID,
        CLIENT_SECRET,
        code,
    )

    logger.info("Access and refresh token found.")
    return access_token, refresh_token


def exchange_code_for_token(client_id, client_secret, code):
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    response_dict = response.json()
    return response_dict["access_token"], response_dict["refresh_token"]


def get_strava_authorization_url(
    client_id,
    redirect_uri="http://localhost/exchange_token",
    scopes=["activity:read"],
):
    base_url = "https://www.strava.com/oauth/authorize"
    scope_str = ",".join(scopes)
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "approval_prompt": "force",
        "scope": scope_str,
    }
    request_url = requests.Request("GET", base_url, params=params).prepare().url
    return request_url


def get_athlete_info(access_token):
    print()
    print("Extracting athlete information ... ")
    url = f"{BASE_URL}athlete"
    athlete = make_request(url, access_token)
    create_json(athlete, "athlete.json")
    return athlete


def get_activities(access_token, athlete, start=None, end=None):
    print()
    print("Extracting athlete information ... ")
    if not start:
        start = athlete["created_at"]
    end = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    start_unix = convert_to_timestamp(start)
    end_unix = convert_to_timestamp(end)

    activities = []
    page = 1
    while True:
        url = f"{BASE_URL}athlete/activities?before={end_unix}&after={start_unix}&page={page}&per_page=30"
        page_respond = make_request(url, access_token)
        if not page_respond:
            break

        activities.extend(page_respond)
        page += 1

        if (page % 5) == 0:
            logger.info(f"Found {page} pages of activities.")

    return activities


def create_json(data, filepath="file.json"):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"{filepath} has been created")


def import_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Imported data from {filepath}")
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error reading {filepath}: {e}")
        return None


def make_request(url, access_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error(f"HTTP error {response.status}: {response.reason}")
        return None
    return response.json()


def convert_to_timestamp(date_str):
    return int(
        datetime.strptime(
            date_str,
            "%Y-%m-%dT%H:%M:%SZ",
        ).timestamp()
    )
