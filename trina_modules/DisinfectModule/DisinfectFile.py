import time,math
import json
import os
import datetime
import csv
import threading
from threading import Thread
import sys
import signal

from klampt.io import resource


class Disinfect:
    def __init__(self,Jarvis = None, debugging = False, mode = 'Kinematic'):
        self.mode = mode
        self.status = 'idle' #states are " idle, active"
        self.state = 'idle' #states are " idle, active
        self.robot = Jarvis
        self.infoLoop_rate = 0.05
        self.dt = 0.025
        self.spawned_obj = False
        self.wipe_obj = None
        signal.signal(signal.SIGINT, self.sigint_handler) # catch SIGINT (ctrl+c)

        stateRecieverThread = threading.Thread(target=self._serveStateReciever)
        main_thread = threading.Thread(target = self._infoLoop)
        stateRecieverThread.start()
        main_thread.start()

    def sigint_handler(self, signum, frame):
        """ Catch Ctrl+C tp shutdown the api,
        there are bugs with using sigint_handler.. not used rn.

        """
    	assert(signum == signal.SIGINT)
    	#logger.warning('SIGINT caught...shutting down the api!')
    	print("SIGINT caught...shutting down the api!")

    def return_threads(self):
    	return [self._serveStateReciever, self._infoLoop]

    def return_processes(self):
    	return []

    def _infoLoop(self):
        while(True):
            self.robot.log_health()
            loop_start_time = time.time()
            status = self.robot.getActivityStatus()

            if(status == 'active'):
                if(self.status == 'idle'):
                    print('\n\n\n starting up Disinfection Module! \n\n\n')
                    self.status = 'active'
                    self.state = 'active'

            elif(status == 'idle'):
                if self.status == 'active':
                    self.state = 'idle'
                    self.status = 'idle'

            elapsed_time = time.time() - loop_start_time
            if elapsed_time < self.infoLoop_rate:
                time.sleep(self.infoLoop_rate - elapsed_time)
            else:
                time.sleep(0.001)

    def _serveStateReciever(self):
        print "Disinfection Module"
        while True:
            if self.state == 'idle':
                pass
            elif self.state == 'active':
                self.robot.setBaseVelocity((0.0, 0.0))
                time.sleep(self.dt)

if __name__ == "__main__" :
    disinfect = Disinfect()
