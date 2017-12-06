import time

import pytz
from pytz.exceptions import UnknownTimeZoneError

from .db import session
from .db.models import Reminder, Status, Timezone


def make(user_id, notify_at, message, commit=True):
    r = Reminder(user_id=user_id, notify_at=notify_at, message=message)
    session.add(r)
    commit and session.commit()
    return r


def modify(user_id, reminder_id, notify_at=None, message=None, commit=True):
    params = {'notify_at': notify_at, 'message': message, 'status': Status.PENDING}
    params = {k: v for k, v in params.items() if v is not None}
    (session.query(Reminder)
     .filter_by(user_id=user_id, id=reminder_id)
     .update(params, synchronize_session=False))
    commit and session.commit()


def delete(user_id, reminder_id, commit=True):
    (session.query(Reminder)
     .filter_by(user_id=user_id, id=reminder_id)
     .delete(synchronize_session=False))
    commit and session.commit()


def get_ready_to_notificate(now=None, threshold=600):
    now = now or time.time()
    return (session.query(Reminder)
            .filter_by(status=Status.PENDING)
            .filter(Reminder.notify_at.between(now - threshold, now))).all()


def complete(reminder_ids, commit=True):
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
