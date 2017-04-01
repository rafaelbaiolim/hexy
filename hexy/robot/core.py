from ..comm.pwm import PWM
from ..config import Config
from time import sleep, time


class Driver(object):
    def __init__(self, throttle=0.0, max_load=18):
        """
        Create a global driver object.
        """
        self.throttle = throttle
        self.max_load = max_load

        self.freq = 0.50

        self.config = Config()
        self.drivers = [PWM(int(addr.split('x')[-1], 16))
                        for addr in self.config['controllers']]

        for driver in self.drivers:
            driver.setPWMFreq(int(self.freq*60))

        self.joint_conf = dict(self.config.items())
        self.last_cmd = {}
        self.idle()

    def num_in_motion(self, since, excluding):
        """
        return the number of servos in motion since the given time,
        excluding the excluded servo.
        
        args:
            since: time period in seconds
        """
        now = time()
        return len([t for t in self.last_cmd.values()
                     if (now - t) <= since])


    def drive(self, joint, val):
        joint_name = 'addr_' + joint.lower()
        controller, channel, pwm_min, pwm_max = self.joint_conf[joint_name]
        driver = self.drivers[controller]
        
        while (val > 0 and
                self.num_in_motion(self.throttle, joint) > self.max_load):
            # Avoid putting too much load on the servos at once by
            # throttling the commands we send
            sleep(self.throttle / 10.0)
            
        driver.setPWM(channel, 0, int(self.freq*val))
        self.last_cmd[joint] = time()


    def idle(self):
        for joint in self.joint_conf:
            if joint.startswith('addr_'):
                self.drive(joint.split('_')[-1], 0)


_driver = None
def get_driver():
    global _driver
    if _driver is None:
        _driver = Driver()
    return _driver


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def remap(old_val, (old_min, old_max), (new_min, new_max)):
    new_diff = (new_max - new_min)*(old_val - old_min) / float((old_max - old_min))
    return int(round(new_diff)) + new_min 


class HexapodCore:

    def __init__(self):
        """
        joint_key convention:
            R - right, L - left
            F - front, M - middle, B - back
            H - hip, K - knee, A - Ankle
            key : (controller, channel, minimum_pulse_length, maximum_pulse_length)
        """


        self.neck = Joint("neck", 'head')

        self.left_front = Leg('left front', 'LFH', 'LFK', 'LFA')
        self.right_front = Leg('right front', 'RFH', 'RFK', 'RFA')

        self.left_middle = Leg('left middle', 'LMH', 'LMK', 'LMA')
        self.right_middle = Leg('right middle', 'RMH', 'RMK', 'RMA')
        
        self.left_back = Leg('left back', 'LBH', 'LBK', 'LBA')
        self.right_back = Leg('right back', 'RBH', 'RBK', 'RBA')

        self.legs = [self.left_front, self.right_front,
                     self.left_middle, self.right_middle,
                     self.left_back, self.right_back]

        self.right_legs = [self.right_front, self.right_middle, self.right_back]
        self.left_legs = [self.left_front, self.left_middle, self.left_back]

        self.tripod1 = [self.left_front, self.right_middle, self.left_back]
        self.tripod2 = [self.right_front, self.left_middle, self.right_back]
        
        self.hips, self.knees, self.ankles = [], [], []

        for leg in self.legs:
            self.hips.append(leg.hip)
            self.knees.append(leg.knee)
            self.ankles.append(leg.ankle)

    def off(self):

        self.neck.off()
        
        for leg in self.legs:
            leg.off() 


class Leg:

    def __init__(self, name, hip_key, knee_key, ankle_key):

        max_hip, max_knee, knee_leeway = 45, 50, 10
        
        self.hip = Joint("hip", hip_key, max_hip)
        self.knee = Joint("knee", knee_key, max_knee, leeway = knee_leeway)
        self.ankle = Joint("ankle", ankle_key)

        self.name = name
        self.joints = [self.hip, self.knee, self.ankle]

    def pose(self, hip_angle = 0, knee_angle = 0, ankle_angle = 0):

        self.hip.pose(hip_angle)
        self.knee.pose(knee_angle)
        self.ankle.pose(ankle_angle)

    def move(self, knee_angle = None, hip_angle = None, offset = 100):
        """ knee_angle < 0 means thigh is raised, ankle's angle will be set to the specified 
            knee angle minus the offset. offset best between 80 and 110 """

        if knee_angle == None: knee_angle = self.knee.angle
        if hip_angle == None: hip_angle = self.hip.angle

        self.pose(hip_angle, knee_angle, knee_angle - offset)

    def replant(self, raised, floor, offset, t = 0.1):

        self.move(raised)
        sleep(t)

        self.move(floor, offset)
        sleep(t)

    def off(self):
        for joint in self.joints:
            joint.off()
        
    def __repr__(self):
        return 'leg: ' + self.name


class Joint:

    def __init__(self, joint_type, jkey, maxx = 90, leeway = 0):

        self.joint_type, self.name =  joint_type, jkey
        joint_addr = 'addr_' + jkey.lower()
        _, _, self.min_pulse, self.max_pulse = get_driver().config[joint_addr]
        self.max, self.leeway = maxx, leeway

        self.off()

    def pose(self, angle = 0):

        angle = constrain(angle, -(self.max + self.leeway), self.max + self.leeway)
        pulse = remap(angle, (-self.max, self.max), (self.min_pulse, self.max_pulse))

        get_driver().drive(self.name, pulse)
        self.angle = angle
        
        #print repr(self), ':', 'pulse', pulse

    def off(self):
        get_driver().drive(self.name, 0)
        self.angle = None

    def __repr__(self):
        return 'joint: ' + self.joint_type + ' : ' + self.name + ' angle: ' + str(self.angle)
 
