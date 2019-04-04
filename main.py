import wx.adv
import wx
import os
from os import path

TRAY_TOOLTIP = 'Name' 
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
        self.__create_menu_item(menu, 'Edit config', self.on_edit_conf)
        menu.AppendSeparator()
        self.__create_menu_item(menu, 'Refresh', self.on_refresh)
        self.__create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):      
        pass

    def on_edit_conf(self, event):
        os.startfile(path.join(path.dirname(__file__), 'cameras.conf'))
		
    def on_refresh(self, event):
        stop()
        start()

    def on_exit(self, event):
        stop()
        wx.CallAfter(self.Destroy)
        self.frame.Close()

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

from server import Server
import json

from time import sleep
import multiprocessing as mproc

import logging
import logging.config

logging.config.fileConfig('logging.conf', disable_existing_loggers=True)
logger = logging.getLogger('main')

procs = []

def server_target(*args, **kwargs):
    try:
        server = Server(*args, **kwargs)
    except Exception as e:
	    logger.error(f'Unable to initialize server: {e}')
    else:
        server.run()


def start():
    logger.debug(f'Reading configuration file')
    with open('cameras.conf', 'r') as f:
        config = json.load(f)

    logger.debug(f'Starting {len(config["CAMERAS"])} jobs')
	


    for c in config['CAMERAS']:
        try:
            p = mproc.Process(
                target=server_target, args=(('localhost', c['VISCA_PORT']), (c['IP'], c['PORT']), c['LOGIN'], c['PASSWORD'], c['PRESET_RANGE']))
            p.start()
        except Exception as e:
            logger.error(f'Unable to start job: {e}')
        else:
            procs.append(p)

				
def stop():
    logger.info(f'Stopping main process')
    for p in procs:
        if p.is_alive():
            logger.info(f'Terminating PID {p.pid} ({p.name})')
            p.terminate()
	



if __name__ == '__main__':
    from threading import Thread
    t = Thread(target=start, name='servers_thread')
    t.start()
    app = App(False)
    app.MainLoop()
    t.join()
	