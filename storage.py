from sqlalchemy import create_engine, text
import pandas as pd

from func import convert_str_to_unix

# Create the engine
engine = create_engine("postgresql://rasp:rasp@localhost:5432/strava")


# Get the latest start_date from the activities table
def get_latest_start_date():
    """Query the database to find the latest start_date."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT MAX(start_date) FROM activities;"))
        latest_start_date = result.scalar()  # Get the single scalar value
        print("Last activity stored in database >> strava << from ... ")
        print(latest_start_date)
    return convert_str_to_unix(latest_start_date)


# Load the CSV file
df = pd.read_csv(
    "activities.csv",
    index_col="activity_id",
)


def load_schema(filename):
    """Load the SQL schema from a file and execute it."""
    with open(filename, "r") as file:
        schema_sql = file.read()

    # Split commands by semicolon if there are multiple statements
    commands = schema_sql.strip().split(";")

    with engine.connect() as connection:
        for command in commands:
            command = command.strip()  # Remove any surrounding whitespace
            if command:  # Ensure command is not empty
                connection.execute(text(command))  # Use text() for safety


# Load the schema
load_schema("schema.sql")

# Insert the data
try:
    df.to_sql("activities", con=engine, if_exists="fail", index=True)
except ValueError as e:
    print(e)
