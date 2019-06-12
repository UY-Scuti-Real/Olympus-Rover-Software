import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
##print(kit.__dict__)
##print("START")
##kit.continuous_servo[0].throttle = 1
##print("FORWARD")
###kit.continuous_servo[1].throttle = 1
##time.sleep(2)
##print("HALF ANGL")
##kit.continuous_servo[0].throttle = 0
##print("HALF FWD")
###kit.continuous_servo[1].throttle = 0.1
##time.sleep(2)
##
###print("BACKWARD")
###kit.continuous_servo[1].throttle = -1
##time.sleep(1)
##print("STOP")
##kit.continuous_servo[0].throttle = -1
##
###kit.continuous_servo[1].throttle = 0
while 1:
    low  = float(input("set low width: "))
    high = float(input("set high width: "))
    kit.servo[0].set_pulse_width_range(low, high)
    kit.servo[0].angle =  0
    input("continue?")
    kit.servo[0].angle =  180
    
##    print(kit.__dict__)
