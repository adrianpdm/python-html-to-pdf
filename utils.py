from datetime import datetime
import re

"""
date value variants:
1. YYYY-MM-DD, e.g 2023-01-01
2. ISO timestamp. e.g 2023-07-04T03:06:28.125594+00:00
"""
def udf_date_parse(date):
    try:
        return datetime.strptime(date, '%Y-%m-%d')
    except Exception as e:
        if ('unconverted data remains' in str(e)):
            return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z')
        else:
            raise e


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

    start_date = udf_date_parse(date1)
    end_date = udf_date_parse(date2) if date2 else None
    
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
    amount_string = ''
    if (currency == 'IDR'):
        curr_symbol = 'Rp'
        amount_string = f"{amount}"
    if (currency == 'USD'):
        curr_symbol = '$'
        amount_string = "{:.2f}".format(float(amount))
    elif (currency == 'skip'):
        curr_symbol = ''
        amount_string = f"{amount}"
    
    return curr_symbol + ' ' + re.sub(r'(\d)(?=(\d{3})+(?:\.\d+)?$)', r'\1,', amount_string)

"""
txn_dt is taken from booking_details.price_breakdown (live data).
use this to check if txn occurs before billing period start.
e.g billing printed at June, purchase at Mar.
"""
def bill_is_past_txn(txn_dt, billing_period_start):
    a = udf_date_parse(txn_dt)
    b = udf_date_parse(billing_period_start).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=a.tzinfo
    )
    print('bill_is_past_txn')
    print(a, b)
    return a < b

"""
txn_dt is taken from booking_details.price_breakdown (live data).
use this to check if txn occurs after billing period end.
e.g booking purchased at Mar has refund at June,
then billing at Mar should now include that June txn.
"""
def bill_is_future_txn(txn_dt, billing_period_end):
    a = udf_date_parse(txn_dt)
    b = udf_date_parse(billing_period_end).replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=0,
        tzinfo=a.tzinfo,
    )
    print('bill_is_future_txn')
    print(a, b)
    return a > b

"""
Similar to bill_is_past_txn, but took price breakdown list as first argument.
"""
def bill_is_past_booking(price_breakdown_list, billing_period_start):
    bo_data = None
    if price_breakdown_list == None:
        return
    
    for item in price_breakdown_list:
        if item['type'] == 'BO':
            bo_data = item
            break
    
    if (bo_data):
        return bill_is_past_txn(bo_data['txn_dt'], billing_period_start)

"""
Sum of price breakdown within that billing period only.
See bill_is_past_txn and bill_is_future_txn.
"""    
def bill_sum_of_price_breakdown(price_breakdown_list, billing_period_start, billing_period_end):
    if price_breakdown_list == None:
        return
    
    total = 0
    for item in price_breakdown_list:
        if (bill_is_future_txn(item['txn_dt'], billing_period_end)):
            continue
        total = total + item['amount']
    return total