from sqlalchemy import Column, String, Integer, Text, Boolean
from . import Base


class Status:
    DONE = 'done'
    PENDING = 'pending'


class Timezone(Base):
    __tablename__ = 'timezones'
    user_id = Column(String, primary_key=True)
    timezone = Column(String)


class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Text)
    message = Column(Text)
    notify_at = Column(Integer)
    status = Column(String, default=Status.PENDING, server_default=Status.PENDING)
