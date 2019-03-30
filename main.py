import logging
import logging.config

logging.config.fileConfig('logging.conf', disable_existing_loggers=True)
logger = logging.getLogger('main')

from server import Server
import json

from time import sleep
import multiprocessing as mproc


def server_target(*args, **kwargs):
    try:
        server = Server(*args, **kwargs)
    except Exception as e:
	    logger.error(f'Unable to initialize server: {e}')
    else:
        server.run()


if __name__ == '__main__':
    logger.debug(f'Reading configuration file')
    with open('cameras.conf', 'r') as f:
        config = json.load(f)

    logger.debug(f'Starting {len(config["CAMERAS"])} jobs')
    procs = []
	

    try:
        for c in config['CAMERAS']:
            try:
                p = mproc.Process(
                    target=server_target, args=(('localhost', c['VISCA_PORT']), (c['IP'], c['PORT']), c['LOGIN'], c['PASSWORD'], c['CLIENT_NUMBER']))
                p.start()
            except Exception as e:
                logger.error(f'Unable to start job: {e}')
            else:
                procs.append(p)

        while True:
            sleep(1)

    except (KeyboardInterrupt, SystemExit):
        logger.info(f'Stopping main process')
        for p in procs:
            if p.is_alive():
                logger.info(f'Terminating PID {p.pid} ({p.name})')
                p.terminate()
