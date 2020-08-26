import os
import sys
from plurk_oauth import PlurkAPI

CONSUMER_KEY = os.getenv('PLURK_APP_KEY', None)
CONSUMER_SECRET = os.getenv('PLURK_APP_SECRET', None)
if CONSUMER_KEY is None or CONSUMER_SECRET is None:
    print('Specify PLURK_APP_KEY or PLURK_APP_SECRET as environment variables.')
    sys.exit(1)

plurk = PlurkAPI(CONSUMER_KEY, CONSUMER_SECRET)
plurk.authorize()
print(plurk.callAPI('/APP/Profile/getOwnProfile'))