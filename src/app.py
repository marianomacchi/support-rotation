import os
import logging

import requests
import boto3
from botocore.exceptions import ClientError
from pytz import timezone
from datetime import datetime, date
from icalendar import Calendar

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_sns_client = None
_last_rotation_set = None


def sns_client():
    """Loads the sns client lazily"""
    # Lazy initialization allows for an easier mock up of the client in tests, while keeping the AWS recommended
    # best practice of taking advantage of the execution environment in subsequent invocations
    global _sns_client
    if not _sns_client:
        _sns_client = boto3.client('sns')
    return _sns_client


def lambda_handler(event, context):
    try:
        # if the lambda's execution environment is destroyed between invocations, the value of the global variable
        # _last_rotation_set may be lost and an SMS may be sent even if the rotation was already set
        global _last_rotation_set
        calendar = Calendar.from_ical(requests.get(os.environ['calendarUrl']).text)
        current_rotation = get_current_rotation(datetime.now(timezone(os.environ['localTz'])),
                                                os.environ['calendarEncoding'], calendar)
        if current_rotation != _last_rotation_set:
            change_rotation(current_rotation)
            _last_rotation_set = current_rotation
    except requests.exceptions.RequestException as error:
        logger.info(error)
    except ClientError as error:
        logger.info(error.response['Error']['Code'])
        logger.info(error.response['Error']['Message'])


def get_current_rotation(local_time, encoding, calendar):
    """Checks an icalendar to determine the current rotation active according to local time"""
    for calendar_event in calendar.walk('VEVENT'):
        start = calendar_event.decoded('DTSTART')
        end = calendar_event.decoded('DTEND')
        summary = calendar_event.decoded('SUMMARY').decode(encoding)
        if type(start) is date and type(end) is date:
            start = datetime(start.year, start.month, start.day, hour=0, minute=0, second=0, microsecond=0,
                             tzinfo=local_time.tzinfo)
            end = datetime(end.year, end.month, end.day, hour=0, minute=0, second=0, microsecond=0,
                           tzinfo=local_time.tzinfo)
        if start <= local_time <= end:
            return summary


def change_rotation(rotation):
    """Changes the current rotation if it hasn't already been set"""
    sns_client().publish(PhoneNumber=os.environ['supportPhoneNumber'], Message=rotation)
    logger.info(f"Sending SMS to {os.environ['supportPhoneNumber']} with message {rotation}")
