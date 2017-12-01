from datetime import datetime
from pytz import timezone
from telenot import bot


def localizer(tz_name):
    tz = timezone(tz_name)
    def inner(*args):
        return tz.localize(datetime(*args))
    return inner


def test_parse_reminders():
    assert bot.parse_reminder('tomorrow 10 pet the dog') == (
        True, 1, (10, 0), 'pet the dog')
    assert bot.parse_reminder('today 20 garbage') == (
        True, 0, (20, 0), 'garbage')
    assert bot.parse_reminder('+3 10:50 check the postbox') == (
        True, 3, (10, 50), 'check the postbox')
    assert bot.parse_reminder('14 11:00 concert at 19:00') == (
        False, (0, 14), (11, 0), 'concert at 19:00')
    assert bot.parse_reminder('12 11:00 concert at 19:00') == (
        False, (0, 12), (11, 0), 'concert at 19:00')
    assert bot.parse_reminder('15.10 10:30 supper with sister at 20:00') == (
        False, (10, 15), (10, 30), 'supper with sister at 20:00')


def test_notification_datetime():
    l = localizer('Europe/Moscow')
    now = l(2017, 9, 13, 18)

    assert bot.notification_datetime(now, True, (0, 3), (20, 10)) == l(2017, 9, 16, 20, 10)
    assert bot.notification_datetime(now, False, (10, 3), (20, 10)) == l(2017, 10, 3, 20, 10)
    assert bot.notification_datetime(now, False, (8, 3), (20, 10)) == l(2018, 8, 3, 20, 10)

    assert bot.notification_datetime(now, False, (0, 20), (20, 10)) == l(2017, 9, 20, 20, 10)
    assert bot.notification_datetime(now, False, (0, 3), (20, 10)) == l(2017, 10, 3, 20, 10)

    now = l(2017, 12, 13, 18)
    assert bot.notification_datetime(now, False, (0, 3), (20, 10)) == l(2018, 1, 3, 20, 10)
