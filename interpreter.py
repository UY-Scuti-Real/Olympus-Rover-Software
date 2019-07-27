import math as m
from modules import network_module
from modules import command_formats
from socket import gethostname
"""
--- rover standards ---

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

--- states ---
control state, interpreter state

control
this is the state the controller is in. updates from controller connection

interpreter
state of the electronics signal. gets transmitted as formatted strings
"""


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


def get_wheel_speeds(_, control_state):
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


def get_arm_speeds(interpreter_state, control_state):
    """
    control to command:
    arm delta vertical = arm_horizontal * sensetivity
    needs to get the previous interpreter state of the arm
    """
    if control_state["TOGL_MSC"]["ARM"]:
        if control_state["TOGL_ARM"]:
            interpreter_state["A1"] = control_state["ARM_VERT"]
        else:
            interpreter_state["A2"] = control_state["ARM_VERT"]
    else:
        interpreter_state["a1"] = "KILL"
        interpreter_state["a2"] = "KILL"
        interpreter_state["a3"] = "KILL"
        interpreter_state["a4"] = "KILL"

def input_toggler(interpreter_state, control_state)


def update_interp_state(interpreter_state=interp, control_state=cont):
    wheel_update = get_wheel_speeds(interpreter_state, control_state)
    arm_update = get_arm_speeds(interpreter_state, control_state)
    interpreter_state.update()


def update_command_state(dict_msg, control_state=cont):
    control_state.update(control_state)


def debug_null(*args):
    pass

# MAIN ========================================================================
# c_to_c_map = {"DRV_FWD": debug_null,
#               "DRV_TURN": debug_null,
#               "TOGL_DRV": debug_null,
#               "TOGL_MSC": debug_null,
#               "ARM_VERT": debug_null,
#               "ARM_HORI": debug_null,
#               "SET_SENS": debug_null,
#               "TOGL_GRB": debug_null,
#               "YEET": debug_null,
#               "TOGL_DMP": debug_null,
#               "TOGL_ARM": debug_null,
#             }

print("===INTERPRETER START===")
# MODE = ["DBW", "localhost"]
MODE = ["DBW", "ethernet", 'sendall']
# MODE = ["DBW"]
# MODE = [0]
# MODE = [1]

if 'localhost' in MODE:
    address = gethostname()
    timeout = 0.5
elif 'wifi' in MODE:
    address = '192.168.1.11'
    # timeout = 5e-3
    timeout = 5
elif 'ethernet' in MODE:
    address = '192.168.1.10'
    # timeout = 5e-3
    timeout = 5

print("MODE options: ", *MODE)
print("creating sockets & classes... ", end='')
controller_server = network_module.make_server(5001, timeout=timeout)
driver_client = network_module.make_client()
arm = rover_arm()
# cont = controller_state()
cont = command_formats.state()
interp = command_formats.state()
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
