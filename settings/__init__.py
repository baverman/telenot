import logging
import os.path
import importlib

ROOT = os.path.dirname(os.path.dirname(__file__))
jroot = lambda *parts: os.path.join(ROOT, *parts)

from settings.default import *

if 'PROFILE' in os.environ:
    mod = importlib.import_module('settings.{}'.format(os.environ['PROFILE']))
    globals().update(vars(mod))

if os.path.exists(jroot('settings', 'local.py')):
    from .local import *

# check required settings
invalid_opts = [k for k, v in globals().items() if v == 'UNDEFINED']
if invalid_opts:
    raise RuntimeError('Following options must be defined: {}'.format(invalid_opts))

if LOGGING:
    logging.dictConfig(LOGGING)
else:
    logging.basicConfig(level=LOGGING_LEVEL)
