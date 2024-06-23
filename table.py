import pandas as pd
from funcs import importJson

activities = importJson("activities.json")
df = pd.DataFrame(activities)
df.to_csv("file.csv")
