from enum import Enum
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from threading import Thread
import math

def create_twist(vel_tuple):
    assert len(vel_tuple) == 2
    rv = Twist()
    rv.linear.x = vel_tuple[0];
    rv.linear.y = 0;
    rv.linear.z = 0;
    rv.angular.x = 0;
    rv.angular.y = 0;
    rv.angular.z = vel_tuple[1];
    return rv

class Spline2d():
    # pose = [x, y, theta (rad)]
    def __init__(self, start_pose, end_pose):
        x0 = start_pose[0]
        x1 = end_pose[0]
        y0 = start_pose[0] 
        y1 = end_pose[1] 
        dx = x1 - x0
        dy = y1 - y0
        self.dist = math.sqrt(dx**2 + dy**2)
        scale = 1.5 * self.dist
        vx0 = scale*math.cos(start_pose[2])
        vx1 = scale*math.cos(end_pose[2])
        vy0 = scale*math.sin(start_pose[2])
        vy1 = scale*math.sin(end_pose[2])

        ax = -2.0*x1 + 2.0*x0 + vx1 + vx0
        ay = -2.0*y1 + 2.0*y0 + vy1 + vy0
        bx = 3.0*x1 - 3.0*x0 - vx1 - 2.0*vx0
        by = 3.0*y1 - 3.0*y0 - vy1 - 2.0*vy0
        cx = vx0
        cy = vy0
        dx = x0
        dy = y0

        self.x_coeffs = [ax, bx, cx, dx]
        self.y_coeffs = [ay, by, cy, dy]
        self.length = self.get_length()

    def get_pose(self, s):
        x = self.x_coeffs[0]*s**3 + self.x_coeffs[1]*s**2 + self.x_coeffs[2]*s + self.x_coeffs[3]
        y = self.y_coeffs[0]*s**3 + self.y_coeffs[1]*s**2 + self.y_coeffs[2]*s + self.y_coeffs[3]
        dx = 3*self.x_coeffs[0]*s**2 + 2*self.x_coeffs[1]*s + self.x_coeffs[2]
        dy = 3*self.y_coeffs[0]*s**2 + 2*self.y_coeffs[1]*s + self.y_coeffs[2]
        theta = math.atan2(dy, dx)
        return (x, y, theta)

    def get_length(self):
        dist = 0
        num_steps = 1000
        for i in range(num_steps - 1):
            i = float(i)
            curr_x, curr_y, _ = self.get_pose(i/num_steps)
            next_x, next_y, _ = self.get_pose((i+1)/num_steps)
            dx = next_x - curr_x
            dy = next_y - curr_y
            dist += math.sqrt(dx**2 + dy**2)
        return dist

    def get_pose_by_dist(self, dist):
        return self.get_pose(dist/self.length)

class Path2d():

    # points - list of poses
    def __init__(self, points):
        self.splines = []
        self.length = 0
        for i in range(len(points)-1):
            spline = Spline2d(points[i], points[i+1])
            self.splines.append(spline)
            self.length += spline.get_length()

    def get_pose(self, s):
        dist = self.length*s
        cum_dist = 0
        for i in range(len(self.splines)):
            spline = self.splines[i]
            cum_dist += spline.length
            if dist < cum_dist:
                return spline.get_pose_by_dist(dist-(cum_dist-spline.length))
        return self.splines[-1].get_pose(1.0)

    def get_pose_by_dist(self, dist):
        return self.get_pose(dist/self.length)

class BaseControlMode(Enum):
    NOTHING = 0
    VELOCITY = 1
    PATH_FOLLOWING = 2

class BaseController:

    def __init__(self, dt):
        self.control_mode = BaseControlMode.NOTHING
        self.enabled = False
        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.imu_sub = rospy.Subscriber("/imu", Imu, self._imu_callback)
        self.control_thread = Thread(target = self._controlLoop)
        self.state_read = False
        self.commanded_vel = [0.0, 0.0]
        self.measured_vel = [0.0, 0.0]
        self.EPS = 0.0001
        self.dt = dt
        self.target_path = None
        self.path_velocity = None

    def _controlLoop(self):
        rate = rospy.Rate(1.0/self.dt)
        while not rospy.is_shutdown() and self.enabled:
            if not self.enabled:
                self.cmd_pub.publish(create_twist((0, 0)))
            elif self.control_mode == BaseControlMode.VELOCITY:
                self.cmd_pub.publish(create_twist(self.commanded_vel))
            elif self.control_mode == BaseControlMode.PATH_FOLLOWING:
                print("here")
                curr_angle = self.target_path.get_pose(float(self.curr_path_point)/self.num_points)[2]
                if self.prev_angle is None:
                    w = 0
                else:
                    w = (curr_angle - self.prev_angle)/self.dt
                cmd = create_twist((self.path_velocity, w))
                self.cmd_pub.publish(cmd)
                self.prev_angle = curr_angle
                self.curr_path_point += 1
            rate.sleep()

    def _imu_callback(self, imu_msg):
        self.state_read = False
        # TODO: figure out position + velocity from imu_msg

    def start(self):
        rospy.init_node("drive_base")
        self.enabled = True
        self.control_thread.start()

    def stopMotion(self):
        self.enabled = False

    def shutdown(self):
        self.enabled = False
        self.commanded_vel = [0.0, 0.0]

    def moving(self):
        if not self.enabled:
            return False
        else:
            return self.commanded_vel[0] > self.EPS or self.commanded_vel[1] > self.EPS

    def setCommandedVelocity(self, cmd_vel):
        if not self.enabled:
            return
        if self.control_mode != BaseControlMode.VELOCITY:
            self.control_mode = BaseControlMode.VELOCITY
        self.commanded_vel = cmd_vel

    # target_path = [] where each element is a 3-tuple (x, y, theta)
    # velocity = float representing constant linear velocity to drive the path
    def setPath(self, target_path, velocity):
        self.target_path = Path2d(target_path)
        self.path_velocity = velocity
        total_path_time = self.target_path.length/self.path_velocity
        self.num_points = int(total_path_time/self.dt)
        self.curr_path_point = 0
        self.prev_angle = None
        if self.control_mode != BaseControlMode.PATH_FOLLOWING:
            self.control_mode = BaseControlMode.PATH_FOLLOWING

    def isPathDone(self):
        return self.curr_path_point == self.num_points

    def getCommandedVelocity(self):
        return self.commanded_vel

    def getMeasuredVelocity(self):
        return self.measured_vel

    def getPosition(self):
        # TODO
        pass

    def markRead(self):
        self.state_read = True

    def newState(self):
        return not self.state_read

    def isEnabled(self):
        return self.enabled
