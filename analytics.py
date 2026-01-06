import csv
from datetime import datetime

def log_query(user, role, question):
    with open("analytics.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), user, role, question])
