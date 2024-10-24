#!/bin/env python3

import time
import usb.core
import usb.util

from enum import Enum

class Leds(Enum):
    BACKLIGHT = 0 # 0 .. 255
    SCREEN_BACKLIGHT = 1 # 0 .. 255
    LOC_GREEN = 3 # all on/off
    AP1_GREEN = 5
    AP2_GREEN = 7
    ATHR_GREEN = 9
    EXPED_GREEN = 11
    APPR_GREEN = 13
    FLAG_GREEN = 17 # 0 .. 255
    EXPED_YELLOW = 30 # 0 .. 255


def winwing_fcu_set_led(ep, led, brightness):
    data = [0x02, 0x10, 0xbb, 0, 0, 3, 0x49, led.value, brightness, 0,0,0,0,0]
    cmd = bytes(data)
    ep.write(cmd)

device = usb.core.find(idVendor=0x4098, idProduct=0xbb10)
if device is None:
    raise RuntimeError('Device not found')
interface = device[0].interfaces()[0]
if device.is_kernel_driver_active(interface.bInterfaceNumber):
    device.detach_kernel_driver(interface.bInterfaceNumber)


endpoints = device[0].interfaces()[0].endpoints()
print(endpoints)
endpoint_out = endpoints[1]
print(endpoint_out)

endpoint_in = endpoints[0]
print(endpoint_in)
while True:
    buf_in = [None] * 7
    num_bytes = endpoint_in.read(0x81, 7)
    print(num_bytes)
    winwing_fcu_set_led(endpoint_out, Leds.AP1_GREEN, 1)
    winwing_fcu_set_led(endpoint_out, Leds.AP2_GREEN, 0)
    time.sleep(0.2)
    winwing_fcu_set_led(endpoint_out, Leds.AP1_GREEN, 0)
    winwing_fcu_set_led(endpoint_out, Leds.AP2_GREEN, 1)
    time.sleep(0.2)
