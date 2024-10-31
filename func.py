import webbrowser
import requests
import json
import os
import logging
import pandas as pd
import time
import pytz
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load strava API credentials
BASE_URL = "https://www.strava.com/api/v3/"
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
if not CLIENT_ID or not CLIENT_SECRET:
    logger.error("Missing CLIENT_ID or CLIENT_SECRET in environment variables")
    raise ValueError("Missing CLIENT_ID or CLIENT_SECRET in environment variables")


def get_tokens(refresh_token=None):

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    if not refresh_token:
        authorization_url = get_strava_authorization_url(CLIENT_ID)
        webbrowser.open(authorization_url)
        code = input(
            "Look at your browser. Enter the code you received after authorization: "
        )
        # code = "38798a777462c0aee6460c084d5875a108823d79"
        code = code.strip()
        payload.update(
            {
                "code": code,
                "grant_type": "authorization_code",
            }
        )

    else:
        payload.update(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        )

    response = requests.post("https://www.strava.com/api/v3/oauth/token", data=payload)
    response_dict = response.json()
    logger.info("Access and refresh token found.")
    logger.info(
        f"access_token expires in {int(response_dict['expires_in'] / 60)} minutes."
    )

    tokens = {
        "access_token": response_dict["access_token"],
        "refresh_token": response_dict["refresh_token"],
        "expires_at": response_dict["expires_at"],
    }
    create_json(tokens, "tokens.json")

    return (
        response_dict["access_token"],
        response_dict["refresh_token"],
        response_dict["expires_at"],
    )


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
        "approval_prompt": "force",  # force / auto
        "scope": scope_str,
    }
    request_url = requests.Request("GET", base_url, params=params).prepare().url
    return request_url


def get_athlete_info(access_token):
    logger.info("Extracting athlete information ... ")
    url = f"{BASE_URL}athlete"
    athlete = make_request(url, access_token)
    return athlete


def get_activities(access_token, athlete, start_unix=None):

    end_unix = int(time.time())

    activities = []
    page = 1
    while True:
        url = f"{BASE_URL}athlete/activities?before={end_unix}&after={start_unix}&page={page}&per_page=30"
        page_respond = make_request(url, access_token)
        if not page_respond:
            break

        activities.extend(page_respond)
        logger.info(f"Found {page} pages of activities.")
        page += 1

    if not activities:
        logger.info("No recent activities found. Database seems up to date!")
    else:
        logger.info(f"Found {len(activities)} new activities")

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


def convert_str_to_unix(date_str, assign_to_utc=True):
    if not date_str:
        logger.info("No time found")
    if assign_to_utc:
        naive_datetime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        utc_datetime = pytz.utc.localize(naive_datetime)

    unix_utc_timestamp = int(utc_datetime.timestamp())

    return unix_utc_timestamp


# POSTGRES functions


# Retrieve database credentials from environment variables
def get_engine():
    load_dotenv()
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    # Create the engine using the credentials from the .env file
    engine = create_engine(
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    return engine


# Get the latest start_date from the activities table
def get_latest_datetime(datetime_col, table):
    """Query the database to find the latest start_date."""

    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(
                text(f"SELECT MAX({datetime_col}) FROM {table};")
            )
            latest_datetime = result.scalar()  # Get the single scalar value
            logger.info(f"Latest {datetime_col} in table {table}: {latest_datetime}")
            return convert_str_to_unix(latest_datetime)

    except ProgrammingError:
        logger.info(f"{table} not found. Setting latest_datetime manually.")
        return 1388530800  # timestamp refers to 2014


def load_schema(filename):
    """Load the SQL schema from a file and execute it."""
    with open(filename, "r") as file:
        schema_sql = file.read()

    # Split commands by semicolon if there are multiple statements
    commands = schema_sql.strip().split(";")

    engine = get_engine()
    with engine.connect() as connection:
        for command in commands:
            command = command.strip()  # Remove any surrounding whitespace
            if command:  # Ensure command is not empty
                connection.execute(text(command))  # Use text() for safety
