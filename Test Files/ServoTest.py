import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=8)
print("START")
kit.servo[0].angle = 180
print("FORWARD")
kit.continuous_servo[1].throttle = 1
time.sleep(1)
print("BACKWARD")
kit.continuous_servo[1].throttle = -1
time.sleep(1)
kit.servo[0].angle = 0
print("STOP")
kit.continuous_servo[1].throttle = 0
