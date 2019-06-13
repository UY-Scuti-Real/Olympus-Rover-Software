from inputs import get_gamepad
import network_module


class state:
    def __init__(self):
        self.values = {'ABS_Y': 0, 'ABS_X': 0, 'ABS_Z': 0, 'BTN_THUMBL': 0,  # left stick
                       'BTN_TL': 0, 'BTN_TR': 0,  # bumpers
                       'ABS_HAT0X': 0, 'ABS_HAT0Y': 0,  # dpad
                       'BTN_START': 0, 'BTN_SELECT': 0,  # selectors
                       'ABS_RY': 0, 'ABS_RX': 0, 'ABS_RZ': 0, 'BTN_THUMBR': 0,  # right stick
                       'BTN_WEST': 0, 'BTN_SOUTH': 0, 'BTN_EAST': 0, 'BTN_NORTH': 0  # buttons
                       }
        self.norms = {'ABS_Y': 2**15, 'ABS_X': 2**15, 'ABS_Z': 2*8, 'BTN_THUMBL': 1,  # left stick
                      'BTN_TL': 1, 'BTN_TR': 1,  # bumpers
                      'ABS_HAT0X': 1, 'ABS_HAT0Y': 1,  # dpad
                      'BTN_START': 1, 'BTN_SELECT': 1,  # selectors
                      'ABS_RY': 2**15, 'ABS_RX': 2**15, 'ABS_RZ': 2**8, 'BTN_THUMBR': 1,  # right stick
                      'BTN_WEST': 1, 'BTN_SOUTH': 1, 'BTN_EAST': 1, 'BTN_NORTH': 1  # buttons
                      }
        self.deadzone = {'ABS_Y': 0.2, 'ABS_X': 0.2, 'ABS_Z': 0, 'BTN_THUMBL': 0,  # left stick
                         'BTN_TL': 0, 'BTN_TR': 0,  # bumpers
                         'ABS_HAT0X': 0, 'ABS_HAT0Y': 0,  # dpad
                         'BTN_START': 1, 'BTN_SELECT': 1,  # selectors
                         'ABS_RY': 0.1, 'ABS_RX': 0.1, 'ABS_RZ': 0, 'BTN_THUMBR': 0,  # right stick
                         'BTN_WEST': 0, 'BTN_SOUTH': 0, 'BTN_EAST': 0, 'BTN_NORTH': 0  # buttons
                         }


def get_changes(events, cont):
    send_dict = {}
    for event in events:
        if event.code == "SYN_REPORT":
            continue
        normalised_value = event.state/cont.norms[event.code]
        if abs(normalised_value - cont.values[event.code]) > 1/64:
            cont.values[event.code] = normalised_value
            if abs(normalised_value) > cont.deadzone[event.code]:
                send_dict[event.code] = normalised_value
            else:
                send_dict[event.code] = 0
    return send_dict


def prep_msg(gamepad_dict):
    strmsg = ""
    for key in gamepad_dict:
        command = command_map[key]
        strmsg += str(command) + ":" + str(gamepad_dict[key]) + ","
    return strmsg


command_map = {'ABS_Y': 'DRV_FWD',
               'ABS_X': 'DRV_TURN',
               'ABS_Z': 'U',
               'BTN_THUMBL': 'U',  # left stick
               'BTN_TL': 'TOGL_SEN',
               'BTN_TR': 'TOGL_ARM',  # bumpers
               'ABS_HAT0X': 'U',
               'ABS_HAT0Y': 'TOGL_MSC',  # dpad
               'BTN_START': 'U',
               'BTN_SELECT': 'U',  # selectors
               'ABS_RY': 'ARM_VERT',
               'ABS_RX': 'ARM_HORI',
               'ABS_RZ': 'U',
               'BTN_THUMBR': 'U',  # right stick
               'BTN_WEST': 'TOGL_GRB',
               'BTN_SOUTH': 'YEET',
               'BTN_EAST': 'TOGL_DMP',
               'BTN_NORTH': 'TOGL_DRV'  # buttons
               }

cont = state()
net = network_module.make_client()
net.connect_to(("localhost", 5001))
while 1:
    events = get_gamepad()
    gamepad_dict = get_changes(events, cont)
    if len(gamepad_dict) > 0:
        msg = prep_msg(gamepad_dict)
        net.send_message(msg)
