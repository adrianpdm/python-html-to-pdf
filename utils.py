from datetime import datetime
import re

"""
1. Same month
    2023-01-01, 2023-01-15 -> 1 - 15 Jan 2023
2. Different month
    2023-01-01, 2023-02-15 -> 1 Jan - 15 Feb 2023
Regardless of include_year, year will always be included if:
    1. not current year, or ..
    2. start and end not in same year
"""
def udf_pretty_date(date1, date2 = None, include_year=False):
    today = datetime.today()

    start_date = datetime.strptime(date1, '%Y-%m-%d')
    end_date = datetime.strptime(date2, '%Y-%m-%d') if date2 else None
    
    if (end_date):
        dates_format = None
        # different year
        if (end_date.year != start_date.year):
            dates_format = ('%-d %b %Y', '%-d %b %Y')

        # same year
        else:
            # must include year if:
            # 1. include_year=True, or
            # 2. same year but not current year
            self_include_year = include_year or (today.year not in {start_date.year, end_date.year})
            use_year = ' %Y' if self_include_year else ''

            # different month
            if (end_date.month != start_date.month):
                dates_format = ('%-d %b', f"%-d %b{use_year}")
            # same month   
            else:
                dates_format = ('%-d', f"%-d %b{use_year}")

        if (dates_format == None):
            raise ValueError()
        
        return f"{start_date.strftime(dates_format[0])} - {end_date.strftime(dates_format[1])}"
    else:
        # must include year if
        # 1. include_year=True, or
        # 2. start date is not current year
        self_include_year = start_date.year != today.year or include_year
        date_format = '%-d %b %Y' if self_include_year else '%-d %b'
        return start_date.strftime(date_format)

"""
Nights between 2 date
2023-01-01, 2023-01-15 -> 14 nights
"""
def udf_night_duration(date1, date2):
    start_date = datetime.strptime(date1, '%Y-%m-%d')
    end_date = datetime.strptime(date2, '%Y-%m-%d')
    return (end_date - start_date).days

"""
Currency (IDR, USD)
USD is rounded to 2 decimal
IDR is as-is
"""
def udf_format_currency(amount, currency = 'IDR'):
    curr_symbol = ''
    if (currency == 'IDR'):
        curr_symbol = 'Rp'
        amount_string = f"{amount}"
    if (currency == 'USD'):
        curr_symbol = '$'
        amount_string = "{:.2f}".format(float(amount))
    elif (currency == 'skip'):
        curr_symbol = ''
    
    return curr_symbol + ' ' + re.sub(r'(\d)(?=(\d{3})+(?:\.\d+)?$)', r'\1,', amount_string)
