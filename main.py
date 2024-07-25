import pandas as pd

from func2 import (
    get_tokens,
    get_athlete_info,
    get_activities,
    import_json,
    create_json,
)


def main():
    # Fetch athlete and activities data
    access_token, refresh_token = get_tokens()
    athlete = get_athlete_info(access_token)
    activities = get_activities(
        access_token,
        athlete,
        start="2014-01-01T00:00:00Z",
    )

    # Save results
    create_json(activities, "activities.json")
    activities = import_json("activities.json")
    df = pd.DataFrame(activities)
    df.to_csv("file.csv")


if __name__ == "__main__":
    main()
