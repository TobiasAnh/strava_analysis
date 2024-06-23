import requests
import json
import time

import polyline


def decodePolyline(encoded_polyline, precision=5):
    # Decode the polyline
    decoded_coordinates = polyline.decode(encoded_polyline, precision)

    return decoded_coordinates


def createJson(batch: dict, json_filepath="file.json"):
    # Writing the dictionary to a JSON file
    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=4)
    print(f"{json_filepath} has been created")


def importJson(json_filepath):
    try:
        with open(json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Imported data from {json_filepath}")
        return data
    except FileNotFoundError:
        print(f"File {json_filepath} NOT found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {json_filepath}: {e}")
        return None


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


def exchange_code_for_token(client_id, client_secret, code):
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()  # Ensure we notice bad responses
    response_dict = response.json()

    access_token = response_dict["access_token"]
    refresh_token = response_dict["refresh_token"]

    if access_token and refresh_token:
        print("Exchange succesful: access_token and refresh_token")
    else:
        print("Failed to get tokens.")
    return access_token, refresh_token


def make_request(url, access_token=None):
    # Headers for the request
    headers = {
        "Content-Type": "application/json",
    }

    # Add access token to the headers if provided
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    try:
        # Making a GET request
        response = requests.get(url, headers=headers)

        # Raise an error if the request was unsuccessful
        response.raise_for_status()

        # Return the response in JSON format
        return response.json()

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")


def convert_to_timestamp(date_str):
    # Convert date string to timestamp
    return int(time.mktime(time.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")))
