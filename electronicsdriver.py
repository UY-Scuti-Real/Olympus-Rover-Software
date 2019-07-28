# Driver
from modules import network_module
from modules import command_formats
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
# MODE ========================================================================
MODE = {}
socket_timeout = 2
time_base = 1


def get_method():
    controller = None
    # zeroth try is GPIO
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
    except (NotImplementedError, ImportError):
        print("Can't contact GPIO, going straight to print")
        MODE["controller"] = "PRINT"
        return controller
    # first try is kit
    try:
        from adafruit_servokit import ServoKit
        controller = ServoKit(channels=16)
    except (NotImplementedError, ImportError):
        print("Failed to import/initiate servokit. Trying Pigpio")
    else:
        MODE["controller"] = "KIT"
        return controller
    # second try is pigpio
    try:
        import pigpio
        global pigpio
        controller = pigpio.pi()
    except (NotImplementedError, ImportError):
        print("Failed to import/initiate pigpio. Setting to printmode")
    else:
        MODE["controller"] = "PIGPIO"
        return controller
    # if those two both failed...
    MODE["controller"] = "PRINT"
    return controller


controller = get_method()
# =============================================================================


def set_servo_to(channel, value_to_set, type, pwm_config=[500, 2500]):
    # alternative methodology: function that makes the function:
    # "set_servo_to" built by "get_method()" based on MODE...
    # this will do for proof of concept
    if "KIT" in MODE and type == "continous_servo":
        # requires throttle -1 <= value_to_set <= 1
        controller.continous_servo[channel].throttle = value_to_set
    elif "KIT" in MODE and type == "standard_servo":
        # requires angle 0 <= value_to_set <= 180
        controller.servo[channel].angle = value_to_set
    elif "PIGPIO" in MODE and type == "continous_servo":
        # requires pulse width 500 <= value_to_set <= 2500
        # convert from fraction to pulse width
        value_to_set = value_to_set * \
            (pwm_config[1]-pwm_config[0]) + pwm_config[0]
        controller.set_servo_pulsewidth(channel, value_to_set)
    elif "PIGPIO" in MODE and type == "standard_servo":
        # requires pulse width 500 <= value_to_set <= 2500
        # convert to fraction from angle
        value_to_set = (value_to_set - 90)/90
        # convert from fraction to pulse width
        value_to_set = value_to_set * \
            (pwm_config[1]-pwm_config[0]) + pwm_config[0]
        controller.set_servo_pulsewidth(channel, value_to_set)
    elif "PRINT" in MODE:
        print("CHNL: {}\tVALU: {}".format(channel, value_to_set))


class servo:
    def __init__(self, channel, min_pulse=0, max_pulse=0):
        self.channel = int(channel)
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        if MODE["controller"] == "PIGPIO":
            controller.set_mode(channel, pigpio.OUTPUT)

    def __call__(self, val):
        if val == "KILL":
            return 0

    def calibrate(self):
        if MODE["controller"] != "KIT":
            return 0
        else:
            controller.servo[self.channel].\
                set_pulse_width_range(self.min_pulse,
                                      self.max_pulse)


class continous_servo(servo):
    def __init__(self, channel, min_pulse=0, max_pulse=0):
        # might be from python 2, keeping for austerity
        # super(continous_servo, self).__init__(channel, min_pulse, max_pulse)
        super().__init__(channel, min_pulse, max_pulse)
        if min_pulse and max_pulse:
            self.calibrate()

    def __call__(self, throttle):
        super().__call__(throttle)
        if -1 <= throttle <= 1:
            set_servo_to(self.channel, throttle, "continous_servo")
        else:
            pass


class standard_servo(servo):
    def __init__(self, channel, min_pulse=0, max_pulse=0):
        # super(standard_servo, self).__init__(channel, min_pulse, max_pulse)
        super().__init__(channel, min_pulse, max_pulse)
        if min_pulse and max_pulse:
            self.calibrate()

    def __call__(self, angle):
        # print(self.channel, type(self.channel))
        super().__call__(angle)
        if 0 <= angle <= 180:
            set_servo_to(self.channel, angle, "standard_servo")
        else:
            pass


class angle_memory_servo(standard_servo):
    angle = 0

    def __call__(self, rotation_rate):
        angle_change = rotation_rate * socket_timeout * time_base
        if 0 <= self.angle + angle_change <= 180:
            self.angle += angle_change
            super()(self.angle)


def update(speeds):
    if 0 in MODE:
        print("\n")
    if speeds is not None:
        for speed in speeds:
            if speed in electronics_map:
                try:
                    electronics_map[speed](float(speeds[speed]))
                except Exception as e:
                    print("bill nye meme", e, speed)


def debug_print(statement):
    str_num = str(statement)[:4]
    print(str_num, " ",  end='')


def debug_null(cmd):
    pass


# MAIN ==============================================================
# wheel declartions (calibration needed)
wheel1 = continous_servo(0)
wheel2 = continous_servo(1)
wheel3 = continous_servo(2)
wheel4 = continous_servo(3)
wheel5 = continous_servo(4)
wheel6 = continous_servo(5)
# gimbal declarations (calibration needed)
gimbal1 = standard_servo(6, 500, 2400)
gimbal2 = standard_servo(7, 550, 2275)
gimbal3 = standard_servo(8, 600, 2350)
gimbal4 = standard_servo(9, 700, 2525)
# arm declartions (calibration needed)
shoulder = standard_servo(10, 1000, 2550)
elbow = standard_servo(11, 400, 2100)
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
update(null_map)
command_server = network_module.make_server(5000, '0.0.0.0')
command_server.get_connection()
while 1:
    string_messages = command_server.get_messages()
    cmd_dict = command_formats.get_valid_cmds(string_messages)
    update(cmd_dict)
