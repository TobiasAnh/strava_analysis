import webbrowser
from datetime import datetime
from funcs import *
from dotenv import load_dotenv
import os

# Authentication
# Load environment variables from a .env file
load_dotenv()

# Access the environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


# Step 1: Get authorization URL and open it in the browser
authorization_url = get_strava_authorization_url(CLIENT_ID)
print(f"Please go to this URL and authorize the application: {authorization_url}")
webbrowser.open(authorization_url)
code = input("Enter the code you received after authorization: ")

access_token, refresh_token = exchange_code_for_token(
    CLIENT_ID,
    CLIENT_SECRET,
    code,
)

# Get athlete information
url = "https://www.strava.com/api/v3/athlete"
athlete = make_request(url, access_token=access_token)
createJson(athlete, "athlete.json")

# Get activities
start = athlete["created_at"]
end = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
start_unix = convert_to_timestamp(start)
end_unix = convert_to_timestamp(end)


page = 1
activities = []
while True:
    try:
        url = f"https://www.strava.com/api/v3/athlete/activities?before={end_unix}&after={start_unix}&page={page}&per_page=30"

        page_respond = make_request(url, access_token=access_token)
        if not page_respond:
            break

        print(f"Found page: {page}")
        activities += page_respond
        page += 1

    except Exception as e:
        print(e)
        break

len(activities)
createJson(activities, f"activities.json")
