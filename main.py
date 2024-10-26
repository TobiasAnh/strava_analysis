import pandas as pd
import psycopg2
from func import (
    get_tokens,
    get_athlete_info,
    get_latest_activity,
    get_activities,
    import_json,
    create_json,
)


def main(update_only=False):
    # Fetch athlete and activities data
    access_token, refresh_token = get_tokens()
    athlete = get_athlete_info(access_token)

    if update_only:
        latest = get_latest_activity()
    else:
        latest = "2014-01-01T00:00:00Z"

    activities = get_activities(
        access_token,
        athlete,
        start=latest,
    )
    df = pd.DataFrame(activities)

    # some unnesting
    df[["map_id", "summary_polyline", "map_resource_state"]] = df["map"].apply(
        pd.Series
    )

    # TODO changing colname here, "type" maybe source of error when loading data into postgres
    # the error suggests some mismatch between col name und number of cols
    df = df.drop("map", axis=1)
    df["type"] = rename("type")
    df.to_csv("activities.csv")


if __name__ == "__main__":
    main()
