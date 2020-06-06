import time,math,datetime
import threading
from motion_client_python3 import MotionClient
import json
from multiprocessing import Process, Manager, Pipe
import numpy as np
from scipy.spatial.transform import Rotation as R
import os,csv,sys
from threading import Thread
from reem.connection import RedisInterface
from reem.datatypes import KeyValueStore
import traceback
from multiprocessing import Pool, TimeoutError
import uuid
from klampt import io
# from Modules import *
import trina_modules
import sys, inspect
# import command_server

class Jarvis:

    def __init__(self, priority = 'P4'):
        self.interface = RedisInterface(host="localhost")
        self.interface.initialize()
        self.server = KeyValueStore(self.interface)
        self.priority = priority
		# should not instantiate commanserver
		# self.command_server = CommandServer()

	# def shutdown(self):
	#     self.command_server.shutdown()

    def sensedBaseVelocity(self):
        return self.server["ROBOT_STATE"]["Velocity"]["Base"].read()

    def sensedLeftLimbVelocity(self):
        return self.server["ROBOT_STATE"]["Velocity"]["LeftArm"].read()

    def sensedRightLimbVelocity(self):
        return self.server["ROBOT_STATE"]["Velocity"]["RightArm"].read()

    def sensedBasePosition(self):
        return self.server["ROBOT_STATE"]["Position"]["Base"].read()

    def sensedTorsoPosition(self):
        return self.server["ROBOT_STATE"]["Position"]["Torso"].read()

    def sensedLeftLimbPosition(self):
        return self.server["ROBOT_STATE"]["Position"]["LeftArm"].read()

    def sensedRightLimbPosition(self):
        return self.server["ROBOT_STATE"]["Position"]["RightArm"].read()

    def sensedBasePosition(self):
        return self.server["ROBOT_STATE"]["Position"]["Base"].read()

    def sensedLeftGripperPosition(self):
        return self.server["ROBOT_STATE"]["Position"]["LeftGripper"].read()

    def setLeftLimbPosition(self,q):
        command = self.send_command('self.robot.setLeftLimbPosition',str(q))
        current_list = self.server['ROBOT_COMMAND']['P4'].read()
        current_list.append(command)
        self.server['ROBOT_COMMAND'][self.priority] = current_list

    def setBaseVelocity(self,q):
        command = self.send_command('self.robot.setBaseVelocity',str(q))
        queue = self.server['ROBOT_COMMAND'][self.priority].read()
        queue.append(command)
        self.server['ROBOT_COMMAND'][self.priority] = queue



################################## All Mighty divider between motion and UI###############################

    def getRayClickUI(self):
        """once this function is called, the UI will ask the user to click twice on the map, and sending back 
        2 ray objects according to the user clicks. first one for destination, second one for calibration
        
        return:
            {
                'FIRST_RAY': {'destination': [-0.8490072256426063,-0.2846905378876157,-0.4451269801347757],
                            'source': [12.653596500469428, 1.6440497080649081, 5.851982763380186]},
                'SECOND_RAY': {'destination': [-0.8590257360168888,-0.20712234383654582,-0.46816142466493127],
                            'source': [12.653596500469428, 1.6440497080649081, 5.851982763380186]}
            }
        blocking?:
            yes
        """
        id = '$'+ uuid.uuid1().hex
        self.server['UI_FEEDBACK'][str(id)] = {'REPLIED':False, 'MSG':''}
        # ask the user to click on a destination in the map, returns 2 rays in reem
        self._do_rpc({'funcName':'getRayClick','args':{'id':str(id)}})
        reply = self.checkFeedback(id)
        return  reply

    def addTextUI(self, text, position):
        """add text to specfified location on UI screen. 

        args:
            text: (str) content you wish to add
            position: (str) positions of the text: (x,y) position of the upper left corner
            of the text on the screen

        return:
            nothing 

        blocking?:
            no
        """
        self._do_rpc({'funcName':'addText','args':{'text':text,'position':position}})
        return

    def addConfirmationUI(self,title,text):
        """once this function is called, the UI will display a confimation window with specified title and text, 
            a string of 'YES' or "NO" is returned

        args:
            text: (str) content you wish to add
            title: (str) window title

        return:
            (str) 'YES' or 'NO'

        blocking?:
            yes
        """
        id = '$'+ uuid.uuid1().hex
        self.server['UI_FEEDBACK'][str(id)] = {'REPLIED':False, 'MSG':''}
        self._do_rpc({'funcName':'addConfirmation','args':{'id':str(id),'title':title,'text':text}})
        reply = self.checkFeedback(id)
        return  reply

    def addPromptUI(self,title,text):
        id = '$'+ uuid.uuid1().hex
        # TODO
        return  id

    def addInputBoxUI(self,title,text,fields):
        id = '$'+ uuid.uuid1().hex
        # TODO
        return id

    def sendTrajectoryUI(self,trajectory,animate):
        """send a trajectory to UI, UI will add the path preview and animate? the robot ghost immediately for only once 
        args:
            trajectory: (klampt obj) the traj calculated
            animate: (bool) if user wants to animate the path

        return:
            nothing

        blocking?:
            no
        """
        trajectory = io.loader.toJson(trajectory,'Trajectory')
        self._do_rpc({'funcName':'sendTrajectory','args':{'trajectory':trajectory, 'animate':animate}})
        return













    # helper func
    def send_command(self,command,*args):
        final_string = str(command)+ '('
        for index,arg in enumerate(args):
            if(index != len(args)-1):
                final_string += '{},'
            else:
                final_string += '{}'
        final_string = (final_string + ')')
        final_string = final_string.format(*args)
        return final_string

    def checkFeedback(self,id):
        while not self.server['UI_FEEDBACK'][str(id)]['REPLIED'].read():
            continue
        return self.server['UI_FEEDBACK'][str(id)]['MSG'].read()

    def _do_rpc(self,msg):
        commandQueue = self.server["UI_END_COMMAND"].read()
        commandQueue.append(msg)
        self.server["UI_END_COMMAND"] = commandQueue
        print("commandQueue", commandQueue)
        time.sleep(0.0001) 

if __name__=="__main__":
	server = Jarvis()
