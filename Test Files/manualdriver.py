# MODE ========================================================================
import time
MODE = 1
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
# Driver
# from .modules import network_module as network_module
# from .modules import command_formats as command_formats
# MODE ========================================================================
MODE = [0]
try:
    import pigpio
    pwm_control = pigpio.pi()
    MODE = [2]
    print("connected to pigpio")
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    MODE = [2]

except (NotImplementedError, ImportError):
    print("unable to connect to pigpio")

try:
    from adafruit_servokit import ServoKit
    kit = ServoKit(channels=16)
    MODE = [1]
except (NotImplementedError, ImportError):
    print("unable to access PWM control board")


class servo:
    def __init__(self, channel, min_pulse=0, max_pulse=0):
        self.channel = int(channel)
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse

    def __call__(self, val):
        pass

    def calibrate(self):
        pass

    def set_pulse_lims(self, min_pulse, max_pulse):
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.calibrate()


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


class pwm_servo(servo):
    def __init__(self, GPIO_pin, min_pulse=500, max_pulse=2500):
        # super(standard_servo, self).__init__(channel, min_pulse, max_pulse)
        super().__init__(GPIO_pin, min_pulse, max_pulse)
        GPIO.setup(GPIO_pin, GPIO.OUT)
        pwm_control.set_mode(GPIO_pin, pigpio.OUTPUT)
##        self.p = GPIO.PWM(GPIO_pin, 50)
##        self.p.start(2.5)

    def __call__(self, angle, max_angle=180):
        fraction_angle = angle/max_angle
        angle_pulse = (self.max_pulse - self.min_pulse) * \
            fraction_angle + self.min_pulse
        if 0 <= fraction_angle <= 1:
            pwm_control.set_servo_pulsewidth(self.channel, angle_pulse)
##            self.p.ChangeDutyCycle(angle/10 + 2.5)
        else:
            pass


class pwm_servo_wheel(pwm_servo):

    def __call__(self, angle, max_angle=180):
        angle = angle*90 + 90
        super().__call__(angle, max_angle)


def get_map_from_mode(mode):
    if 0 in mode:
        return print_map
    elif 1 in mode:
        return electronics_map
    elif 2 in mode:
        return pwm_map


def apply_map(map_dict):
    for code, set_servo in electronics_map.items():
        if code in map_dict:
            set_servo(map_dict[code])


def test_calibration():
    print("setting all to min")
    apply_map(min_map)
    input("press enter to continue")
    print("setting all to max")
    apply_map(max_map)


def calibrate_servo(servo_to_test, max_pulse=2000, min_pulse=1000):
    neutral = 1500
    delta = 100
    servo_to_test.set_pulse_lims(min_pulse, max_pulse)
    print("---setting minimum pulse width---")
    while 1:
        servo_to_test(0)
        done = input(
            "Pulse is {}. At minimum?\ny to quit\nr to reset\nnumber for delta\n".format(min_pulse))
        if done == "y":
            break
        elif done == "r":
            for i in range(0, 181):
                servo_to_test(i)
                time.sleep(0.01)
            for i in range(0, 181):
                servo_to_test(180-i)
                time.sleep(0.01)
        elif done.isnumeric():
            pulse = int(done)
        min_pulse = pulse
        servo_to_test.set_pulse_lims(min_pulse, max_pulse)
    print("---setting maximum pulse width---")
    delta = 100
    while 1:
        servo_to_test(180)
        done = input(
            "Pulse is {}. At max?\ny to quit\nr to reset\nnumber for delta\n".format(max_pulse))
        if done == "y":
            break
        elif done == "r":
            for i in range(0, 181):
                servo_to_test(180-i)
                time.sleep(0.01)
            for i in range(0, 181):
                servo_to_test(i)
                time.sleep(0.01)
        elif done.isnumeric():
            pulse = int(done)
            max_pulse = pulse
            servo_to_test.set_pulse_lims(min_pulse, max_pulse)
    print("calibration done, final pulse widths were {} and {} microseconds".format(
        min_pulse, max_pulse))


def debug_print(statement):
    str_num = str(statement)[:4]
    print(str_num, " ",  end='')


def debug_null(cmd):
    pass


# kit = ServoKit(channels=16)
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

# pwm declarations (only used as backup)
#pwm_wheel1 = pwm_servo(0)
#pwm_wheel2 = pwm_servo(1)
pwm_wheel3 = pwm_servo_wheel(2)
pwm_wheel4 = pwm_servo_wheel(3)
pwm_wheel5 = pwm_servo_wheel(4)
pwm_wheel6 = pwm_servo_wheel(5)
pwm_gimbal1 = pwm_servo(6)
pwm_gimbal2 = pwm_servo(7)
pwm_gimbal3 = pwm_servo(8)
pwm_gimbal4 = pwm_servo(9)
pwm_shoulder = pwm_servo(10)
pwm_elbow = pwm_servo(11)
pwm_grabber = pwm_servo(12)

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

pwm_map = {"w1": debug_null,
           "w2": debug_null,
           "w3": pwm_wheel3,
           "w4": pwm_wheel4,
           "w5": pwm_wheel5,
           "w6": pwm_wheel6,
           "g1": pwm_gimbal1,
           "g2": pwm_gimbal2,
           "g3": pwm_gimbal3,
           "g4": pwm_gimbal4,
           "a1": pwm_shoulder,
           "a2": pwm_elbow,
           "a3": pwm_grabber,
           "a4": debug_null,
           "p4": debug_null,
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


min_map = {"g1": 0,
           "g2": 0,
           "g3": 0,
           "g4": 0,
           "a1": 0,
           "a2": 0,
           "a3": 0,
           }

max_map = {"g1": 180,
           "g2": 180,
           "g3": 180,
           "g4": 180,
           "a1": 180,
           "a2": 180,
           "a3": 180,
           }

print("===Servo calibration tool & manual driver===")
