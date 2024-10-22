import json
import os
import logging
from google.cloud import bigquery
import google.api_core.exceptions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# GCP


# Construct a BigQuery job configuration object.
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,  # Adjust this if your CSV file has a header row.
    schema=AUTO # <- TODO adjust
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    time_partitioning=bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="start_date",  # Name of the column to use for partitioning.
    ),
)


# Set up GCP # TODO set up gcp project
project_id = os.getenv("project-id")
dataset = os.getenv("dataset")
bigquery_client = bigquery.Client(project=project_id)
dataset_ref = bigquery_client.dataset(dataset)

if not project_id or not dataset:
    logger.info("No GCP project or dataset given. File output stays local")
    stay_local = True


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
