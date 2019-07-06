#Driver
import socket as s
import select
from adafruit_servokit import ServoKit

#MODE ====================================================================================
MODE = 1
#=========================================================================================
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


class driver:
    def __init__(self, mode):
        self.command_sock = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.command_sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
        self.command_sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEPORT, 1)
        self.command_sock.bind(('192.168.1.11', 5000))
        self.command_sock.listen(2048)
        if mode == 0:
            self.map = print_map
        elif mode == 1:
            self.map = electronics_map
        while 1:
            self.aquire_conn()
            while self.connection:
                msg = self.get_msg()
                if msg and msg != b'1':
                    speeds = self.convert_msg(msg)
                    self.update(speeds)

    def aquire_conn(self):
        self.command_sock.setblocking(1)
        self.connection, addr = self.command_sock.accept()
        print("got connection from {}".format(addr))
        self.command_sock.setblocking(0)

    def get_msg(self):
        try:
            readable, _, errors = select.select(
                        [self.connection],
                        [],
                        [self.connection],
                        5)
            if len(errors) > 0:
                self.connection = False
                return False
            elif len(readable) == 0:
                return b'1'
            for readable_socket in readable:
                msg = readable_socket.recv(2048)
                return msg.decode()
        except ConnectionResetError:
            return False

    def convert_msg(self, msg):
        aryform = str(msg).split(",")
        dictform = {}
        for ary in aryform:
            if len(ary) == 0 or ":" not in ary:
                continue
            key, value = ary.split(":")
            dictform[key] = value
        return dictform

    def update(self, speeds):
        if speeds is not None:
            for speed in speeds:
                if speed in self.map:
                    try:
                        self.map[speed](float(speeds[speed]))
                    except Exception as e:
                        print("bill nye meme", e, speed)


# MAIN ==============================================================
kit = ServoKit(channels=16)
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

print_map = {"w1": print,
             "w2": print,
             "w3": print,
             "w4": print,
             "w5": print,
             "w6": print,
             "g1": print,
             "g2": print,
             "g3": print,
             "g4": print,
             "a1": print,
             "a2": print,
             "a3": print,
             "a4": print,
             "p4": print,
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
drive = driver(MODE)
