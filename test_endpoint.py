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

class Lcd(Enum):
    ALL_ON = 2
    ALL_OFF = 6
    HALF_LCD_ON1 = 7
    HALF_LCD_ON2 = 9


def winwing_fcu_set_led(ep, led, brightness):
    data = [0x02, 0x10, 0xbb, 0, 0, 3, 0x49, led.value, brightness, 0,0,0,0,0]
    cmd = bytes(data)
    ep.write(cmd)


def lcd_init(ep):
    data = [0xf0, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0] # init packet
    cmd = bytes(data)
    ep.write(cmd)


def lcd_set(ep, cmd):
    pkg_nr = 1
    data = [0xf0, 0x0, pkg_nr, 0x12, 0x10, 0xbb, 0x0, 0x0, 0x4, 0x1, 0x0, 0x0, 0xff, 0xff, 0x0, 0x0, 0x0, 0x1, 0x0, 0x0, 0x0, cmd.value, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0] # first packet, checksum (byte 13-14) set to 0xff, does not make any problems
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

lcd_init(endpoint_out)

endpoint_in = endpoints[0]
print(endpoint_in)
while True:
    buf_in = [None] * 7
    num_bytes = endpoint_in.read(0x81, 7)
    print(num_bytes)
    winwing_fcu_set_led(endpoint_out, Leds.AP1_GREEN, 1)
    winwing_fcu_set_led(endpoint_out, Leds.AP2_GREEN, 0)
    lcd_set(endpoint_out, Lcd.ALL_ON)
    time.sleep(0.5)
    winwing_fcu_set_led(endpoint_out, Leds.AP1_GREEN, 0)
    winwing_fcu_set_led(endpoint_out, Leds.AP2_GREEN, 1)
    lcd_set(endpoint_out, Lcd.ALL_OFF)
    time.sleep(0.5)
