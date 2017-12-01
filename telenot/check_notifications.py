import sys
import logging
sys.path.insert(0, '.')

import settings
from telenot import bot

log = logging.getLogger('telenot.notifications')

if __name__ == '__main__':
    try:
        bot.check_notifications()
    except KeyboardInterrupt:
        pass
    except Exception:
        log.exception('Check notification error')
