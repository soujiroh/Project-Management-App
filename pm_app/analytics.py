import os
import pandas as pd

ANALYTICS_FILE = "user_data.csv"


def save_to_csv_analytics(category, count):
    file_exists = os.path.exists(ANALYTICS_FILE)
    df = pd.DataFrame([[category, count]], columns=["Category", "Count"])
    df.to_csv(ANALYTICS_FILE, mode="a", header=not file_exists, index=False)
