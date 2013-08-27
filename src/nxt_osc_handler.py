#!/usr/bin/env python


__author__ = 'Yasir'

import multiprocessing as mp

import nxt.locator

from nxt import Touch, Ultrasonic, HTGyro
from nxt.sensor import *
from nxt.motor import *
from simpleOSC import initOSCClient, initOSCServer, setOSCHandler, startOSCServer, sendOSCMsg, closeOSC


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


def sensor_broadcast(brick_obj):
    touch = Touch(brick_obj, PORT_1)
    ultrasonic = Ultrasonic(brick_obj, PORT_4)
    gyro = HTGyro(brick_obj, PORT_2)

    while 1:
        touched = touch.get_sample()
        distance = ultrasonic.get_sample()
        degrees = gyro.get_sample()

        sendOSCMsg('/touch', [0 if not touched else 1])
        sendOSCMsg('/ultrasound', [distance])
        sendOSCMsg('/gyro', [degrees])

        time.sleep(0.150)  # 150 ms


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
    foo = sensor_broadcast(controls.nxt_obj)
    pool.apply_async(foo)
    pool.close()
    pool.join()

    #listening for termination request
    input("Press any key to close OSC server")
    closeOSC()