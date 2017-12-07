from telenot.db import models as m
from telenot import reminder

TABLES = [m.Reminder, m.Timezone]


def test_create_get_and_complete_reminders(dbsession):
    r1 = reminder.make(1, 100, 'boo')
    r2 = reminder.make(2, 200, 'boo')

    reminder.modify(2, r1.id, 101, 'foo')
    dbsession.refresh(r1)
    assert r1.notify_at == 100
    assert r1.message == 'boo'

    reminder.modify(1, r1.id, 101, 'foo')
    dbsession.refresh(r1)
    assert r1.notify_at == 101
    assert r1.message == 'foo'

    assert reminder.get_future_notifications(1, 50) == [r1]
    assert reminder.get_future_notifications(2, 210) == []

    assert reminder.get_ready_to_notificate(50) == []
    assert reminder.get_ready_to_notificate(110) == [r1]
    assert reminder.get_ready_to_notificate(210) == [r1, r2]
    assert reminder.get_ready_to_notificate(210, 50) == [r2]

    reminder.complete([r1.id])
    dbsession.refresh(r1)
    assert r1.status == 'done'
    assert reminder.get_ready_to_notificate(210) == [r2]

    reminder.delete(2, r1.id)
    dbsession.refresh(r1)

    reminder.delete(1, r1.id)
    assert dbsession.query(m.Reminder).filter_by(id=r1.id).first() is None


def test_set_and_get_user_timezone(dbsession):
    assert not reminder.set_user_timezone(1, 'Boo')

    assert reminder.set_user_timezone(1, 'Europe/Moscow')
    assert reminder.get_user_timezone(1) == 'Europe/Moscow'

    assert reminder.set_user_timezone(1, 'US/Eastern')
    assert reminder.get_user_timezone(1) == 'US/Eastern'

    assert reminder.get_user_timezone(2) is None
