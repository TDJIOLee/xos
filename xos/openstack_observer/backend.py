import threading
import time
from observer.event_loop import XOSObserver
from observer.event_manager import EventListener
from util.logger import Logger, logging
from model_policy import run_policy
from xos.config import Config

logger = Logger(level=logging.INFO)

class Backend:

    def run(self):
        # start the openstack observer
        observer = XOSObserver()
        observer_thread = threading.Thread(target=observer.run)
        observer_thread.start()

        # start model policies thread
        observer_name = getattr(Config(), "observer_name", "")
        if (not observer_name):
            model_policy_thread = threading.Thread(target=run_policy)
            model_policy_thread.start()
        else:
            print "Skipping model policies thread for service observer."


        # start event listene
        #event_manager = EventListener(wake_up=observer.wake_up)
        #event_manager_thread = threading.Thread(target=event_manager.run)
        #event_manager_thread.start()
