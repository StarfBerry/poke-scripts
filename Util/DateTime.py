MONTHS_DAYS = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    
def valid_year(year):
    return 1999 < year < 2100
    
def valid_month(month):
    return 0 < month < 13
    
def days_in_month(year, month):
    return 29 if (month == 2 and year % 4 == 0) else MONTHS_DAYS[month]

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