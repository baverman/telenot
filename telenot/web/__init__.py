import os

import logging
from flaskish import Flask

import settings

app = Flask('telenot')
if settings.SENTRY:
    from raven.contrib.flask import Sentry
    sentry = Sentry(app, client=settings.sentry_client)

# close session after request
from .. import db
app.teardown_request(db.remove_session)

# import views
from . import views
