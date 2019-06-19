# for testing the network module
import time
import math


def get_position(x):
    x += (math.pi*2)/resolution
    return x


def print_wave(value):
    print(" "*int(value*10+10), "*")


x = 0
period = 1/1
resolution = 36
while 1:
    x = get_position(x)
    sinx = math.sin(x)
    print_wave(sinx)
    time.sleep(period/resolution)
