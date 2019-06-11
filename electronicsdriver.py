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
    kit.servo[0].angle = float(spd)*80 + 90
    


class driver:
    def __init__(self, mode):
        self.command_sock = s.socket(s.AF_INET, s.SOCK_STREAM)
        #self.command_sock.setsockopt(s.SO_SOCK, s.SO_REUSEADDR, 1)
        #self.command_sock.setsockopt(s.SO_SOCK, s.SO_REUSEPORT, 1)
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
            self.map = {"w1":servo_angle,
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
        print(speeds)
        if speeds is not None:
            for speed in speeds:
                self.map[speed](speeds[speed]) 

print("Starting driver")
drive = driver(MODE)
