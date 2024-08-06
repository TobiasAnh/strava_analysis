import webbrowser
import requests
import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from google.cloud import bigquery
import google.api_core.exceptions

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Strava API ids
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Missing CLIENT_ID or CLIENT_SECRET in environment variables")


# Set up GCP
project_id = os.getenv("project-id")
dataset = os.getenv("dataset")
bigquery_client = bigquery.Client(project=project_id)
dataset_ref = bigquery_client.dataset(dataset)

if not project_id or not dataset:
    logger.info("No GCP project or dataset given. File output stays local")
    stay_local = True


BASE_URL = "https://www.strava.com/api/v3/"


def get_tokens():
    authorization_url = get_strava_authorization_url(CLIENT_ID)
    webbrowser.open(authorization_url)

    code = input("Enter the code you received after authorization: ").strip()
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
    url = f"{BASE_URL}athlete"
    athlete = make_request(url, access_token)
    create_json(athlete, "athlete.json")
    return athlete


def get_activities(access_token, athlete, start=None, end=None):
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


# GCP
# TODO Refactoring required


def convertSchema(file_path):
    # Replace 'path_to_schema.json' with the path to your schema.json file
    with open(file_path, "r") as file:
        columns = json.load(file)

    schema = []
    for column in columns:
        name = column["name"]
        type = column["type"]
        mode = column["mode"]
        description = column["description"]

        schema.append(
            bigquery.SchemaField(
                name=name,
                field_type=type,
                mode=mode,
                description=description,
            )
        )

    return schema


# Construct a BigQuery job configuration object.
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,  # Adjust this if your CSV file has a header row.
    schema=convertSchema("schema.json"),
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    time_partitioning=bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="start_date",  # Name of the column to use for partitioning.
    ),
)


# TODO continue refactoring here
def createTableIfNotExisting(table_ref):

    table_id = f"{project_id}.{table_ref.dataset_id}.{table_ref.table_id}"
    # Check if the table exists, if not, create it with the specified partitioning
    try:
        bigquery_client.get_table(table_id)
        # print(f"Table {table_ref.table_id} found.")
    except google.api_core.exceptions.NotFound:
        # Create a new table
        print(f"{table_ref.table_id} NOT FOUND in {table_ref.dataset_id}")
        table = bigquery.Table(table_id, schema=job_config.schema)
        table.time_partitioning = job_config.time_partitioning
        bigquery_client.create_table(table)
        print(f"{table_ref.table_id} CREATED in {table_ref.dataset_id}")


def getMissingDatesInBQ(date_range, table, date_col):

    table_ref = dataset_ref.table(table)
    createTableIfNotExisting(bigquery_client, table_ref)

    # Dates found in BigQuery
    table_id = f"{table_ref.dataset_id}.{table_ref.table_id}"
    query = f"""
    SELECT DISTINCT `{date_col}`
    FROM `{table_id}`
    """

    # Execute and print job results
    query_job = bigquery_client.query(query)
    dates_in_bq = []
    for row in query_job:
        dates_in_bq.append(row[0])
        row[0]

    missing_dates = list(set(date_range) - set(dates_in_bq))
    missing_dates.sort()
    print(f"BQ table {table_ref.table_id} misses {len(missing_dates)} days of data")

    return missing_dates


def uploadDFintoBQ(df, table, date_col):
    """
    Load a DataFrame into a BigQuery table, partitioned by a daily date, and append the data.

    Args:
    df (pd.DataFrame): The DataFrame to load into BigQuery.
    table_id (str): The BigQuery table ID in the format 'your-project.your_dataset.your_table'.
    date_column (str): The name of the date column to partition by.
    """

    table_ref = dataset_ref.table(table)
    table_id = f"{table_ref.dataset_id}.{table_ref.table_id}"

    # Ensure the date columns are valid for BQ
    df[date_col] = pd.to_datetime(df[date_col])
    df.columns = [col.replace("-", "_") for col in df.columns]

    # Configure the load job to append to the existing table and to partition by date
    job_config = bigquery.LoadJobConfig(
        schema=convertSchema("schema.json"),
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=date_col,  # Name of the partitioning field
        ),
    )

    # Load the DataFrame to BigQuery
    load_job = bigquery_client.load_table_from_dataframe(
        df, table_id, job_config=job_config
    )

    load_job.result()  # Wait for the job to complete.

    print(f"Loaded data with timestamp >> {df[date_col][0]} << in BQ {table_id}")
