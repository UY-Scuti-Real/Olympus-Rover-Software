import socket as s
import math as m
"""
rover standards

where # is a wheel. adjacent number shows wheel number
from a top down position. wheel codonr is wn, where n is wheel
number.

1#  __  #2
   |  |
3# |  | #4
   |__|
5#      #6

if the rover has gimbals, gimbals as follows, where
gn is the gimbal codon

1#  __  #2
   |  |
 # |  | #
   |__|
3#      #4

as far as the rover arm goes...
an, you know the dril it's the same as before

grab#--#--#
    3  2  1

rotation #4

if the rover has debug LEDs/sounds, should be presented as
on, output number respectively

"""
MODE = "DBW"
# MODE = 0
# MODE = 1

def gimbal_drive(x, y, sensitivity=1):
    speeds = {}
    gimbals = {}
    for wheel in range(0, 6):
        speeds["w{}".format(str(wheel+1))] = y * sensitivity
    speeds["g1"] = x*sensitivity
    speeds["g2"] = x*sensitivity
    speeds["g3"] = -1*x*sensitivity
    speeds["g4"] = -1*x*sensitivity
    return speeds


def differential_drive(x, y, sensitivity=1):
    #normalised by (x**2 + y**2)**0.5
    speeds = {
        "w1":y + x,
        "w2":y - x,
        "w3":y + x,
        "w4":y - x,
        "w5":y + x,
        "w6":y - x
        }
    return speeds

def convert_msg(msg):
    aryform = str(msg).split(",")
    dictform = {}
    for ary in aryform:
        if len(ary) > 0:
            key, value = ary.split(":")
            dictform[key] = value
    return dictform


def toggle(x, number = False):
    if not number:
        return not x
    else:
        if number < 1:
            return 1
        else:
            return 0.5

def transmit(driver_sock, speeds):
    prefiltered_string = str(speeds) + ","
    filter_list = ['{', '}', "'", " "]
    #print(prefiltered_string)
    postfiltered_string = ""
    for char in prefiltered_string:
        if char in filter_list:
            continue
        else:
            postfiltered_string += char
    #print("sending:", postfiltered_string)
    driver_sock.send(postfiltered_string.encode())

    pass
#ROVER DRIVE==============================================================================
class rover_drive:
    def __init__(self):
        self.sensitivity = 1
        self.drive_mode = 1

#TRIG STUFF ==============================================================================
def rad(deg):
    return deg/180 * m.pi


def deg(rad):
    return rad/m.pi*180


def cosine_rule(b, c, A):
    #a^2 =  b^2 + c^2 - 2bccosA
    asqr = (b**2 + c**2 - (2*b*c*m.cos(A)))
    a = m.sqrt(asqr)
    return a


def sine_rule(a, b, A):
    sinb = m.sin(A)/a * b
    return m.asin(sinb)

#ARM BULLSHIT ============================================================================
class rover_arm:
    def __init__(self):
        self.L1 = 10        #cm
        self.L2 = 10        #cm
        self.L3_check = self.L1**2 + self.L2**2
        self.theta1 = 0.01  #IN FUCKING DEGREES
        self.theta2 = 0.01  #DEGREES


    def inc_theta1(self, angle):
        self.theta1 = self.validate_angle(self.theta1 + angle)
        return {"a1":self.theta1}


    def inc_theta2(self, angle):
        self.theta2 = self.validate_angle(self.theta2 + angle)
        return {"a2": self.theta2}


    def rotate_arm(self, angle):
        theta1 = self.theta1
        theta1 += angle
        if theta1 > 180:
            self.theta1 = 180
        elif theta1 < 0:
            self.theta1 = 1
        else:
            self.theta1 = theta1
        print("cos t2\t{} \tt2 {:.0f} \t t1 {:.3f}".format("!", self.theta2, self.theta1))
        return {"a1":self.theta1}

    def extend_arm(self, length):
        L3init = self.get_L3()
        L3new = L3init + length
        if L3new < L3init and self.theta1 >= 179:
            print("your genius fix worked as always mr high IQ rick and morty watcher")
            theta2 = self.get_T2_from_L3(L3new)
            self.theta2 = self.validate_angle(theta2)
        else:
            T1primeinit = self.get_T1prime(L3init)
            if L3new >= self.L1 + self.L2:
                L3new = (self.L1 + self.L2)*0.99
            theta2 = self.get_T2_from_L3(L3new)
            if theta2 > 180:
                self.theta2 = 179
            elif theta2 < 0:
                self.theta2 = 1
            else:
                self.theta2 = theta2
            T1primenew = self.get_T1prime(L3new)
            self.theta1 = self.validate_angle(self.theta1 - (T1primenew-T1primeinit))
            #print("a1", self.theta1, "a2", self.theta2)
        return{"a1":self.theta1, "a2":self.theta2}

    def get_L3(self):
        L3squared = self.L1**2 + self.L2**2 - 2*self.L1*self.L2*m.cos(rad(self.theta2))
        return L3squared**0.5

    def get_T2_from_L3(self, L3):
        cosT2 = (L3**2 - self.L1**2 - self.L2**2)/(-2*self.L1*self.L2)
        #print(cosT2)
        T2 = deg(m.acos(cosT2))
        print("cos t2\t{:.3f} \tt2 {:.0f} \t t1 {:.3f}".format(cosT2, T2, self.theta1))
        return T2

    def get_T1prime(self, L3):
        sinT1diff = self.L1/L3 * m.sin(rad(self.theta2))
        #might be self.l2 there instead...
        T1diff = deg(m.asin(abs(sinT1diff)))
        #print(sinT1diff, T1diff)
        return self.theta1 - T1diff


    def validate_angle(self, angle):
        if angle >= 180:
            angle = 179
        elif angle <= 0:
            angle = 1
        return angle



#CONTROLLER===============================================================================
class controller_state:
    def __init__(self):
        self.status = {
            "ABS_X":0,
            "ABS_Y":0,
            "ABS_RX":0,
            "ABS_RY":0,
            }
        self.drive_mode = True
        self.sensitivity = 1
        self.arm_mode = True
        self.grabber = True
        self.yeet = False
        self.arm_deploy = True
        self.fudge_angle = 1
        self.fudge_length = 1

    def input_switcher(self, dictforminput):
        for key in dictforminput:
            self.status[key] = float(dictforminput[key])
            if key == "BTN_NORTH":
                self.drive_mode = toggle(self.drive_mode)
            elif key == "BTN_WEST":
                self.grabber = toggle(self.grabber)
            elif key == "BTN_TR":
                # print("TOGGLED ARM MODE")
                self.arm_mode = toggle(self.arm_mode)
            elif key == "BTN_TL":
                self.sensitivity = toggle(self.sensitivity, self.sensitivity)
            elif key == "BTN_SOUTH":
                self.yeet = True
            elif key == "ABS_HAT0Y" and dictforminput[key] == 1:
                self.arm_deploy = toggle(self.arm_deploy)


    def get_speeds(self, arm):
        #print(self.status)
        speeds = {}
        if self.drive_mode:
            speeds.update(gimbal_drive(
                self.status["ABS_X"], self.status["ABS_Y"], self.sensitivity))
        else:
            speeds.update(differential_drive(
                self.status["ABS_X"], self.status["ABS_Y"], self.sensitivity))
        if MODE == 0:
            if self.arm_mode:
                #print("Extending arm")
                speeds.update(arm.extend_arm(self.fudge_length*self.sensitivity*self.status["ABS_RY"]))
            else:
                #print("rotating arm")
                speeds.update(arm.rotate_arm(self.fudge_angle*self.sensitivity*self.status["ABS_RY"]))
        elif MODE == "DBW":
            if self.arm_mode:
                speeds.update(arm.inc_theta2(self.fudge_angle*self.sensitivity*self.status["ABS_RY"]))
            else:
                speeds.update(arm.inc_theta1(self.fudge_angle*self.sensitivity*self.status["ABS_RY"]))
        if self.grabber:
            speeds.update({"a3": 180})
        else:
            speeds.update({"a3": 0})
        return speeds



#MAIN=====================================================================================
print("===INTERPRETER START===")
print("creating sockets & classes... ", end = '')
cont_local_sock = s.socket(s.AF_INET, s.SOCK_STREAM)
driver_local_sock = s.socket(s.AF_INET, s.SOCK_STREAM)
arm = rover_arm()
cont = controller_state()
print("Done. \nbinding.... ", end = '')
cont_local_sock.bind(('localhost', 5001))
cont_local_sock.listen()
if MODE != 0:
    print("Done. \nconnecting to electronics....", end = '')
    #takes input commands and turns them into dictionaries of speeds
##    driver_local_sock.connect(('localhost', 5000))
    driver_local_sock.connect(('192.168.1.10', 5000))
    print("Done. \nawaiting connection from controller...", end = '')
    connection, addr  = cont_local_sock.accept()
    print("Done: conn from {}. \nReady for instructions.".format(addr))


    while 1:
        msg = connection.recv(2048).decode()
        #print("msg recvd {}".format(msg))
        dictmsg = convert_msg(msg)
        cont.input_switcher(dictmsg)
        speeds = cont.get_speeds(arm)
        transmit(driver_local_sock, speeds)
else:
    print("Done.\nEntering test mode:")
