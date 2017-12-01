import logging
from datetime import timedelta, datetime

import requests
import pytz
from covador import Date, Time, oneof
from covador.utils import pipe

import settings
from . import reminder

log = logging.getLogger('telenot.bot')
request_session = requests.Session()

DAYS = {
    'today': 0,
    'tomorrow': 1,
}

t_date = oneof(Date('%d') | (lambda d: (0, d.day)),
               Date('%d.%m') | (lambda d: (d.month, d.day)))

t_time = pipe(oneof(Time('%H'), Time('%H:%M')), lambda t: (t.hour, t.minute))


def parse_reminder(string):
    """Parses reminder string

    :param string: text with reminder
    :return: (is_relative, (month, day) or delta, (hour, minute), "message")
    """

    parts = string.split(None, 2)
    if len(parts) != 3:
        raise ValueError('Invalid syntax')

    day, time, message = parts

    if day in DAYS:
        relative = True
        day = DAYS[day]
    else:
        if day.startswith('+'):
            relative = True
            day = int(day)
        else:
            relative = False
            day = t_date(day)

    tm = t_time(time)
    return relative, day, tm, message


def notification_datetime(now, is_relative, dt, tm):
    if is_relative:
        result = now + timedelta(days=dt)
    else:
        if dt[0]:
            result = now.replace(month=dt[0], day=dt[1])
            if result < now:
                result = result.replace(year=result.year + 1)
        else:
            result = now.replace(day=dt[1])
            if result < now:
                delta_y, month = divmod(now.month, 12)
                result = result.replace(year=now.year + delta_y, month=month + 1)

    return result.replace(hour=tm[0], minute=tm[1], second=0, microsecond=0)


def _tele_call(method, _timeout=None, **params):
    params = {k:v for k, v in params.items() if v is not None}
    url = 'https://api.telegram.org/bot{}/{}'.format(settings.TELEGRAM_TOKEN, method)
    resp = request_session.post(url, json=params, timeout=_timeout or 5)
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data.get('ok'), resp.content
    return data['result']


def check_updates(offset=None, timeout=None):
    result = _tele_call('getUpdates', offset=offset, timeout=timeout,
                        _timeout=timeout and timeout + 5)
    next_offset = max((r['update_id'] for r in result), default=None)
    return next_offset and next_offset + 1, result


def check_notifications():
    reminders = reminder.get_ready_reminders(threshold=86400)
    if not reminders:
        return

    completed = []
    for r in reminders:
        try:
            send_message(r.user_id, r.message)
            completed.append(r)
        except Exception:
            log.exception('Error during handling notification')

    reminder.complete_reminders([r.id for r in completed])


def send_message(chat_id, text, **params):
    _tele_call('sendMessage', chat_id=chat_id, text=text, **params)


def handle_updates(updates):
    for u in updates:
        try:
            handle_update(u)
        except Exception:
            log.exception('Error during handling update')


def handle_update(update):
    msg = update.get('message', {})
    text = msg.get('text', '')
    user_id = msg['from']['id']
    chat_id = msg['chat']['id']

    parts = text.split(None, 1)
    if len(parts) > 1:
        cmd, rest = parts
    else:
        cmd = parts[0]
        rest = None

    if cmd == '/tz':
        handle_tz(msg, user_id, chat_id, rest)
    elif cmd == '/remind':
        handle_remind(msg, user_id, chat_id, rest)
    else:
        print(update)


def handle_tz(msg, user_id, chat_id, text):
    if text:
        if reminder.set_user_timezone(user_id, text):
            send_message(chat_id, 'Current timezone is {}'.format(text))
        else:
            send_message(chat_id, 'Invalid timezone {}'.format(text))
    else:
        send_message(chat_id, 'Current timezone is {}'.format(reminder.get_user_timezone(user_id)))


def handle_remind(msg, user_id, chat_id, text):
    if not text:
        return

    is_relative, day, tm, message = parse_reminder(text)

    tz_name = reminder.get_user_timezone(user_id) or 'Moscow/Europe'
    tz = pytz.timezone(tz_name)

    now = pytz.utc.localize(datetime.utcnow()).astimezone(tz)
    next_notification = notification_datetime(now, is_relative, day, tm)

    ts = int(next_notification.astimezone(pytz.utc).timestamp())
    reminder.make_reminder(user_id, ts, message)
    send_message(chat_id, 'Next reminder at {}'.format(next_notification))
