from inputs import get_gamepad
import socket as s
##
##cont_sock = s.socket(s.AF_INET, s.SOCK_STREAM)
##cont_sock.connect(("localhost", 5001))
class state:
    def __init__(self):
        self.values = {'ABS_Y': 0, 'ABS_X':0, 'ABS_Z': 0, 'BTN_THUMBL': 0, #left stick
                      'BTN_TL': 0, 'BTN_TR': 0, #bumpers
                      'ABS_HAT0X': 0, 'ABS_HAT0Y': 0, #dpad
                      'BTN_START': 0, 'BTN_SELECT': 0,#selectors
                      'ABS_RY': 0, 'ABS_RX': 0, 'ABS_RZ': 0, 'BTN_THUMBR': 0, #right stick
                      'BTN_WEST': 0, 'BTN_SOUTH': 0, 'BTN_EAST': 0, 'BTN_NORTH': 0 #buttons
                       }
        self.norms = {'ABS_Y': 2**15, 'ABS_X':2**15, 'ABS_Z': 2*8, 'BTN_THUMBL': 1, #left stick
                      'BTN_TL': 1, 'BTN_TR': 1, #bumpers
                      'ABS_HAT0X': 1, 'ABS_HAT0Y': 1, #dpad
                      'BTN_START': 1, 'BTN_SELECT': 1,#selectors
                      'ABS_RY': 2**15, 'ABS_RX': 2**15, 'ABS_RZ': 2**8, 'BTN_THUMBR': 1, #right stick
                      'BTN_WEST': 1, 'BTN_SOUTH': 1, 'BTN_EAST': 1, 'BTN_NORTH':1 #buttons
                       }
        self.deadzone = {'ABS_Y': 0.1, 'ABS_X':0.1, 'ABS_Z': 0, 'BTN_THUMBL': 0, #left stick
                      'BTN_TL': 0, 'BTN_TR': 0, #bumpers
                      'ABS_HAT0X': 0, 'ABS_HAT0Y': 0, #dpad
                      'BTN_START': 1, 'BTN_SELECT': 1,#selectors
                      'ABS_RY': 0.1, 'ABS_RX': 0.1, 'ABS_RZ': 0, 'BTN_THUMBR': 0, #right stick
                      'BTN_WEST': 0, 'BTN_SOUTH': 0, 'BTN_EAST': 0, 'BTN_NORTH':0 #buttons
                       }
        
        
class network:
    def __init__(self):
        self.sock = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.conn_stat = False
        pass

    def aquire_conn(self, addrport):
        self.sock.connect(addrport)
        self.conn_stat = True

    def send(self, msg):
        if self.conn_stat:
            self.sock.send(msg.encode())



def get_changes(events, cont):
    send_dict = {}
    for event in events:
        if event.code == "SYN_REPORT":
            continue
        normalised_value = event.state/cont.norms[event.code]
        #print(normalised_value)
        if abs(normalised_value  - cont.values[event.code])> 1/64:
            cont.values[event.code] = normalised_value
            if abs(normalised_value) > cont.deadzone[event.code]:
                send_dict[event.code] = normalised_value
            else:
                send_dict[event.code] = 0
    return send_dict

def prep_msg(dictmsg):
    strmsg = ""
    for key in dictmsg:
        strmsg += str(key) + ":" + str(dictmsg[key]) + ","
    return strmsg
        

cont = state()
net = network()
net.aquire_conn(("localhost", 5001))
while 1:
    events = get_gamepad()
    send_dict = get_changes(events, cont)
    if len(send_dict)>0:       
        msg = prep_msg(send_dict)
##        print(msg)
        net.send(msg)
