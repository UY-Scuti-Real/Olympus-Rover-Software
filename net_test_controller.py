# for testing the network module
import time
import math
import network_module


def get_position(x):
    x += (math.pi*2)/resolution
    return x


def construct_message(value):
    message = "sx:{},".format(value)
    return message


sock = network_module.make_client()
sock.connect_to(5001, 'localhost')
x = 0
period = 1/1
resolution = 36
while 1:
    x = get_position(x)
    sinx = math.sin(x)
    message = construct_message(sinx)
    sock.send_message(message)
    time.sleep(period/resolution)
