import sys
import logging
sys.path.insert(0, '.')

import settings
from telenot import bot

log = logging.getLogger('telenot.updates')

if __name__ == '__main__':
    offset = None
    try:
        for _ in range(1000):
            offset, result = bot.check_updates(offset=offset, timeout=10)
            bot.handle_updates(result)
    except KeyboardInterrupt:
        pass
