from datetime import datetime

DAYS_MONTHS = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    
def valid_year(year):
    return 1999 < year < 2100
    
def valid_month(month):
    return 0 < month < 13
    
def days_in_month(year, month):
    if not valid_year(year):
        raise ValueError("invalid year (2000 <= year <= 2099)")
    if not valid_month(month):
        raise ValueError("invalid month")
    return 29 if (month == 2 and year % 4 == 0) else DAYS_MONTHS[month]

def valid_day(year, month, day):
    return 0 < day <= days_in_month(year, month)

def valid_hour(hour):
    return 0 <= hour < 24
    
def valid_minute(minute):
    return 0 <= minute < 60
    
def valid_second(second):
    return 0 <= second < 60

def valid_date(year, month, day):
    return valid_year(year) and valid_month(month) and valid_day(year, month, day)
    
def valid_time(hour, minute, second):
    return valid_hour(hour) and valid_minute(minute) and valid_second(second)
    
def valid_date_time(year, month, day, hour, minute, second):
    return valid_date(year, month, day) and valid_time(hour, minute, second)

def get_base_seed(dt):
    base = (dt.month * dt.day + dt.minute + dt.second) & 0xff
    return (base << 24) | (dt.hour << 16) | (dt.year % 2000)

def seed_to_time_3(seed, year=2000):
    pass

def seed_to_time_4(seed, year=2000, target_month=0, target_second=0):    
    base = seed >> 24
    hour = (seed >> 16) & 0xff
    delay = ((seed & 0xffff) - (year % 2000)) & 0xffffffff

    if hour > 23:
        delay += (hour-23) * 0x10000
        hour = 23
    
    month_range = range(target_month, target_month+1) if target_month else (1)
    
    res = []
    for month in month_range:
        for day in range(1, days_in_month(year, month)+1):
            md = month * day
            for minute in range(60):
                if (md + minute + target_second) & 0xff == base:
                    dt = datetime(year, month, day, hour, minute, target_second)
                    res.append(dt)
    
    return (res, delay)