import logging

logger = logging.getLogger(__name__)

from server import Server
import json

from time import sleep
import multiprocessing as mproc

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='(%(threadName)-10s) %(message)s',
# )

if __name__ == '__main__':
    logger.debug(f'Reading configuration file')
    with open('cameras.conf', 'r') as f:
        config = json.load(f)

    logger.debug(f'Starting {len(config["CAMERAS"])} jobs')
    procs = []

    for c in config['CAMERAS']:
        try:
            p = mproc.Process(target=Server(('localhost', c['VISCA_PORT']), (c['IP'], c['PORT']), c['LOGIN'], c['PASSWORD']).run)
            p.start()
        except Exception as e:
            logger.warning(f'Unable to start job: {e}')
        else:
            procs.append(p)

    while True:
        try:
            sleep(1)
        except KeyboardInterrupt as e:
            logger.warning(f'Stopping main process: {e}')
            for p in procs:
                if p.is_alive():
                    logger.info(f'Terminating PID {p.pid} ({p.name})')
                    p.terminate()
            break
