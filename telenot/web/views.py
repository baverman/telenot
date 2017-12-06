from functools import wraps

from flask import request
from flaskish import ApiError
from covador import check, item, opt
from covador.flask import query_string

from .. import bot, auth, reminder
from . import app


def api_key_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        key = request.headers.get('X-Api-Key')
        if key:
            try:
                data = auth.decode_apikey(key)
                return func(*args, user_id=data['user_id'], **kwargs)
            except Exception:
                pass
        return ApiError('auth-required', 401)
    return inner


@app.api('/updates', methods=['POST'])
@query_string(key=str | check(auth.is_valid_hook_key, 'Invalid hook key'))
def check_updates():
    bot.handle_updates(request.json())
    return {'result': 'ok'}


@app.api('/reminder/add', methods=['POST'])
@api_key_required
@query_string(at=int, message=str)
def remind_add(user_id, at, message):
    r = reminder.make(user_id, at, message)
    return {'result': r.id}


@app.api('/reminder/update', methods=['POST'])
@api_key_required
@query_string(reminder_id=item(str, src='id'), at=opt(int), message=opt(str))
def remind_update(user_id, reminder_id, at, message):
    reminder.modify(user_id, reminder_id, at, message)
    return {'result': 'ok'}


@app.api('/reminder/delete', methods=['POST'])
@api_key_required
@query_string(reminder_id=item(str, src='id'))
def remind_update(user_id, reminder_id):
    reminder.delete(user_id, reminder_id)
    return {'result': 'ok'}
