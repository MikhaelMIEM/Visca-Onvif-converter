from server import Server
import json
import threading

import logging

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='(%(threadName)-10s) %(message)s',
# )

with open('cameras.conf', 'r') as f:
    config = json.load(f)

threads = []
for c in config['CAMERAS']:
    t = threading.Thread(target=Server(c['IP'], c['PORT'], c['VISCA_PORT'], c['LOGIN'], c['PASSWORD']).run)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
