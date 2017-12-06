import itsdangerous
import settings

jwt = itsdangerous.JSONWebSignatureSerializer(settings.SECRET)


def is_valid_hook_key(key):
    return settings.HOOK_KEY and key == settings.HOOK_KEY


def decode_apikey(key):
    return jwt.loads(key, salt='apikey')


def make_apikey(user_id):
    return jwt.dumps({'user_id': user_id}, salt='apikey').decode()
