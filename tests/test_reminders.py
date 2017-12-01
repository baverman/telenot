from telenot.db import models as m
from telenot import reminder

TABLES = [m.Reminder, m.Timezone]


def test_create_get_and_complete_reminders(dbsession):
    r1 = reminder.make_reminder(1, 100, 'boo')
    r2 = reminder.make_reminder(1, 200, 'boo')

    assert reminder.get_ready_reminders(50) == []
    assert reminder.get_ready_reminders(110) == [r1]
    assert reminder.get_ready_reminders(210) == [r1, r2]
    assert reminder.get_ready_reminders(210, 50) == [r2]

    reminder.complete_reminders([r1.id])
    dbsession.refresh(r1)
    assert r1.status == 'done'
    assert reminder.get_ready_reminders(210) == [r2]


def test_set_and_get_user_timezone(dbsession):
    assert not reminder.set_user_timezone(1, 'Boo')

    assert reminder.set_user_timezone(1, 'Europe/Moscow')
    assert reminder.get_user_timezone(1) == 'Europe/Moscow'

    assert reminder.set_user_timezone(1, 'US/Eastern')
    assert reminder.get_user_timezone(1) == 'US/Eastern'

    assert reminder.get_user_timezone(2) is None
