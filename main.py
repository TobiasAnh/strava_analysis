import pandas as pd
import time
from func import (
    import_json,
    get_tokens,
    get_athlete_info,
    get_activities,
    get_engine,
    load_schema,
    get_latest_datetime,
)

# TODO setup ready (data fetch + storing in postgres on same machine)
# Next step -> fetching on machine 1 and storing on raspberry
# requires to set up on raspberry (postgres + database + ssh connection from linux vm ?)


def main():

    tokens = import_json("tokens.json")
    if int(time.time()) > tokens["expires_at"]:
        access_token, refresh_token, expires_at = get_tokens(
            refresh_token=tokens["refresh_token"],
        )
    else:
        access_token = tokens["access_token"]

    # Fetch athlete data
    athlete = get_athlete_info(access_token)
    # TODO athlete data can also be stored as table
    # _ = pd.DataFrame.from_dict(athlete, orient="index").T

    # Fetch activities
    initial_setup = False
    if initial_setup:
        load_schema("activities.sql")
        start_unix = 1388530800  # refers to 2014 (activities date prior athlete account was set up)
    else:
        start_unix = get_latest_datetime("start_date", "activities")

    activities = get_activities(
        access_token,
        athlete,
        start_unix=start_unix,
    )

    if not activities:
        return

    # Transform (unnesting relevant info)
    df = pd.DataFrame(activities)
    df[["map_id", "summary_polyline", "map_resource_state"]] = df["map"].apply(
        pd.Series
    )
    df = df.rename(columns={"type": "activities_type", "id": "activity_id"})
    df = df.drop(["map"], axis=1)

    # Save and load csv
    df.to_csv("activities.csv", index=False)
    df = pd.read_csv(
        "activities.csv",
        index_col="activity_id",
    )

    # Move date to postgres database
    engine = get_engine()
    try:
        df.to_sql("activities", con=engine, if_exists="append", index=True)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
