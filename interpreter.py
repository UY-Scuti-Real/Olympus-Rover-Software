import math as m
from modules import network_module
from modules import command_formats
from socket import gethostname
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
# MODE = ["DBW", "localhost"]
MODE = ["DBW", "ethernet", 'sendall']
# MODE = ["DBW"]
# MODE = [0]
# MODE = [1]



def toggle(x, number=False):
    if not number:
        return not x
    else:
        if number < 1:
            return 1
        else:
            return 0.5


# ROVER DRIVE==================================================================
def gimbal_drive(x, y, sensitivity=1):
    speeds = {}
    for wheel in range(0, 6):
        y = -y
        speeds["w{}".format(str(wheel+1))] = y * sensitivity
    speeds["g1"] = (x*90)*sensitivity + 90
    speeds["g2"] = (x*90)*sensitivity + 90
    speeds["g3"] = (x*-90)*sensitivity + 90
    speeds["g4"] = (x*-90)*sensitivity + 90
    return speeds


def differential_drive(x, y, sensitivity=1):
    # divide through by root 2 (hey that rhymes) to enfornce v_rms > 1
    speeds = {
        "w1": (-y - x)/(2**0.5),
        "w2": (y - x)/(2**0.5),
        "w3": (-y - x)/(2**0.5),
        "w4": (y - x)/(2**0.5),
        "w5": (-y - x)/(2**0.5),
        "w6": (y - x)/(2**0.5)
        }
    return speeds


def get_wheel_speeds(control_state):
    if control_state['TOGL_DRV']:
        drive_speeds = differential_drive(control_state['DRV_TURN'],
                                          control_state['DRV_FWD'],
                                          control_state['SET_SENS'])
    else:
        drive_speeds = gimbal_drive(control_state['DRV_TURN'],
                                    control_state['DRV_FWD'],
                                    control_state['SET_SENS'])
    return drive_speeds



# TRIG STUFF ==================================================================
def rad(deg):
    return deg/180 * m.pi


def deg(rad):
    return rad/m.pi*180


def cosine_rule(b, c, A):
    # a^2 =  b^2 + c^2 - 2bccosA
    asqr = (b**2 + c**2 - (2*b*c*m.cos(A)))
    a = m.sqrt(asqr)
    return a


def sine_rule(a, b, A):
    sinb = m.sin(A)/a * b
    return m.asin(sinb)


# ARM BULLSHIT ================================================================
# class rover_arm:
#     def __init__(self):
#         self.L1 = 10  # cm
#         self.L2 = 10  # cm
#         self.L3_check = self.L1**2 + self.L2**2
#         self.theta1 = 179  # IN FUCKING DEGREES
#         self.theta2 = 0.01  # DEGREES
#
#     def inc_theta1(self, angle):
#         self.theta1 = self.validate_angle(self.theta1 - angle)
#         return {"a1": self.theta1}
#
#     def inc_theta2(self, angle):
#         self.theta2 = self.validate_angle(self.theta2 - angle)
#         return {"a2": self.theta2}
#
#     def rotate_arm(self, angle):
#         theta1 = self.theta1
#         theta1 += angle
#         if theta1 > 180:
#             self.theta1 = 180
#         elif theta1 < 0:
#             self.theta1 = 1
#         else:
#             self.theta1 = theta1
#         print("cos t2\t{} \tt2 {:.0f} \t t1 {:.3f}".format(
#             "!", self.theta2, self.theta1))
#         return {"a1": self.theta1}
#
#     def extend_arm(self, length):
#         L3init = self.get_L3()
#         L3new = L3init + length
#         if L3new < L3init and self.theta1 >= 179:
#             theta2 = self.get_T2_from_L3(L3new)
#             self.theta2 = self.validate_angle(theta2)
#         else:
#             T1primeinit = self.get_T1prime(L3init)
#             if L3new >= self.L1 + self.L2:
#                 L3new = (self.L1 + self.L2)*0.99
#             theta2 = self.get_T2_from_L3(L3new)
#             if theta2 > 180:
#                 self.theta2 = 179
#             elif theta2 < 0:
#                 self.theta2 = 1
#             else:
#                 self.theta2 = theta2
#             T1primenew = self.get_T1prime(L3new)
#             self.theta1 = self.validate_angle(
#                 self.theta1 - (T1primenew-T1primeinit))
#         return{"a1": self.theta1, "a2": self.theta2}
#
#     def get_L3(self):
#         L3squared = self.L1**2 + self.L2**2 - 2 * \
#             self.L1*self.L2*m.cos(rad(self.theta2))
#         return L3squared**0.5
#
#     def get_T2_from_L3(self, L3):
#         cosT2 = (L3**2 - self.L1**2 - self.L2**2)/(-2*self.L1*self.L2)
#         T2 = deg(m.acos(cosT2))
#         return T2
#
#     def get_T1prime(self, L3):
#         sinT1diff = self.L1/L3 * m.sin(rad(self.theta2))
#         # might be self.l2 there instead...
#         T1diff = deg(m.asin(abs(sinT1diff)))
#         return self.theta1 - T1diff
#
#     def validate_angle(self, angle):
#         if angle >= 180:
#             angle = 179
#         elif angle <= 0:
#             angle = 1
#         return angle

def update_command_from_control(command_state, control_state):
    pass


# CONTROLLER===================================================================
control_state = command_formats.state()
# MAIN ========================================================================
if 'localhost' in MODE:
    address = gethostname()
    timeout = 0.5
elif 'wifi' in MODE:
    address = '192.168.1.11'
    timeout = 5e-3
elif 'ethernet' in MODE:
    address = '192.168.1.10'
    timeout = 5e-3

print("===INTERPRETER START===")
print("creating sockets & classes... ", end='')
controller_server = network_module.make_server(5001, timeout=timeout)
driver_client = network_module.make_client()
arm = rover_arm()
cont = controller_state()
print("Done. \nconnecting to electronics....", end='')
driver_client.connect_to(5000, address)
print("Done.", end='\n')
controller_server.get_connection()
while 'test' not in MODE:
    str_cmd_msg = controller_server.get_messages()
    dict_msg = command_formats.get_valid_cmds(str_cmd_msg)
    # update control state
    # calculate command state
    # derive command dict
    str_speeds_msg = command_formats.get_strcmds_from_dict(dict_speeds)
    driver_client.send_message(str_speeds_msg)

print("Entering test mode:")
