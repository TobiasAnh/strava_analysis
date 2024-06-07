import requests
import time


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


url = "https://www.strava.com/api/v3/athlete"


client_secret = "246cfc6ae2519331905a0c0834fc05aaa42ad0b4"
access_token = "9409868a418c3538743cfbfa89f5ac25405da48e"
refresh_token = "e4b4a4ce52d22187112c03a0aaf370329efe18f8"


make_request(url, access_token=access_token)
