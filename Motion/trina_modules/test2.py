import threading
import atexit
import multiprocessing
import time


class C2:
    def __init__(self):
        from reem.connection import RedisInterface
        from reem.datatypes import KeyValueStore
        self.name = 'LaWanda'
        self.processes = []
        self.processes.append(multiprocessing.Process(target=self.idle,name = 'karen'))
        self.processes.append(multiprocessing.Process(target=self.verify,name = 'joshua'))
        self.interface = RedisInterface(host="localhost")
        self.interface.initialize()
        self.server = KeyValueStore(self.interface)
        self.sleep_time = 30
        atexit.register(self.shutdown)
        for i in self.processes:
            i.start()
        # while(True):
        #     print('hahahaha you can see this? ')
    def idle(self):
        while(True):
            # print('idling C2')
            time.sleep(self.sleep_time)
    def verify(self):
        while(True):
            try:
                self.server['health_log']['C2'] = [True,time.time()]
                time.sleep(1)
            except Exception as e:
                print(e)
    def shutdown(self):
        print('shutting the whole circus down')
        for i in self.processes:
            i.terminate()
    def return_processes(self):
        return self.processes
