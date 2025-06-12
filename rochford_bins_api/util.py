from datetime import datetime
import re

def parse_date(date: str, year: str) -> datetime:
    """
    Parse a date in the format "Monday 1st January", and a year into a python date object

    Handles multiple spaces in between date components, e.g. "Monday   1st January"
    """
    date_with_year = " ".join(date.split() + [year])
    return datetime.strptime(date_with_year, "%A %d %B %Y")

def weekday_to_int(weekday: str) -> int:
    days = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }
    return days[weekday]


def slugify(text: str) -> str:
    """
    Replace non-alphanumeric characters with hyphens
    """
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-").lower()
