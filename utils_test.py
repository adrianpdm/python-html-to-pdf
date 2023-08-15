
from datetime import datetime
from utils import \
    udf_pretty_date,\
    udf_format_currency,\
    udf_night_duration

def test_udf_pretty_date():
    this_year = datetime.today().year
    def do_assert(date1, date2 = None, include_year = False, expected = None):
        if (expected == None):
            raise ValueError()
        assert(udf_pretty_date(date1, date2, include_year)) == expected

    # SINGLE DATE
    # 1. Date at current year
    do_assert(
        date1=f"{this_year}-01-29",
        include_year=False,
        expected='29 Jan'
    )
    do_assert(
        date1=f"{this_year}-01-29",
        include_year=True,
        expected=f"29 Jan {this_year}"
    )
    # 2. Date at different year
    do_assert(
        date1='9999-01-29',
        include_year=False,
        expected='29 Jan 9999'
    )
    do_assert(
        date1='9999-01-29',
        include_year=True,
        expected='29 Jan 9999'
    )

    # DATE RANGE
    # 1. Dates at same month, current year
    do_assert(
        date1=f"{this_year}-04-20",
        date2=f"{this_year}-04-24",
        include_year=False,
        expected='20 - 24 Apr'
    )
    do_assert(
        date1=f"{this_year}-04-20",
        date2=f"{this_year}-04-24",
        include_year=True,
        expected=f"20 - 24 Apr {this_year}"
    )

    # 2. Dates at same month, same year, not current year
    do_assert(
        date1='9999-04-20',
        date2='9999-04-24',
        include_year=False,
        expected='20 - 24 Apr 9999'
    )
    do_assert(
        date1='9999-04-20',
        date2= '9999-04-24',
        include_year=True,
        expected='20 - 24 Apr 9999'
    )

    # 3. Dates at different month, current year
    do_assert(
        date1=f"{this_year}-04-20",
        date2=f"{this_year}-06-09",
        include_year=False,
        expected='20 Apr - 9 Jun'
    )
    do_assert(
        date1=f"{this_year}-04-20",
        date2= f"{this_year}-06-09",
        include_year=True,
        expected=f"20 Apr - 9 Jun {this_year}"
    )

    # 4. Dates at different month, same year, not current year
    do_assert(
        date1='9999-04-20',
        date2='9999-06-09',
        include_year=False,
        expected='20 Apr - 9 Jun 9999'
    )
    do_assert(
        date1='9999-04-20',
        date2= '9999-06-09',
        include_year=True,
        expected='20 Apr - 9 Jun 9999'
    )

    # 5. Dates at different year
    do_assert(
        date1='9998-12-31',
        date2='9999-01-06',
        include_year=False,
        expected='31 Dec 9998 - 6 Jan 9999'
    )
    do_assert(
        date1='9998-12-31',
        date2= '9999-01-06',
        include_year=True,
        expected='31 Dec 9998 - 6 Jan 9999'
    )

def test_udf_night_duration():
    assert(udf_night_duration('2023-01-01', '2023-01-02')) == 1
    assert(udf_night_duration('2023-01-01', '2023-01-03')) == 2
    assert(udf_night_duration('2023-01-01', '2023-01-04')) == 3
    assert(udf_night_duration('2023-01-01', '2023-02-01')) == 31

def test_udf_format_currency():
    assert(udf_format_currency(42)) == 'Rp 42'
    assert(udf_format_currency(690)) == 'Rp 690'
    assert(udf_format_currency(4200)) == 'Rp 4,200'
    assert(udf_format_currency(69000)) == 'Rp 69,000'
    assert(udf_format_currency(420690)) == 'Rp 420,690'
    assert(udf_format_currency(6900420)) == 'Rp 6,900,420'
    assert(udf_format_currency(42069042)) == 'Rp 42,069,042'

    assert(udf_format_currency(42, currency='USD')) == '$ 42.00'
    assert(udf_format_currency(42.69, currency='USD')) == '$ 42.69'
    assert(udf_format_currency(690, currency='USD')) == '$ 690.00'
    assert(udf_format_currency(690.42, currency='USD')) == '$ 690.42'
    assert(udf_format_currency(4200, currency='USD')) == '$ 4,200.00'
    assert(udf_format_currency(4200.69, currency='USD')) == '$ 4,200.69'
