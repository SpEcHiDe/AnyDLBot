# ----------------
# dont forget 'pip install requests' first
# ----------------
# usage example:
#
# import botan
#
# print botan.track(1111, 1, {'text':2}, 'Search')

import requests
import json

TRACK_URL = 'https://api.botan.io/track'
SHORTENER_URL = 'https://api.botan.io/s/'

class Botan:

    def track(token, uid, message, name='Message'):
        try:
            r = requests.post(
                TRACK_URL,
                params={"token": token, "uid": uid, "name": name},
                data=json.dumps(message),
                headers={'Content-type': 'application/json'},
            )
            return r.json()
        except requests.exceptions.Timeout:
            # set up for a retry, or continue in a retry loop
            return False
        except (requests.exceptions.RequestException, ValueError) as e:
            # catastrophic error
            print(e)
            return False


    def shorten_url(url, botan_token, user_id):
        """
        Shorten URL for specified user of a bot
        """
        try:
            return requests.get(SHORTENER_URL, params={
                'token': botan_token,
                'url': url,
                'user_ids': str(user_id),
            }).text
        except:
            return url
