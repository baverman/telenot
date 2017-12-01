import time

import pytz
from pytz.exceptions import UnknownTimeZoneError

from .db import session
from .db.models import Reminder, Status, Timezone


def make_reminder(user_id, notify_at, message, commit=True):
    r = Reminder(user_id=user_id, notify_at=notify_at, message=message)
    session.add(r)
    commit and session.commit()
    return r


def get_ready_reminders(now=None, threshold=600):
    now = now or time.time()
    return (session.query(Reminder)
            .filter_by(status=Status.PENDING)
            .filter(Reminder.notify_at.between(now - threshold, now))).all()


def complete_reminders(reminder_ids, commit=True):
    if not reminder_ids:
        return

    (session.query(Reminder)
     .filter(Reminder.id.in_(reminder_ids))
     .update({'status': Status.DONE}, synchronize_session=False))

    commit and session.commit()


def set_user_timezone(user_id, tz_name):
    try:
        tz = pytz.timezone(tz_name)
    except UnknownTimeZoneError:
        return False

    t = session.query(Timezone).get(user_id)
    if not t:
        t = Timezone(user_id=user_id, timezone=tz_name)
        session.add(t)
    else:
        t.timezone = tz_name

    session.commit()
    return True


def get_user_timezone(user_id):
    return session.query(Timezone.timezone).filter_by(user_id=user_id).scalar()
