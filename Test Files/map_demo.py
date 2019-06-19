def whl_drv(chnl, spd):
    kit.continuous_servo[whl].throttle = spd


def whl_gmbl():
    pass

def arm_angl():
    pass

electronics_speeds = {"w1":0.5675675,
                   "w2":0,
                   }


electronics_map = {"w1":[whl_drv, 0],
                   "w2":0,

                   "g1":[whl_gmbl, 5+1],

                   "a1":[arm_angl, 9+1],
                   }


