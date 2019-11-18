from SimpleXMLRPCServer import SimpleXMLRPCServer
import signal
import sys
from motion import Motion

##global variable
robot = Motion(mode = "Physical")
def sigint_handler(signum,frame):
	robot.shutdown()
	sys.exit(0)

def _startup():
	return robot.startup()

def _setLeftLimbPosition(q):
	robot.setLeftLimbPosition(q)
	return 0

def _setRightLimbPosition(q):
	robot.setRightLimbPosition(q)
	return 0

def _setLeftLimbPositionLinear(q,duration):
	robot.setLeftLimbPositionLinear(q,duration)
	return 0

def _setRightLimbPositionLinear(q,duration):
	robot.setRightLimbPositionLinear(q,duration)
	return 0

def _sensedLeftLimbPosition():
	return robot.sensedLeftLimbPosition()

def _sensedRightLimbPosition():
	return robot.sensedRightLimbPosition()

def _setLeftLimbVelocity(qdot):
	robot.setLeftLimbVelocity(qdot)
	return 0

def _setRightLimbVelocity(qdot):
	robot.setRightLimbVelocity(qdot)
	return 0

def _setLeftEEInertialTransform(Tgarget,duration):
	robot.setLeftEEInertialTransform(Tgarget,duration)
	return 0

def _setRightEEInertialTransform(Tgarget,duration):
	robot.setRightEEInertialTransform(Tgarget,duration)
	return 0

def _setLeftEEVelocity(v = None,w = None, tool = [0,0,0]):
    robot.setLeftEEVelocity(v = v,w = w,tool = tool)
    return 0

def _setRightEEVelocity(v = None,w = None, tool = [0,0,0]):
    robot.setRightEEVelocity(v = v,w = w,tool = tool)
    return 0

def _sensedLeftEETransform():
	return robot.sensedLeftEETransform()

def _sensedRightEETransform():
	return robot.sensedRightEETransform()

def _sensedLeftLimbVelocity():
    return robot.sensedLeftLimbVelocity()

def _sensedRightLimbVelocity():
    return robot.sensedRightLimbVelocity()

def _setBaseTargetPosition(q, vel):
	robot.setBaseTargetPosition(q,vel)
	return 0

def _setBaseVelocity(q):
	robot.setBaseVelocity(q)
	return 0

def _setTorsoTargetPosition(q):
	robot.setTorsoTargetPosition(q)
	return 0

def _sensedBaseVelocity():
    return robot.sensedBaseVelocity()

def _sensedBasePosition():
    return robot.sensedBasePosition()

def _sensedTorsoPosition():
    return robot.sensedTorsoPosition()

def _setGripperPosition(position):
    robot.setGripperPosition(position)
    return 0

def _setGripperVelocity(velocity):
	robot.setGripperVelocity(velocity)
	return 0

def _sensedGripperPosition():
    return robot.sensedGripperPosition()

def _getKlamptCommandedPosition():
	return robot.getKlamptSensedPosition()

def _getKlamptSensedPosition():
    return robot.getKlamptSensedPosition()


def _shutdown():
	robot.shutdown()
	return 0

def _isStarted():
	return robot.isStarted()

def _isShutDown():
	return robot.isShutDown()

def _moving():
	return robot.moving()

def _stopMotion():
	robot.stopMotion()
	return 0

def _resumeMotion():
	robot.resumeMotion()
	return 0

def _mirror_arm_config(config):
	return robot.mirror_arm_config(config)

def _getWorld():
	return robot.getWorld()

def _cartesianDriveFail():
	return robot.cartesianDriveFail()

ip_address = 'localhost'
port = 8000
server = SimpleXMLRPCServer((ip_address,port))
server.register_introspection_functions()
signal.signal(signal.SIGINT, sigint_handler)


##add functions...
server.register_function(_startup,'startup')
server.register_function(_setLeftLimbPosition,'setLeftLimbPosition')
server.register_function(_setRightLimbPosition,'setRightLimbPosition')
server.register_function(_setLeftLimbPositionLinear,'setLeftLimbPositionLinear')
server.register_function(_setRightLimbPositionLinear,'setRightLimbPositionLinear')
server.register_function(_sensedLeftLimbPosition,'sensedLeftLimbPosition')
server.register_function(_sensedRightLimbPosition,'sensedRightLimbPosition')
server.register_function(_setLeftLimbVelocity,'setLeftLimbVelocity')
server.register_function(_setRightLimbVelocity,'setRightLimbVelocity')
server.register_function(_setLeftEEInertialTransform,'setLeftEEInertialTransform')
server.register_function(_setRightEEInertialTransform,'setRightEEInertialTransform')
server.register_function(_setLeftEEVelocity,'setLeftEEVelocity')
server.register_function(_setRightEEVelocity,'setRightEEVelocity')
server.register_function(_sensedLeftEETransform,'sensedLeftEETransform')
server.register_function(_sensedRightEETransform,'sensedRightEETransform')
server.register_function(_sensedLeftLimbVelocity,'sensedLeftLimbVelocity')
server.register_function(_sensedRightLimbVelocity,'sensedRightLimbVelocity')
server.register_function(_setBaseTargetPosition,'setBaseTargetPosition')
server.register_function(_setBaseVelocity,'setBaseVelocity')
server.register_function(_setTorsoTargetPosition,'setTorsoTargetPosition')
server.register_function(_sensedBaseVelocity,'sensedBaseVelocity')
server.register_function(_sensedBasePosition,'sensedBasePosition')
server.register_function(_sensedTorsoPosition,'sensedTorsoPosition')
server.register_function(_setGripperPosition,'setGripperPosition')
server.register_function(_setGripperVelocity,'setGripperVelocity')
server.register_function(_sensedGripperPosition,'sensedGripperPosition')
server.register_function(_getKlamptCommandedPosition,'getKlamptCommandedPosition')
server.register_function(_getKlamptSensedPosition,'getKlamptSensedPosition')
server.register_function(_shutdown,'shutdown')
server.register_function(_isStarted,'isStarted')
server.register_function(_moving,'moving')
server.register_function(_stopMotion,'stopMotion')
server.register_function(_resumeMotion,'resumeMotion')
server.register_function(_mirror_arm_config,'mirror_arm_config')
server.register_function(_getWorld,'getWorld')
server.register_function(_cartesianDriveFail,'cartesianDriveFail')
server.register_function(_startup,'startup')
server.register_function(_isShutDown,'isShutDown')


##
print('#######################')
print('#######################')
print('Server Started')
##run server
server.serve_forever()
	


