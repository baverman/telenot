import sys
import time
import logging
sys.path.insert(0, '.')

import settings
from telenot import bot

log = logging.getLogger('telenot.notifications')

if __name__ == '__main__':
    try:
        for _ in range(1000):
            try:
                bot.check_notifications()
            except Exception:
                log.exception('Check notification error')
            time.sleep(60)
    except KeyboardInterrupt:
        pass
