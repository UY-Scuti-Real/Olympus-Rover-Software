# for testing the network module
import time
import math
import network_module
import message_format_module


def get_position(x):
    x += (math.pi*2)/resolution
    return x


sock = network_module.make_client()
sock.connect_to(5001, 'localhost')
x = 0
period = 1/1
resolution = 36
cmd_dict = {}
while 1:
    x = get_position(x)
    sinx = math.sin(x)
    cmd_dict["sx"] = sinx
    message = message_format_module.get_strcmds_from_dict(cmd_dict)
    sock.send_message(message)
    time.sleep(period/resolution)
