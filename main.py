import wx.adv
import wx
import os
from os import path

TRAY_TOOLTIP = 'visca-onvif converter'
TRAY_ICON = path.join(path.dirname(__file__), '1.png')


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def __create_menu_item(self, menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.Append(item)
        return item

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self.__create_menu_item(menu, 'Show log', self.on_show_log)
        menu.AppendSeparator()
        self.__create_menu_item(menu, 'Edit config', self.on_edit_conf)
        menu.AppendSeparator()
        self.__create_menu_item(menu, 'Reconnect', self.on_reconnect)
        self.__create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_show_log(self, event):
        os.startfile(path.join(path.dirname(__file__), 'main.log'))

    def on_left_down(self, event):
        pass

    def on_edit_conf(self, event):
        os.startfile(path.join(path.dirname(__file__), 'cameras.conf'))

    def on_reconnect(self, event):
        stop()
        start()

    def on_exit(self, event):
        stop()
        wx.CallAfter(self.Destroy)
        self.frame.Close()


class App(wx.App):
    def OnInit(self):
        frame = wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True


from server import Server
import json
import threading
import logging.config

logging.config.fileConfig('logging.conf', disable_existing_loggers=True)
logger = logging.getLogger('main')


jobs = []


class ServerJob(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.running = False
        self.args = args
        self.kwargs = kwargs
        threading.Thread.__init__(self)

    def run(self):
        self.running = True
        try:
            server = Server(*self.args, **self.kwargs)
        except Exception as e:
            logger.error(f'Unable to initialize server: {e}')
            return
        else:
            try:
                while True:
                    if not self.running:
                        logger.info('Job interrupted')
                        return
                    try:
                        server.run_once()
                    except TimeoutError:
                        pass
            except Exception as e:
                logger.error(f'Stopping job: {e}')
                return

    def stop(self):
        self.running = False


def start():
    global jobs
    logger.debug(f'Reading configuration file')
    try:
        with open('cameras.conf', 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f'Unable to load config: {e}')
    else:
        logger.debug(f'Starting {len(config["CAMERAS"])} jobs')
        for c in config['CAMERAS']:
            try:
                job = ServerJob(('localhost', c['VISCA_PORT']),
                                  (c['IP'], c['PORT']),
                                  c['LOGIN'],
                                  c['PASSWORD'],
                                  c['PRESET_RANGE'])
                job.start()
            except Exception as e:
                logger.error(f'Unable to start job: {e}')
            else:
                jobs.append(job)


def stop(timeout=10):
    global jobs
    logger.info(f'Stopping jobs')
    if jobs:
        for j in jobs:
            if j.is_alive():
                logger.info(f'Stopping {j.name}')
                j.stop()
                j.join(timeout=timeout)
                if j.is_alive():
                    logger.warning(f'Cannot stop {j.name}: Timeout')
            else:
                j.join()
                logger.info(f'Job {j.name} already stopped')
    else:
        logger.info('No jobs to stop')
    jobs = []


if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
