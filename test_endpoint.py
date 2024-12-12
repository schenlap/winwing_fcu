#!/bin/env python3

from dataclasses import dataclass
import time
import usb.core
import usb.backend.libusb1
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
    '#' : 0x36,
    '/' : 0x60,
    '\\' : 0xa0,
    ' ' : 0x00,
}

class Byte(Enum):
    H0 = 0
    H3 = 1
    A0 = 2
    A1 = 3
    A2 = 4
    A3 = 5
    A4 = 6
    A5 = 7
    V2 = 8
    V3 = 9
    V0 = 10
    V1 = 11



@dataclass
class Flag:
    name : str
    byte : Byte
    mask : int
    value : bool = False


flags = dict([("spd", Flag('spd-mach_spd', Byte.H3, 0x08, True)),
              ("mach", Flag('spd-mach_mach', Byte.H3, 0x04)),
              ("hdg", Flag('hdg-trk-lat_hdg', Byte.H0, 0x80)),
              ("trk", Flag('hdg-trk-lat_trk', Byte.H0, 0x40)),
              ("lat", Flag('hdg-trk-lat_lat', Byte.H0, 0x20, True)),
              ("vshdg", Flag('hdg-v/s_hdg', Byte.A5, 0x08, True)),
              ("vs", Flag('hdg-v/s_v/s', Byte.A5, 0x04, True)),
              ("ftrk", Flag('trk-fpa_trk', Byte.A5, 0x02)),
              ("ffpa", Flag('trk-fpa_fpa', Byte.A5, 0x01)),
              ("alt", Flag('alt', Byte.A4, 0x10, True)),
              ("hdg_managed", Flag('hdg managed', Byte.H0, 0x10)),
              ("spd_managed", Flag('spd managed', Byte.H3, 0x02)),
              ("alt_managed", Flag('alt_managed', Byte.V1, 0x10)),
              ("vs_horz", Flag('v/s plus horizontal', Byte.A0, 0x10, True)),
              ("vs_vert", Flag('v/s plus vertical', Byte.V2, 0x10)),
              ("lvl", Flag('lvl change', Byte.A2, 0x10, True)),
              ("lvl_left", Flag('lvl change left', Byte.A3, 0x10, True)),
              ("lvl_right", Flag('lvl change right', Byte.A1, 0x10, True)),
              ("fvs", Flag('v/s-fpa_v/s', Byte.V0, 0x40, True)),
              ("ffpa2", Flag('v/s-fpa_fpa', Byte.V0, 0x80)),
              ])


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
        r = representations.get(string.upper()[i])
        if r == None:
            r = 0xef
            print("ERROR: char '{string.upper()[i]}' not found")
        d[l-1-i] = r
    return d


def data_from_string_swapped(num_7segments, string): # some 7-segemnts have wired mapping, correct ist here
    # return array with one byte more than lcd chars

    l = num_7segments

    d = data_from_string(l, string)
    d.append(0)

    # fix wired segment mapping
    for i in range(len(d)):
        d[i] = swap_nibbles(d[i])
    for i in range(0, len(d) - 1):
        d[l-i] = (d[l-i] & 0x0f) | (d[l-1-i] & 0xf0)
        d[l-1-i] = d[l-1-i] & 0x0f

    return d


def winwing_fcu_lcd_set(ep, speed, heading, alt,vs, new):
    s = data_from_string( 3, str(speed))
    h = data_from_string_swapped(3, str(heading))
    a = data_from_string_swapped(5, str(alt))
    v = data_from_string_swapped(4, str(vs))

    bl = [0] * len(Byte)
    for f in flags:
        bl[flags[f].byte.value] |= (flags[f].mask * flags[f].value)

    pkg_nr = 1
    data = [0xf0, 0x0, pkg_nr, 0x31, 0x10, 0xbb, 0x0, 0x0, 0x2, 0x1, 0x0, 0x0, 0xff, 0xff, 0x2, 0x0, 0x0, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, s[2], s[1], s[0], h[3] | bl[Byte.H3.value], h[2], h[1], h[0] | bl[Byte.H0.value], a[5] | bl[Byte.A5.value], a[4] | bl[Byte.A4.value], a[3] | bl[Byte.A3.value], a[2] | bl[Byte.A2.value], a[1] | bl[Byte.A1.value], a[0] | v[4] | bl[Byte.A0.value], v[3] | bl[Byte.V3.value], v[2] | bl[Byte.V2.value], v[1] | bl[Byte.V1.value], v[0] | bl[Byte.V0.value], 0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
    cmd = bytes(data)
    ep.write(cmd)

    data = [0xf0, 0x0, pkg_nr, 0x11, 0x10, 0xbb, 0x0, 0x0, 0x3, 0x1, 0x0, 0x0, 0xff, 0xff, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
    cmd = bytes(data)
    ep.write(cmd)

def find_usblib():
    path = ['/opt/homebrew/lib/libusb-1.0.0.dylib',
            '/usr/lib/x86_64-linux-gnu/libusb-1.0.so.0',
            '/usr/lib/libusb-1.0.so.0']
    pathlist = list(enumerate(path))
    for p in range(len(pathlist)):
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: pathlist[p][1])
        if backend:
            print(f"using {pathlist[p][1]}")
            return backend

    print(f"*** No usblib found. Install it with:")
    print(f"***   debian: apt install libusb1")
    print(f"***   mac: brew install libusb")
    print(f"***   If you get this warning and fcu is working, please open an issue at")
    print(f"***   https://github.com/schenlap/winwing_fcu")
    return None

backend = find_usblib()

device = usb.core.find(idVendor=0x4098, idProduct=0xbb10, backend=backend)
if device is None:
    print(f"seachring for FCU ... not found")
    device = usb.core.find(idVendor=0x4098, idProduct=0xbc1e, backend=backend)
    if device is None:
        print(f"seachring for FCU + EFIS-R ... not found")
        raise RuntimeError('No device not found')
    else:
        print(f"seachring for FCU + EFIS-R ... found")
else:
    print(f"seachring for FCU ... found")

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
speed = 250
heading = 180
alt = 16000
vs = '----'


long_str = " A-319schenlap           "
winwing_fcu_set_led(endpoint_out, Leds.BACKLIGHT, 70)
winwing_fcu_set_led(endpoint_out, Leds.SCREEN_BACKLIGHT, 200)

while True:
    buf_in = [None] * 7
    num_bytes = endpoint_in.read(0x81, 7)
    print(num_bytes)
    winwing_fcu_set_led(endpoint_out, Leds.AP1_GREEN, 1)
    winwing_fcu_set_led(endpoint_out, Leds.AP2_GREEN, 0)
    winwing_fcu_lcd_set(endpoint_out, speed, heading, alt, vs, 0x0)
    speed = speed + 1
    #heading = heading + 3
    time.sleep(0.5)
    winwing_fcu_set_led(endpoint_out, Leds.AP1_GREEN, 0)
    winwing_fcu_set_led(endpoint_out, Leds.AP2_GREEN, 1)
    winwing_fcu_lcd_set(endpoint_out, speed, heading, alt, vs, 0xff)
    time.sleep(0.5)
