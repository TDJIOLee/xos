import threading
import requests, json

from planetstack.config import Config

import uuid
import os
import imp
import inspect
import base64
from fofum import Fofum
import json
import traceback

random_client_id=None
def get_random_client_id():
    global random_client_id

    if (random_client_id is None) and os.path.exists("/opt/planetstack/random_client_id"):
        # try to use the last one we used, if we saved it
        try:
            random_client_id = open("/opt/planetstack/random_client_id","r").readline().strip()
            print "get_random_client_id: loaded %s" % random_client_id
        except:
            print "get_random_client_id: failed to read /opt/planetstack/random_client_id"

    if random_client_id is None:
        random_client_id = base64.urlsafe_b64encode(os.urandom(12))
        print "get_random_client_id: generated new id %s" % random_client_id

        # try to save it for later (XXX: could race with another client here)
        try:
            open("/opt/planetstack/random_client_id","w").write("%s\n" % random_client_id)
        except:
            print "get_random_client_id: failed to write /opt/planetstack/random_client_id"

    return random_client_id

# decorator that marks dispatachable event methods
def event(func):
    setattr(func, 'event', func.__name__)
    return func

class EventHandler:
    # This code is currently not in use.
    def __init__(self):
        pass

    @staticmethod
    def get_events():
        events = []
        for name in dir(EventHandler):
            attribute = getattr(EventHandler, name)
            if hasattr(attribute, 'event'):
                events.append(getattr(attribute, 'event'))
        return events

    def dispatch(self, event, *args, **kwds):
        if hasattr(self, event):
            return getattr(self, event)(*args, **kwds)
            

class EventSender:
    def __init__(self,user=None,clientid=None):
        try:
            user = Config().feefie_client_user
        except:
            user = 'pl'

        try:
            clid = Config().feefie_client_id
        except:
            clid = get_random_client_id()
            print "EventSender: no feefie_client_id configured. Using random id %s" % clid

        self.fofum = Fofum(user=user)
        self.fofum.make(clid)

    def fire(self,**kwargs):
        kwargs["uuid"] = str(uuid.uuid1())
        self.fofum.fire(json.dumps(kwargs))

class EventListener:
    def __init__(self,wake_up=None):
        self.handler = EventHandler()
        self.wake_up = wake_up
        self.deleters = {}
        self.load_deleter_modules()

    def load_deleter_modules(self, deleter_dir=None):
        if deleter_dir is None:
            if hasattr(Config(), "observer_deleters_dir"):
                deleter_dir = Config().observer_deleters_dir
            else:
                deleter_dir = "/opt/planetstack/observer/deleters"

        for fn in os.listdir(deleter_dir):
            pathname = os.path.join(deleter_dir,fn)
            if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py"):
                module = imp.load_source(fn[:-3],pathname)
                for classname in dir(module):
                    c = getattr(module, classname, None)

                    # make sure 'c' is a descendent of Deleter and has a
                    # provides field (this eliminates the abstract base classes
                    # since they don't have a provides)

                    if inspect.isclass(c) and issubclass(c, Deleter) and hasattr(c,"model") and c.model!=None:
                        modelName = c.model
                        if not modelName in self.deleters:
                            self.deleters[modelName] = []
                        if not (c in self.deleters[modelName]):
                            self.deleters[modelName].append(c)
        print 'loaded deleters: %s' % ",".join(self.deleters.keys())


    def handle_event(self, payload):
        payload_dict = json.loads(payload)

        try:
            deletion = payload_dict.get('delete_flag', False)
            if (deletion):
                model = payload_dict['model']
                pk = payload_dict['pk']
                model_dict = payload_dict['model_dict']

                for deleter in self.deleters[model]:
                    try:
                        deleter()(pk, model_dict)
                    except:
                        # something is silently eating these
                        # exceptions...
                        traceback.print_exc()
                        raise
        except:
            deletion = False

        if (not deletion and self.wake_up):
            self.wake_up()

    def run(self):
        # This is our unique client id, to be used when firing and receiving events
        # It needs to be generated once and placed in the config file

        try:
            user = Config().feefie_client_user
        except:
            user = 'pl'

        try:
            clid = Config().feefie_client_id
        except:
            clid = get_random_client_id()
            print "EventListener: no feefie_client_id configured. Using random id %s" % clid

        f = Fofum(user=user)
        
        listener_thread = threading.Thread(target=f.listen_for_event,args=(clid,self.handle_event))
        listener_thread.start()