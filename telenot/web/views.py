from flask import request
from covador import check
from covador.flask import query_string

import settings
from .. import bot
from . import app


def is_valid_key(key):
    return settings.HOOK_KEY and key == settings.HOOK_KEY


@app.api('/test')
def check_updates():
    return bot.check_updates()


@app.api('/updates')
@query_string(key=str | check(is_valid_key, 'Invalid hook key'))
def check_updates():
    bot.handle_updates(request.json())
    return {'result': 'ok'}
