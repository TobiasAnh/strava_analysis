import pandas as pd
import time
import argparse
import os
from fetch.func import (
    import_json,
    get_tokens,
    get_athlete_info,
    get_activities,
    get_engine,
    load_schema,
    get_latest_datetime,
)


# NOTE Set initial_setup=True when executing the first time
def main(mode):

    if mode == "init":
        # Get new token
        access_token, refresh_token, expires_at = get_tokens()

        # TODO this does not seems to work! Some permission error.
        # WHOLE SEtup of postgres db might, however, be reevaluated anyway...
        # Generate postgres tables
        # load_schema("athlete.sql")
        # load_schema("activities.sql")
        return

    # Check token status
    tokens = import_json("tokens.json")
    if int(time.time()) > tokens["expires_at"]:
        access_token, refresh_token, expires_at = get_tokens(
            refresh_token=tokens["refresh_token"],
        )
    else:
        access_token = tokens["access_token"]

    # Fetch athlete data
    athlete = get_athlete_info(access_token)

    # ATHLETE
    df = pd.DataFrame.from_dict(athlete, orient="index").T
    df = df.rename(columns={"id": "athlete_id"})
    df = df.set_index("athlete_id")
    engine = get_engine()
    df.to_sql(
        "athlete",
        con=engine,
        if_exists="replace",
        index=True,
    )

    # ACTIVITIES
    start_unix = get_latest_datetime("start_date", "activities")
    activities = get_activities(
        access_token,
        athlete,
        start_unix=start_unix,
    )

    if not activities:
        return

    df = pd.DataFrame(activities)
    df[["map_id", "summary_polyline", "map_resource_state"]] = df["map"].apply(
        pd.Series
    )
    df = df.rename(columns={"type": "activities_type", "id": "activity_id"})
    df = df.drop(["map"], axis=1)

    # NOTE for some reason, the .to_sql only works when saving and reloading the csv.
    # Save and load csv
    df.to_csv("activities.csv", index=False)
    df = pd.read_csv(
        "activities.csv",
        index_col="activity_id",
    )

    # Move date to postgres database
    engine = get_engine()
    try:
        df.to_sql(
            "activities",
            con=engine,
            if_exists="append",
            index=True,
        )
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some modes.")
    parser.add_argument(
        "--mode",
        type=str,
        default="update",
        choices=["update", "init"],
        help='Mode of operation: "update" (default) or "init".',
    )

    args = parser.parse_args()
    main(args.mode)
