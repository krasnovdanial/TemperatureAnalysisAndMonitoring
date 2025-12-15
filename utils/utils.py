from datetime import datetime


def get_season(dt):
    if isinstance(dt, str):
        dt = datetime.strptime(dt, "%Y-%m-%d")

    month = dt.month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"
