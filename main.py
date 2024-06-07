from __future__ import print_statement
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: strava_oauth
swagger_client.configuration.access_token = "YOUR_ACCESS_TOKEN"

# create an instance of the API class
api_instance = swagger_client.AthletesApi()

try:
    # Get Authenticated Athlete
    api_response = api_instance.getLoggedInAthlete()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AthletesApi->getLoggedInAthlete: %s\n" % e)


client_secret = "246cfc6ae2519331905a0c0834fc05aaa42ad0b4"
access_token = "9409868a418c3538743cfbfa89f5ac25405da48e"
refresh_token = "e4b4a4ce52d22187112c03a0aaf370329efe18f8"
