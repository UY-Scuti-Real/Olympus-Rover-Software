# Driver
from modules import network_module
from modules import message_format_module
# MODE ========================================================================
MODE = [1]
try:
    from adafruit_servokit import ServoKit
    kit = ServoKit(channels=16)
except (NotImplementedError, ImportError):
    print("unable to access electronics, moving to print mode")
    MODE = [0]

# =============================================================================
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

>#--#--#
 3  2  1

if the rover has debug LEDs/sounds, should be presented as
on, output number respectively
"""


class servo:
    def __init__(self, channel, min_pulse=0, max_pulse=0):
        self.channel = int(channel)
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse

    def __call__(self, val):
        pass

    def calibrate(self):
        pass


class continous_servo(servo):
    def __init__(self, channel, min_pulse=0, max_pulse=0):
        # might be from python 2, keeping for austerity
        # super(continous_servo, self).__init__(channel, min_pulse, max_pulse)
        super().__init__(channel, min_pulse, max_pulse)
        if min_pulse and max_pulse:
            self.calibrate()

    def __call__(self, throttle):
        if -1 <= throttle <= 1:
            kit.continuous_servo[self.channel].throttle = throttle
        else:
            pass

    def calibrate(self):
        kit.continuous_servo[self.channel].set_pulse_width_range(self.min_pulse,
                                                                self.max_pulse)


class standard_servo(servo):
    def __init__(self, channel, min_pulse=0, max_pulse=0):
        # super(standard_servo, self).__init__(channel, min_pulse, max_pulse)
        super().__init__(channel, min_pulse, max_pulse)
        if min_pulse and max_pulse:
            self.calibrate()

    def __call__(self, angle):
        # print(self.channel, type(self.channel))
        if 0 <= angle <= 180:
            kit.servo[self.channel].angle = angle
        else:
            pass

    def calibrate(self):
        kit.servo[self.channel].set_pulse_width_range(self.min_pulse,
                                                      self.max_pulse)


def get_map_from_mode(mode):
    if 0 in mode:
        return print_map
    elif 1 in mode:
        return electronics_map


def update(speeds):
    if 0 in MODE:
        print("\n")
    if speeds is not None:
        for speed in speeds:
            if speed in mode_map:
                try:
                    mode_map[speed](float(speeds[speed]))
                except Exception as e:
                    print("bill nye meme", e, speed)


def debug_print(statement):
    str_num = str(statement)[:4]
    print(str_num, " ",  end='')

# MAIN ==============================================================
# wheel declartions (calibration needed)
wheel1 = continous_servo(0)
wheel2 = continous_servo(1)
wheel3 = continous_servo(2)
wheel4 = continous_servo(3)
wheel5 = continous_servo(4)
wheel6 = continous_servo(5)
# gimbal declarations (calibration needed)
gimbal1 = standard_servo(6)
gimbal2 = standard_servo(7)
gimbal3 = standard_servo(8)
gimbal4 = standard_servo(9)
# arm declartions (calibration needed)
shoulder = standard_servo(10)
elbow = standard_servo(11)
grabber = standard_servo(12)
waist = standard_servo(13)
cargo = standard_servo(14)

print_map = {"w1": debug_print,
             "w2": debug_print,
             "w3": debug_print,
             "w4": debug_print,
             "w5": debug_print,
             "w6": debug_print,
             "g1": debug_print,
             "g2": debug_print,
             "g3": debug_print,
             "g4": debug_print,
             "a1": debug_print,
             "a2": debug_print,
             "a3": debug_print,
             "a4": debug_print,
             "p4": debug_print,
             }

electronics_map = {"w1": wheel1,
                   "w2": wheel2,
                   "w3": wheel3,
                   "w4": wheel4,
                   "w5": wheel5,
                   "w6": wheel6,
                   "g1": gimbal1,
                   "g2": gimbal2,
                   "g3": gimbal3,
                   "g4": gimbal4,
                   "a1": shoulder,
                   "a2": elbow,
                   "a3": grabber,
                   "a4": waist,
                   "p1": cargo,
                   }

null_map = {"w1": 0,
            "w2": 0,
            "w3": 0,
            "w4": 0,
            "w5": 0,
            "w6": 0,
            "g1": 90,
            "g2": 90,
            "g3": 90,
            "g4": 90,
            "a1": 180,
            "a2": 0,
            "a3": 0,
            }

print("Starting driver")
command_server = network_module.make_server(5000)
command_server.get_connection()
mode_map = get_map_from_mode(MODE)
while 1:
    string_messages = command_server.get_messages()
    cmd_dict = message_format_module.get_valid_cmds(string_messages)
    update(cmd_dict)
