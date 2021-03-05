import datetime


def cd_to_datetime(calendar_date):
    return datetime.datetime.strptime(calendar_date, "%d.%m.%Y %H:%M")


def datetime_to_str(dt) -> object:
    return datetime.datetime.strftime(dt, "%d-%m-%Y %H:%M")
