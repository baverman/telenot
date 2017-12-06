from uuid import uuid4
from base64 import urlsafe_b64encode

from sqlalchemy import Column, String, Integer, Text, Boolean
from . import Base


def gen_id():
    return urlsafe_b64encode(uuid4().bytes).decode('ascii').rstrip('=')


class Status:
    DONE = 'done'
    PENDING = 'pending'


class Timezone(Base):
    __tablename__ = 'timezones'
    user_id = Column(String, primary_key=True)
    timezone = Column(String)


class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(Text)
    message = Column(Text)
    notify_at = Column(Integer)
    status = Column(String, default=Status.PENDING, server_default=Status.PENDING)
