#!/bin/env python3

# IP Address of machine running X-Plane. 
UDP_IP = "127.0.0.1"
UDP_PORT = 49000

import binascii
from dataclasses import dataclass
from enum import Enum
import evdev
import socket
import struct

#for raw usb
import re
import subprocess

from threading import Thread, Event
from time import sleep

import usb.core
import usb.util

import XPlaneUdp

BUTTONS_CNT = 32


class BUTTON(Enum):
    SWITCH = 0
    TOGGLE = 1
    NONE = 2 # for testing


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


class DREF_TYPE(Enum):
    DATA = 0
    CMD = 1
    NONE = 2 # for testing


class Button:
    def __init__(self, nr, label, dataref = None, dreftype = DREF_TYPE.DATA, button_type = BUTTON.NONE, led = None):
        self.id = nr
        self.label = label
        self.dataref = dataref
        self.dreftype = dreftype
        #self.data = None
        self.type = button_type
        self.led = led

buttonlist = []

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


flags = dict([("spd", Flag('spd-mach_spd', Byte.H3, 0x08)),
              ("mach", Flag('spd-mach_mach', Byte.H3, 0x04)),
              ("hdg", Flag('hdg-trk-lat_hdg', Byte.H0, 0x80)),
              ("trk", Flag('hdg-trk-lat_trk', Byte.H0, 0x40)),
              ("lat", Flag('hdg-trk-lat_lat', Byte.H0, 0x20)),
              ("vshdg", Flag('hdg-v/s_hdg', Byte.A5, 0x08)),
              ("vs", Flag('hdg-v/s_v/s', Byte.A5, 0x04)),
              ("ftrk", Flag('trk-fpa_trk', Byte.A5, 0x02)),
              ("ffpa", Flag('trk-fpa_fpa', Byte.A5, 0x01)),
              ("alt", Flag('alt', Byte.A4, 0x10)),
              ("hdg_managed", Flag('hdg managed', Byte.H0, 0x10)),
              ("spd_managed", Flag('spd managed', Byte.H3, 0x02)),
              ("alt_managed", Flag('alt_managed', Byte.V1, 0x10)),
              ("vs_horz", Flag('v/s plus horizontal', Byte.A0, 0x10)),
              ("vs_vert", Flag('v/s plus vertical', Byte.V2, 0x10)),
              ("lvl", Flag('lvl change', Byte.A2, 0x10)),
              ("lvl_left", Flag('lvl change left', Byte.A3, 0x10)),
              ("lvl_right", Flag('lvl change right', Byte.A1, 0x10)),
              ("fvs", Flag('v/s-fpa_v/s', Byte.V0, 0x40)),
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
        d[l-1-i] = representations[string.upper()[i]]
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

fcu_device = None # usb /dev/inputx device

datacache = {}

# List of datarefs to request. 
datarefs = [
    # ( dataref, unit, description, num decimals to display in formatted output )
    #("sim/flightmodel/position/latitude","°N","The latitude of the aircraft",6),
    #("sim/flightmodel/position/longitude","°E","The longitude of the aircraft",6),
    #("sim/flightmodel/misc/h_ind", "ft", "",0),
    #("sim/flightmodel/position/y_agl","m", "AGL", 0), 
    #("sim/flightmodel/position/mag_psi", "°", "The real magnetic heading of the aircraft",0),
    #("sim/flightmodel/position/indicated_airspeed", "kt", "Air speed indicated - this takes into account air density and wind direction",0), 
    #("sim/flightmodel/position/groundspeed","m/s", "The ground speed of the aircraft",0),
    #("sim/flightmodel/position/vh_ind", "m/s", "vertical velocity",1),
    ("AirbusFBW/HDGdashed","-", "heading dashed", 2),
    ("AirbusFBW/SPDdashed","-", "speed dashed", 2),
    ("AirbusFBW/VSdashed","-", "vs dashed", 2),
    ("sim/cockpit/autopilot/airspeed", "-", "speed value", 2),
    ("sim/cockpit2/autopilot/airspeed_dial_kts_mach", "-", "kts mach dial", 2),
    ("AirbusFBW/SPDmanaged", "-", "spd dot ???", 2),
    ("sim/cockpit/autopilot/airspeed_is_mach", "-", "set speed label", 2),
    ("sim/cockpit/autopilot/heading_mag", "-", "Heading", 2),
    ("AirbusFBW/HDGmanaged", "SET", "Set Hdg managed", 2),
    ("AirbusFBW/HDGTRKmode", "-", "HDG/TRK toggle", 2),
    ("sim/cockpit/autopilot/altitude", "-", "ALT", 2),
    ("AirbusFBW/ALTmanaged", "SET", "Set alt magaged", 2),
    ("sim/cockpit/autopilot/vertical_velocity", "-", "vs speed", 2),
    ("sim/cockpit2/autopilot/fpa", "??", "fpa ???", 2),
    ("AirbusFBW/HDGTRKmode", "-", "V/FPA Mode", 2),
    ("AirbusFBW/AP1Engage", "-", "AP1 Engaged", 2),
    ("AirbusFBW/AP2Engage", "-", "AP2 Engaged", 2)


  ]


buttons_press_event = [0] * BUTTONS_CNT
buttons_release_event = [0] * BUTTONS_CNT

fcu_out_endpoint = None
fcu_in_endpoint = None

xp = None


def create_button_list_fcu():
    buttonlist.append(Button(0, "MACH", "toliss_airbus/ias_mach_button_push", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(1, "LOC", "AirbusFBW/LOCbutton", DREF_TYPE.DATA, BUTTON.TOGGLE, Leds.LOC_GREEN))
    buttonlist.append(Button(2, "TRK", "toliss_airbus/hdgtrk_button_push", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(3, "AP1", "AirbusFBW/AP1Engage", DREF_TYPE.DATA, BUTTON.TOGGLE, Leds.AP1_GREEN))
    buttonlist.append(Button(4, "AP2", "AirbusFBW/AP2Engage", DREF_TYPE.DATA, BUTTON.TOGGLE, Leds.AP2_GREEN))
    buttonlist.append(Button(5, "A/THR", "AirbusFBW/ATHRmode", DREF_TYPE.DATA, BUTTON.TOGGLE, Leds.ATHR_GREEN))
    buttonlist.append(Button(6, "EXPED", "AirbusFBW/EXPEDbutton", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(7, "METRIC", "toliss_airbus/metric_alt_button_push", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(8, "APPR", "AirbusFBW/APPRbutton", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(9, "SPD DEC", "sim/autopilot/airspeed_down", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(10, "SPD INC", "sim/autopilot/airspeed_up", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(11, "SPD PUSH", "AirbusFBW/PushSPDSel", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(12, "SPD PULL", "AirbusFBW/PullSPDSel", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(13, "HDG DEC", "sim/autopilot/heading_down", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(14, "HDG INC", "sim/autopilot/heading_up", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(15, "HDG PUSH", "AirbusFBW/PushHDGSel", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(16, "HDG PULL", "AirbusFBW/PullHDGSel", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(17, "ALT DEC", "sim/autopilot/altitude_down", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(18, "ALT INC", "sim/autopilot/altitude_up", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(19, "ALT PUSH", "AirbusFBW/PushAltitude", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(20, "ALT PULL", "AirbusFBW/PullAltitude", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(21, "VS DEC", "sim/autopilot/vertical_speed_down", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(22, "VS INC", "sim/autopilot/vertical_speed_up", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(23, "VS PUSH", "AirbusFBW/PushVSSel", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(24, "VS PULL", "AirbusFBW/PullVSSel", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(25, "ALT 100", "AirbusFBW/ALT100_1000", DREF_TYPE.DATA, BUTTON.TOGGLE)) # TODO send 0
    buttonlist.append(Button(26, "ALT 1000", "AirbusFBW/ALT100_1000", DREF_TYPE.DATA, BUTTON.TOGGLE)) # todo send 1
    buttonlist.append(Button(27, "FD"))
    buttonlist.append(Button(28, "RES"))


def RequestDataRefs(xp):
    for idx,b in enumerate(buttonlist):
        if b.type == BUTTON.NONE:
            continue
        datacache[b.dataref] = None
        xp.AddDataRef(b.dataref, 3)


def xor_bitmask(a, b, bitmask):
    return (a & bitmask) != (b & bitmask)


def fcu_button_event():
    #print(f'events: press: {buttons_press_event}, release: {buttons_release_event}')
    for b in buttonlist:
        if buttons_press_event[b.id]:
            buttons_press_event[b.id] = 0
            print(f'button {b.label} pressed')
            if b.type == BUTTON.TOGGLE:
                val = datacache[b.dataref]
                if b.dreftype== DREF_TYPE.DATA:
                    print(f'set dataref {b.dataref} from {bool(val)} to {not bool(val)}')
                    xp.WriteDataRef(b.dataref, not bool(val))
                elif b.dreftype== DREF_TYPE.CMD:
                    print(f'send command {b.dataref}')
                    xp.SendCommand(b.dataref)
            elif b.type == BUTTON.SWITCH:
                val = datacache[b.dataref]
                if b.dreftype== DREF_TYPE.DATA:
                    print(f'set dataref {b.dataref} to 1')
                    xp.WriteDataRef(b.dataref, 1)
                elif b.dreftype== DREF_TYPE.CMD:
                    print(f'send command {b.dataref}')
                    xp.SendCommand(b.dataref)
            else:
                print(f'no datafref set for pressed button {b.label}')
        if buttons_release_event[b.id]:
            buttons_release_event[b.id] = 0
            print(f'button {b.label} released')
            if b.type == BUTTON.SWITCH:
                xp.WriteDataRef(b.dataref, 0)


def fcu_create_events(ep_in, ep_out, event):
        buttons_last = 0
        while True:
            sleep(0.02  )
            data_in = ep_in.read(0x81, 7)
            buttons=data_in[1] | (data_in[2] << 8) | (data_in[3] << 16) | (data_in[4] << 24)
            for i in range (32):
                mask = 0x01 << i
                if xor_bitmask(buttons, buttons_last, mask):
                    #print(f"buttons: {format(buttons, "#04x"):^14}")
                    if buttons & mask:
                        buttons_press_event[i] = 1
                    else:
                        buttons_release_event[i] = 1
                    event.set()
                    fcu_button_event()
            buttons_last = buttons


def set_button_led(dataref, v):
    for b in buttonlist:
        if b.dataref == dataref:
            if b.led == None:
                break
            if v >= 1:
                v = 200
            print(f'led: {b.led}, value: {v}')
            winwing_fcu_set_led(fcu_out_endpoint, b.led, int(v))
            break
        else:
            continue


def set_datacache(values):
    global datacache
    for v in values:
        #print(f'cache: v:{v} val:{values[v]}')
        if datacache[v] != values[v]:
            datacache[v] = values[v]
            set_button_led(v, values[v])


def main():
    global xp
    global fcu_in_endpoint, fcu_out_endpoint

    create_button_list_fcu()

    device = usb.core.find(idVendor=0x4098, idProduct=0xbb10)
    if device is None:
        raise RuntimeError('Winwing FCU-A320 not found')
    print('Found winwing FCU-A320')
    interface = device[0].interfaces()[0]
    if device.is_kernel_driver_active(interface.bInterfaceNumber):
        device.detach_kernel_driver(interface.bInterfaceNumber)

    endpoints = device[0].interfaces()[0].endpoints()
    fcu_out_endpoint = endpoints[1]
    fcu_in_endpoint = endpoints[0]

    event=Event()

    usb_event_thread = Thread(target=fcu_create_events, args=[fcu_in_endpoint, fcu_out_endpoint, event])
    usb_event_thread.start()

    print('opening socket')
    xp = XPlaneUdp.XPlaneUdp()
    xp.BeaconData["IP"] = '127.0.0.1' # workaround to set IP and port
    xp.BeaconData["Port"] = 49000
    xp.UDP_PORT = xp.BeaconData["Port"]

    #beacon = xp.FindIp()

    RequestDataRefs(xp)

    while True:
        try:
            values = xp.GetValues()
            #print(values)
            set_datacache(values)
        except XPlaneUdp.XPlaneTimeout:
            print("XPlane Timeout")
            exit(0)

if __name__ == '__main__':
  main() 
