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

#      A
#      ---
#   F | G | B
#      ---
#   E |   | C
#      ---
#       D
# A=0x80, B=0x40, C=0x20, D=0x10, E=0x02, F=0x08, G=0x04
# Bits are valid for Speed display only, all other share bits in 2 databyte per lcd 7-segment display.
# Use function data_from_string_swapped to recalculate values
representations = {
    '0' : 0xfa,
    '1' : 0x60,
    '2' : 0xd6,
    '3' : 0xf4,
    '4' : 0x6c,
    '5' : 0xbc,
    '6' : 0xbe,
    '7' : 0xe0,
    '8' : 0xfe,
    '9' : 0xfc,
    'A' : 0xee,
    'B' : 0xfe,
    'C' : 0x9a,
    'D' : 0x76,
    'E' : 0x9e,
    'F' : 0x8e,
    'G' : 0xbe,
    'H' : 0x6e,
    'I' : 0x60,
    'J' : 0x70,
    'K' : 0x0e,
    'L' : 0x1a,
    'M' : 0xa6,
    'N' : 0x26,
    'O' : 0xfa,
    'P' : 0xce,
    'Q' : 0xec,
    'R' : 0x06,
    'S' : 0xbc,
    'T' : 0x1e,
    'U' : 0x7a,
    'V' : 0x32,
    'W' : 0x58,
    'X' : 0x6e,
    'Y' : 0x7c,
    'Z' : 0xd6,
    '-' : 0x04,

}


def swap_nibbles(x):
    return ( (x & 0x0F)<<4 | (x & 0xF0)>>4 )


def winwing_fcu_set_led(ep, led, brightness):
    data = [0x02, 0x10, 0xbb, 0, 0, 3, 0x49, led.value, brightness, 0,0,0,0,0]
    cmd = bytes(data)
    ep.write(cmd)


def lcd_init(ep):
    data = [0xf0, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0] # init packet
    cmd = bytes(data)
    ep.write(cmd)


def data_from_string(num_7segments, string):

    l = num_7segments
    d = [0] * (l)
    for i in range(min(l, len(string))):
        d[l-1-i] = representations[string.upper()[i]]
    return d


def data_from_string_swapped(num_7segments, string): # some 7-segemnts have wired mapping, correct ist here
    # return array with one byte more than lcd chars

    l = num_7segments

    d = data_from_string(l, string)
    d.append(0)

    # fix wired segemnt mapping
    for i in range(len(d)):
        d[i] = swap_nibbles(d[i])
    for i in range(0, len(d) - 1):
        d[l-i] = (d[l-i] & 0x0f) | (d[l-1-i] & 0xf0)
        d[l-1-i] = d[l-1-i] & 0x0f

    return d


def lcd_set(ep, speed, heading, alt,vs, new):
    speed_mode_speed_flag = 0x08 # h[3]
    speed_mode_mach_flag = 0x04 # h[3]
    lateral_mode_heading_flag = 0x80 # h[0]
    lateral_mode_lateral_flag = 0x20 # h[0]

    h2_dp = 0x10
    hdg2_flag = 0x08 # a[5]
    v_s_flag = 0x04 # a[5]
    trk_flag = 0x02 # a[5]
    fpa_flag = 0x01 # a[5]
    alt_flag = 0x10 # a[4]

    spd_managed_flag = 0x02 # h[3]
    hdg_managed_flag = 0x10 # h[0]
    alt_managed_flag = 0x10 # v[2]

    vs_minus_horiz = 0x10 # a[0]
    vs_minus_vert = 0x10 # v[3]

    s = data_from_string( 3, str(speed))
    h = data_from_string_swapped(3, str(heading))
    a = data_from_string_swapped(5, str(alt))
    v = data_from_string_swapped(4, str(vs)) # v[1] includes V/s and FPA instead of 4th segment
    pkg_nr = 1
    data = [0xf0, 0x0, pkg_nr, 0x31, 0x10, 0xbb, 0x0, 0x0, 0x2, 0x1, 0x0, 0x0, 0xff, 0xff, 0x2, 0x0, 0x0, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, s[2], s[1], s[0], h[3], h[2], h[1], h[0], a[5], a[4], a[3], a[2], a[1], a[0], v[4], v[3], v[2], v[1], v[0], 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
    cmd = bytes(data)
    ep.write(cmd)

    data = [0xf0, 0x0, pkg_nr, 0x11, 0x10, 0xbb, 0x0, 0x0, 0x3, 0x1, 0x0, 0x0, 0xff, 0xff, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
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
speed = 100
heading = 888
alt = 16000
vs = 8888

while True:
    buf_in = [None] * 7
    num_bytes = endpoint_in.read(0x81, 7)
    print(num_bytes)
    winwing_fcu_set_led(endpoint_out, Leds.AP1_GREEN, 1)
    winwing_fcu_set_led(endpoint_out, Leds.AP2_GREEN, 0)
    lcd_set(endpoint_out, speed, heading, alt, vs, 0x0) # bf
    speed = speed + 1
    #heading = heading + 3
    time.sleep(0.5)
    winwing_fcu_set_led(endpoint_out, Leds.AP1_GREEN, 0)
    winwing_fcu_set_led(endpoint_out, Leds.AP2_GREEN, 1)
    lcd_set(endpoint_out, speed, heading, alt, vs, 0xff)
    time.sleep(0.5)
