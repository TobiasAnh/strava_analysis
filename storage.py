import psycopg2
import pandas as pd

# Database connection parameters
db_params = {
    "dbname": "strava",
    "user": "rasp",
    "password": "rasp",
    "host": "localhost",
    "port": "5432",
}

# Load CSV into a DataFrame
df = pd.read_csv(
    "activities.csv", index_col=0
)  # Make sure data.csv is created from JSON

# Connect to the PostgreSQL database
conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

# Create table structure if not exists
# Load and execute the schema file
with open("schema.sql", "r") as schema_file:
    schema_sql = schema_file.read()
    cursor.execute(schema_sql)
    conn.commit()

# Insert CSV data into the PostgreSQL table
for _, row in df.iterrows():
    row = row.replace({pd.NA: None, pd.NaT: None})
    cursor.execute(
        """
        INSERT INTO activities (
            resource_state, athlete, name, distance, moving_time, elapsed_time, total_elevation_gain,
            activities_type, sport_type, workout_type, id, start_date, start_date_local, timezone, utc_offset,
            location_city, location_state, location_country, achievement_count, kudos_count,
            comment_count, athlete_count, photo_count, trainer, commute, manual, private, visibility,
            flagged, gear_id, start_latlng, end_latlng, average_speed, max_speed, average_cadence,
            average_temp, average_watts, max_watts, weighted_average_watts, device_watts, kilojoules,
            has_heartrate, heartrate_opt_out, display_hide_heartrate_option, elev_high, elev_low,
            upload_id, upload_id_str, external_id, from_accepted_tag, pr_count, total_photo_count,
            has_kudoed, suffer_score, average_heartrate, max_heartrate, map_id, summary_polyline,
            map_resource_state
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """,
        (
            row["resource_state"],
            row["athlete"],
            row["name"],
            row["distance"],
            row["moving_time"],
            row["elapsed_time"],
            row["total_elevation_gain"],
            row["activities_type"],
            row["sport_type"],
            row["workout_type"],
            row["id"],
            row["start_date"],
            row["start_date_local"],
            row["timezone"],
            row["utc_offset"],
            row["location_city"],
            row["location_state"],
            row["location_country"],
            row["achievement_count"],
            row["kudos_count"],
            row["comment_count"],
            row["athlete_count"],
            row["photo_count"],
            row["trainer"],
            row["commute"],
            row["manual"],
            row["private"],
            row["visibility"],
            row["flagged"],
            row["gear_id"],
            row["start_latlng"],
            row["end_latlng"],
            row["average_speed"],
            row["max_speed"],
            row["average_cadence"],
            row["average_temp"],
            row["average_watts"],
            row["max_watts"],
            row["weighted_average_watts"],
            row["device_watts"],
            row["kilojoules"],
            row["has_heartrate"],
            row["heartrate_opt_out"],
            row["display_hide_heartrate_option"],
            row["elev_high"],
            row["elev_low"],
            row["upload_id"],
            row["upload_id_str"],
            row["external_id"],
            row["from_accepted_tag"],
            row["pr_count"],
            row["total_photo_count"],
            row["has_kudoed"],
            row["suffer_score"],
            row["average_heartrate"],
            row["max_heartrate"],
            row["map_id"],
            row["summary_polyline"],
            row["map_resource_state"],
        ),
    )

# Commit the transaction and close the connection
conn.commit()
cursor.close()
conn.close()



rows_n = (
            row["resource_state"],
            row["athlete"],
            row["name"],
            row["distance"],
            row["moving_time"],
            row["elapsed_time"],
            row["total_elevation_gain"],
            row["activities_type"],
            row["sport_type"],
            row["workout_type"],
            row["id"],
            row["start_date"],
            row["start_date_local"],
            row["timezone"],
            row["utc_offset"],
            row["location_city"],
            row["location_state"],
            row["location_country"],
            row["achievement_count"],
            row["kudos_count"],
            row["comment_count"],
            row["athlete_count"],
            row["photo_count"],
            row["trainer"],
            row["commute"],
            row["manual"],
            row["private"],
            row["visibility"],
            row["flagged"],
            row["gear_id"],
            row["start_latlng"],
            row["end_latlng"],
            row["average_speed"],
            row["max_speed"],
            row["average_cadence"],
            row["average_temp"],
            row["average_watts"],
            row["max_watts"],
            row["weighted_average_watts"],
            row["device_watts"],
            row["kilojoules"],
            row["has_heartrate"],
            row["heartrate_opt_out"],
            row["display_hide_heartrate_option"],
            row["elev_high"],
            row["elev_low"],
            row["upload_id"],
            row["upload_id_str"],
            row["external_id"],
            row["from_accepted_tag"],
            row["pr_count"],
            row["total_photo_count"],
            row["has_kudoed"],
            row["suffer_score"],
            row["average_heartrate"],
            row["max_heartrate"],
            row["map_id"],
            row["summary_polyline"],
            row["map_resource_state"],
        )

(
            resource_state, athlete, name, distance, moving_time, elapsed_time, total_elevation_gain,
            activities_type, sport_type, workout_type, id, start_date, start_date_local, timezone, utc_offset,
            location_city, location_state, location_country, achievement_count, kudos_count,
            comment_count, athlete_count, photo_count, trainer, commute, manual, private, visibility,
            flagged, gear_id, start_latlng, end_latlng, average_speed, max_speed, average_cadence,
            average_temp, average_watts, max_watts, weighted_average_watts, device_watts, kilojoules,
            has_heartrate, heartrate_opt_out, display_hide_heartrate_option, elev_high, elev_low,
            upload_id, upload_id_str, external_id, from_accepted_tag, pr_count, total_photo_count,
            has_kudoed, suffer_score, average_heartrate, max_heartrate, map_id, summary_polyline,
            map_resource_state
        ) 

placeholder = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )

len(rows_n)

type