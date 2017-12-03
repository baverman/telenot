import sys
import time
import logging
sys.path.insert(0, '.')

import settings
from telenot import bot

log = logging.getLogger('telenot.updates')

if __name__ == '__main__':
    offset = None
    try:
        for _ in range(1000):
            try:
                offset, result = bot.check_updates(offset=offset, timeout=10)
            except Exception:
                log.exception('Get updates error')
                time.sleep(5)
            else:
                bot.handle_updates(result)
    except KeyboardInterrupt:
        pass
