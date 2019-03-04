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
    t = threading.Thread(target=Server(('localhost', c['VISCA_PORT']), (c['IP'], c['PORT']), c['LOGIN'], c['PASSWORD']).run)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
