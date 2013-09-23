#!/usr/bin/env python

__author__ = 'Yasir'

import multiprocessing as mp

import nxt.locator

from nxt.sensor import *
from nxt.motor import *
from simpleOSC import initOSCClient, initOSCServer, setOSCHandler, \
    startOSCServer, sendOSCMsg, closeOSC


class Motor_Control(object):
    nxt_obj = 0
    m_left = []
    m_right = []

    def __init__(self, bot):
        self.nxt_obj = bot
        self.m_left = Motor(self.nxt_obj, PORT_B)
        self.m_right = Motor(self.nxt_obj, PORT_C)

    def motor_osc_handler(self, addr, tags, data, source):
        self.motor_command(data)

    def motor_command(self, d):
        self.m_left.run(d[0] if not d[1] else d[1], regulated=True)
        self.m_right.run(d[0], regulated=True)


# OSC server function, forwards all required values to PureData OSC client
def sensor_broadcast(Control_Object):
    ultrasonic = Ultrasonic(Control_Object.nxt_obj, PORT_4)

    while 1:
        distance = ultrasonic.get_distance()
        sendOSCMsg('/motor_state', [Control_Object.m_right._get_state().power,
                                    Control_Object.m_left._get_state().power])
        # print distance
        sendOSCMsg('/ultrasound', [distance])
        time.sleep(0.10)  # 10 ms


def shutdown(pl):
    input("Press any key to close OSC server")
    closeOSC()
    pl.terminate()

if __name__ == '__main__':
    b = nxt.locator.find_one_brick()
    controls = Motor_Control(b)

    # takes args : ip, port
    initOSCClient()

    # takes args : ip, port, mode --> 0 for basic server, 1 for threading server, 2 for forking server
    initOSCServer(ip='127.0.0.1', port=20000, mode=1)

    # bind addresses to functions
    setOSCHandler('/motors', controls.motor_osc_handler)

    # and now set it into action
    startOSCServer()

    # starting the sensor broadcast in parallel
    pool = mp.Pool()
    #pool.apply_async(shutdown(pool))
    pool.apply_async(sensor_broadcast(controls))
    pool.close()
    pool.join()
    # server = sensor_broadcast(controls)
    # procOSC = mp.Process(server)
    # procOSC.start()

    # input("Press any key to close OSC server")
    # closeOSC()