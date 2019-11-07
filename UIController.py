import time,math
from klampt import vis
from klampt import WorldModel
import threading
from Motion.motion_client import MotionClient
from Motion.motion import Motion
import json

model_name = "Motion/data/TRINA_world_reflex.xml"

class UIController:
    """handles UI_state and motion controller logic
    """
    def __init__(self):
        self.dt = 0.5
        self.robot = MotionClient()
        self.UI_state = {}
        res = self.robot.startup()
        if not res:
            return
        world = WorldModel()
        res = world.readFile(model_name)
        if not res:
            raise RuntimeError("Unable to load Klamp't model")
       
        self.vis_robot = world.robot(0)

        controlThread = threading.Thread(target = self._visualUpdateLoop)
        controlThread.start()

        vis.add("world",world)
        vis.show()

    def _visualUpdateLoop(self):
        while not self.robot.isShutDown():
            q = self.robot.getKlamptSensedPosition()
            self.vis_robot.setConfig(q)
            time.sleep(self.dt)
            print(q)

    def updateState(self,state):
        self.UI_state = state

    def moveRobotTest(self):
        self.robot.setBaseVelocity([0,0])
        leftUntuckedConfig = [-0.2028,-2.1063,-1.610,3.7165,-0.9622,0.0974] #motionAPI format
        init_leftUntuckedConfig = [0,0,0,0,0,0] #motionAPI format
        self.robot.setLeftLimbPositionLinear(leftUntuckedConfig,5)
        # self.robot.setLeftLimbPositionLinear(init_leftUntuckedConfig,5)


if __name__ == "__main__" : 
    a = UIController()
    a.moveRobotTest()