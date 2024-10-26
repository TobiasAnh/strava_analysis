import pandas as pd

from func import (
    get_tokens,
    get_athlete_info,
    get_activities,
)

from storage import get_latest_start_date


def main(update_only=True):
    # Fetch athlete and activities data
    access_token, refresh_token = get_tokens()
    athlete = get_athlete_info(access_token)

    # TODO athlete info can also be store as csv and in a separate table
    # df = pd.DataFrame(athlete, index="id")

    if update_only:
        latest = get_latest_start_date()
    else:
        latest = 1388530800  # refers to 2014 (activities date prior athlete account was set up)

    activities = get_activities(
        access_token,
        athlete,
        start_unix=latest,
    )

    if activities:
        # df restructuring
        df = pd.DataFrame(activities)
        df[["map_id", "summary_polyline", "map_resource_state"]] = df["map"].apply(
            pd.Series
        )
        df = df.rename(
            columns={
                "type": "activities_type",
                "id": "activity_id",
            }
        )
        df = df.drop(["map"], axis=1)
        df.to_csv("activities.csv", index=False)


if __name__ == "__main__":
    main()
