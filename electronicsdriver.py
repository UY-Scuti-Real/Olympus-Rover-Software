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
kit = ServoKit(channels=16)

def servo_angle(spd):
    try:
        angle = float(spd)*80 + 90
        kit.servo[0].angle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("But that's wrong, you fucking retard: ", e, spd)


def debug_cmd(msg):
    pass


def wheel1(spd):
    try:
        angle = -float(spd)
        kit.continuous_servo[0].throttle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("wheel1: ", e, spd)

def wheel2(spd):
    try:
        angle = float(spd)
        kit.continuous_servo[1].throttle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("wheel2: ", e, spd)


def wheel3(spd):
    try:
        angle = -float(spd)
        kit.continuous_servo[2].throttle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("wheel3: ", e, spd)


def wheel4(spd):
    try:
        angle = float(spd)
        kit.continuous_servo[3].throttle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("wheel4: ", e, spd)


def wheel5(spd):
    try:
        angle = -float(spd)
        kit.continuous_servo[4].throttle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("wheel5: ", e, spd)


def wheel6(spd):
    try:
        angle = float(spd)
        kit.continuous_servo[5].throttle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("wheel6: ", e, spd)


def gimbal1(spd):
    try:
        angle = float(spd)*90+90
        kit.servo[6].angle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("gimbal1: ", e, spd)


def gimbal2(spd):
    try:
        angle = float(spd)*90+90
        kit.servo[7].angle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("gimbal2: ", e, spd)


def gimbal3(spd):
    try:
        angle = float(spd)*90+90
        kit.servo[8].angle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("gimbal3: ", e, spd)


def gimbal4(spd):
    try:
        angle = float(spd)*90+90
        kit.servo[9].angle = angle
        #print("angle should be ", angle)
    except Exception as e:
        print("gimbal4: ", e, spd)


def shoulder(spd):
    try:
        kit.servo[10].angle = float(spd)
        #print("shoulder", spd, end = '')
    except Exception as e:
        print("But that's wrong, you fucking shoulder: ", e, spd)

def elbow(spd):
    try:
        kit.servo[11].angle = float(spd)
        #print("\t elbow", spd, "\n", end = '\n')
    except Exception as e:
        print("But that's wrong, you fucking elbow: ", e, spd)


def grabber(spd):
    try:
        kit.servo[12].angle = float(spd)
    except Exception as e:
        print("But that's wrong, you fucking grabber: ", e, spd)


class driver:
    def __init__(self, mode):
        self.command_sock = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.command_sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
        self.command_sock.setsockopt(s.SOL_SOCKET, s.SO_REUSEPORT, 1)
        self.command_sock.bind(("192.168.1.10", 5000))
        self.command_sock.listen(2048)
        if mode == 0:
            self.map = {"w1":print,
                        "w2":print,
                        "w3":print,
                        "w4":print,
                        "w5":print,
                        "w6":print,
                        "g1":print,
                        "g2":print,
                        "g3":print,
                        "g4":print,
                        "g5":print,
                        "g6":print,
                        "a1":print,
                        "a2":print,
                        "a3":print,
                        }
        if mode == 1:
            self.map = {"w1":wheel1,
                        "w2":wheel2,
                        "w3":wheel3,
                        "w4":wheel4,
                        "w5":wheel5,
                        "w6":wheel6,
                        "g1":gimbal1,
                        "g2":gimbal2,
                        "g3":gimbal3,
                        "g4":gimbal4,
                        "g5":debug_cmd,
                        "g6":debug_cmd,
                        "a1":shoulder,
                        "a2":elbow,
                        "a3":grabber,
                        }
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
##        try:
        aryform = str(msg).split(",")
        dictform = {}
        for ary in aryform:
            if len(ary) == 0 or ":" not in ary:
                continue
            key, value = ary.split(":")
            dictform[key] = value
        return dictform
##        except ValueError as e:
            #print("oppsie:", e , "\n", aryform)
##            pass

    def update(self, speeds):
        #this feels very wrong
        if speeds is not None:
            for speed in speeds:
                if speed in self.map:
                    self.map[speed](speeds[speed])
##            if "a1" in speeds:
##                print("a1 ",speeds["a1"])
##            if "a2" in speeds:
##                print("a2", speeds["a2"])
            #print(speeds)

print("Starting driver")
drive = driver(MODE)
