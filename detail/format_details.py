"""Format extracted raw information"""
import re


def get_currency(price):
    """Map currency into valid string format"""
    if 'eur' in price or 'EUR' in price:
        currency = 'EUR'
    return currency


def get_symbol_currency(txt):
    """Map currency symbol into valid string format"""
    currency = ''
    if '$' in txt:
        currency = 'USD'
    elif '€' in txt:
        currency = 'EUR'
    else:
        currency = get_currency(txt)
    return currency


def format_date(date_str):
    """Format date in a style of 2021-01-01"""
    date_str = date_str.strip()
    date_list = date_str.split('/')
    date = date_list[0]
    month = date_list[1]
    year = date_list[-1]
    formatted_date = f'{year}-{month}-{date}'
    return formatted_date


def month_dict(month_str):
    """Map month from string to digit"""
    months_check = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12',
    }
    for key in months_check:
        if key in month_str:
            return months_check[key]
    return '01'


def find_date(string):
    """Using regex to match date"""
    date = re.findall(r'\d{1,2}', string)[0]
    return date


def find_year(string):
    """Using regex to match year"""
    year = re.findall(r'\d{4}', string)[0]
    return year


def find_directly_start_date1(string):
    """The simplest way to format needed date"""
    year = find_year(string)
    month = month_dict(string)
    date = find_date(string)
    start_date = f'{year}-{month}-{date}'
    return start_date


def filter_locations(locations):
    """Trim out useless description in location string"""
    clean_locations = []
    useless_locations = ['Vlerick','Campus',',']

    for loc in locations:
        if loc not in useless_locations:
            clean_locations.append(loc)
    return clean_locations
