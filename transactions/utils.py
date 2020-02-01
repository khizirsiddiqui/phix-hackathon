import datetime

def last_day_of_month(any_day):
    """
    Get last day of the month: https://stackoverflow.com/a/13565185/7643359
    """
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)