import folium
from funcs import importJson, decodePolyline

activities = importJson("activities.json")


# Create a map centered at the average location
average_lat = 49.37
average_lon = 8.78

mymap = folium.Map(location=[average_lat, average_lon], zoom_start=12)
for activity in activities:
    print(activity["sport_type"])

    if not activity["map"]["summary_polyline"]:
        print(f"No polyline found for {activity['name']}, {activity['start_date']}")
        continue

    # if not activity["sport_type"] == "MountainBikeRide":
    #    continue

    if activity["sport_type"] == "Ride":
        color = "blue"
    elif activity["sport_type"] == "MountainBikeRide":
        color = "red"
    elif activity["sport_type"] == "Hike":
        color = "brown"
    elif activity["sport_type"] == "VirtualRide":
        color = "pink"
    else:
        color = "green"

    activity_polyline = activity["map"]["summary_polyline"]
    coordinates = decodePolyline(activity_polyline, precision=5)

    # Add a PolyLine to connect the coordinates
    folium.PolyLine(coordinates, color=color, weight=2.5, opacity=0.5).add_to(mymap)


# Save the map to an HTML file
heatmap_name = "map.html"
mymap.save(heatmap_name)
