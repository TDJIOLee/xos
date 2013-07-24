import threading
from openstack.observer import OpenStackObserver
from openstack.event_manager import EventListener

class Backend:
    
    def run(self):
        # start the openstack observer
        observer = OpenStackObserver()
        observer_thread = threading.Thread(target=observer.run)
        observer_thread.start()

        # start event listene
        event_manager = EventListener(wake_up=observer.wake_up)
        event_manager_thread = threading.Thread(target=event_manager.run)
        event_manager_thread.start()
                