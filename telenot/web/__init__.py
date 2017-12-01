import os

import logging
from flaskish import Flask

import settings

app = Flask('telenot')

# close session after request
from .. import db
app.teardown_request(db.remove_session)

# import views
from . import views
