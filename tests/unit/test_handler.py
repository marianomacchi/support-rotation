import datetime

import pytz
from icalendar import Calendar
import pytest

from src import app


@pytest.fixture()
def local_tz():
    return pytz.timezone('Europe/Rome')


@pytest.fixture()
def calendar_encoding():
    return 'utf-8'


@pytest.fixture()
def mock_calendar():
    with open('mock_icalendar.ics') as icalendar_file:
        icalendar_data = icalendar_file.read()
    return Calendar.from_ical(icalendar_data)


def test_get_current_rotation_with_date(local_tz, calendar_encoding, mock_calendar):
    naive_local_time = datetime.datetime.fromisoformat('2022-06-28T00:00:00')
    tz_aware_local_time = local_tz.localize(naive_local_time)
    current_rotation = app.get_current_rotation(tz_aware_local_time, calendar_encoding, mock_calendar)
    assert 'EmployeeA' == current_rotation


def test_get_current_rotation_with_datetime(local_tz, calendar_encoding, mock_calendar):
    naive_local_time = datetime.datetime.fromisoformat('2022-06-29T12:00:01')
    tz_aware_local_time = local_tz.localize(naive_local_time)
    current_rotation = app.get_current_rotation(tz_aware_local_time, calendar_encoding, mock_calendar)
    assert 'EmployeeB' == current_rotation


def test_get_current_rotation_with_overlapping_datetime(local_tz, calendar_encoding, mock_calendar):
    naive_local_time = datetime.datetime.fromisoformat('2022-06-29T12:00:00')
    tz_aware_local_time = local_tz.localize(naive_local_time)
    current_rotation = app.get_current_rotation(tz_aware_local_time, calendar_encoding, mock_calendar)
    assert 'EmployeeA' == current_rotation

