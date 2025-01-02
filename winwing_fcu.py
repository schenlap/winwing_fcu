#!/usr/bin/env python3

# IP Address of machine running X-Plane. 
UDP_IP = "127.0.0.1"
UDP_PORT = 49000

import binascii
from dataclasses import dataclass
from enum import Enum, IntEnum
import os
import socket
import struct

#for raw usb
import re
import subprocess

from threading import Thread, Event, Lock
from time import sleep

import usb.core
import usb.backend.libusb1
import usb.util

import XPlaneUdp

BUTTONS_CNT = 32+32+32 # FCU:32, EFISR:32, EFISL:32

#@unique
class DEVICEMASK(IntEnum):
    NONE = 0
    FCU = 1
    EFISR = 2
    EFISL = 4


class BUTTON(Enum):
    SWITCH = 0
    TOGGLE = 1
    SEND_0 = 2
    SEND_1 = 3
    SEND_2 = 4
    SEND_3 = 5
    SEND_4 = 6
    SEND_5 = 7
    NONE = 5 # for testing


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
    EFISR_BACKLIGHT = 100 # 0 .. 255
    EFISR_SCREEN_BACKLIGHT = 101 # 0 .. 255
    EFISR_FLAG_GREEN = 102 # 0 .. 255
    EFISR_FD_GREEN = 103
    EFISR_LS_GREEN = 104
    EFISR_CSTR_GREEN = 105
    EFISR_WPT_GREEN = 106
    EFISR_VORD_GREEN = 107
    EFISR_NDB_GREEN = 108
    EFISR_ARPT_GREEN = 109
    EFISL_BACKLIGHT = 200 # 0 .. 255
    EFISL_SCREEN_BACKLIGHT = 201 # 0 .. 255
    EFISL_FLAG_GREEN = 202 # 0 .. 255
    EFISL_FD_GREEN = 203
    EFISL_LS_GREEN = 204
    EFISL_CSTR_GREEN = 205
    EFISL_WPT_GREEN = 206
    EFISL_VORD_GREEN = 207
    EFISL_NDB_GREEN = 208
    EFISL_ARPT_GREEN = 209


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

values_processed = Event()
xplane_connected = False
buttonlist = []
values = []

led_brightness = 180
exped_led_state = False

device_config = DEVICEMASK.NONE



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
    S1 = 12
    EFISR_B0 = 13
    EFISR_B2 = 14
    EFISL_B0 = 15
    EFISL_B2 = 16



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
              ("lat", Flag('hdg-trk-lat_lat', Byte.H0, 0x20, True)),
              ("vshdg", Flag('hdg-v/s_hdg', Byte.A5, 0x08)),
              ("vs", Flag('hdg-v/s_v/s', Byte.A5, 0x04)),
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
              ("fvs", Flag('v/s-fpa_v/s', Byte.V0, 0x40)),
              ("ffpa2", Flag('v/s-fpa_fpa', Byte.V0, 0x80)),
              ("fpa_comma", Flag('fpa_comma', Byte.V3, 0x10)),
              ("mach_comma", Flag('mach_comma', Byte.S1, 0x01)),
              ("efisr_qfe", Flag('efisr_qfe', Byte.EFISR_B0, 0x01)), # TODO: don't know when to set this
              ("efisr_qnh", Flag('efisr_qnh', Byte.EFISR_B0, 0x02)),
              ("efisr_hpa_dec", Flag('efisr_hpa_dec', Byte.EFISR_B2, 0x80)),
              ])


def swap_nibbles(x):
    return ( (x & 0x0F)<<4 | (x & 0xF0)>>4 )



def winwing_fcu_set_leds(ep, leds, brightness):
    if isinstance(leds, list):
        for i in range(len(leds)):
            winwing_fcu_set_led(ep, leds[i], brightness)
    else:
        winwing_fcu_set_led(ep, leds, brightness)

def winwing_fcu_set_led(ep, led, brightness):
    if led.value < 100: # FCU
        data = [0x02, 0x10, 0xbb, 0, 0, 3, 0x49, led.value, brightness, 0,0,0,0,0]
    elif led.value < 200 and device_config & DEVICEMASK.EFISR: # EFIS_R
        data = [0x02, 0x0e, 0xbf, 0, 0, 3, 0x49, led.value - 100, brightness, 0,0,0,0,0]
    elif device_config & DEVICEMASK.EFISL: # EFIS_L
        #TODO set leds EFSIL
        print(f"setting leds on EFISL not supported")
        return
    if 'data' in locals():
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


def data_from_string_swapped_efis(num_7segments, string): # next wired mapping :-)

    l = num_7segments

    d = data_from_string(l, string)
    n = [0] * l

    # fix wired segment mapping
    for i in range(len(d)):
        n[i] |= 0x01 if d[i] & 0x08 else 0
        n[i] |= 0x02 if d[i] & 0x04 else 0
        n[i] |= 0x04 if d[i] & 0x02 else 0
        n[i] |= 0x08 if d[i] & 0x10 else 0
        n[i] |= 0x10 if d[i] & 0x80 else 0
        n[i] |= 0x20 if d[i] & 0x40 else 0
        n[i] |= 0x40 if d[i] & 0x20 else 0
        n[i] |= 0x80 if d[i] & 0x01 else 0

    return n

def string_fix_length(v, l):
    s = str(v)
    return s.rjust(l, '0')


def winwing_fcu_set_lcd(ep, speed, heading, alt, vs):
    global usb_retry
    s = data_from_string( 3, string_fix_length(speed, 3))
    h = data_from_string_swapped(3, string_fix_length(heading, 3))
    a = data_from_string_swapped(5, string_fix_length(alt, 5))
    v = data_from_string_swapped(4, string_fix_length(vs, 4))

    bl = [0] * len(Byte)
    for f in flags:
        bl[flags[f].byte.value] |= (flags[f].mask * flags[f].value)

    pkg_nr = 1
    data = [0xf0, 0x0, pkg_nr, 0x31, 0x10, 0xbb, 0x0, 0x0, 0x2, 0x1, 0x0, 0x0, 0xff, 0xff, 0x2, 0x0, 0x0, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, s[2], s[1] | bl[Byte.S1.value], s[0], h[3] | bl[Byte.H3.value], h[2], h[1], h[0] | bl[Byte.H0.value], a[5] | bl[Byte.A5.value], a[4] | bl[Byte.A4.value], a[3] | bl[Byte.A3.value], a[2] | bl[Byte.A2.value], a[1] | bl[Byte.A1.value], a[0] | v[4] | bl[Byte.A0.value], v[3] | bl[Byte.V3.value], v[2] | bl[Byte.V2.value], v[1] | bl[Byte.V1.value], v[0] | bl[Byte.V0.value], 0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
    cmd = bytes(data)
    try:
        ep.write(cmd)
    except Exception as error:
        usb_retry = True
        print(f"error in write data: {error}")

    data = [0xf0, 0x0, pkg_nr, 0x11, 0x10, 0xbb, 0x0, 0x0, 0x3, 0x1, 0x0, 0x0, 0xff, 0xff, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
    cmd = bytes(data)
    try:
        ep.write(cmd)
        usb_retry = False
    except Exception as error:
        usb_retry = True
        print(f"error in commit data: {error}")


def winwing_efisr_set_lcd(ep, baro):
    global usb_retry
    b = data_from_string_swapped_efis( 4, string_fix_length(baro, 4))

    bl = [0] * len(Byte)
    for f in flags:
        bl[flags[f].byte.value] |= (flags[f].mask * flags[f].value)

    pkg_nr = 1

#                                                              alwa  unknown3   chksum    unknown4 nown5  cmd2    ZZZEEEERRROoooo                  seg 1    2     3     4
    data = [0xf0, 0x0, pkg_nr, 0x1a, 0x0e, 0xbf, 0x0, 0x0, 0x2, 0x1, 0x0, 0x0, 0xff, 0xff, 0x1d, 0x0, 0x0, 0x9, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, b[3], b[2] | bl[Byte.EFISR_B2.value], b[1], b[0], bl[Byte.EFISR_B0.value], 0x0e, 0xbf, 0x0, 0x0, 0x3, 0x1, 0x0, 0x0, 0x4c, 0xc, 0x1d, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]

    cmd = bytes(data)
    try:
        ep.write(cmd)
        usb_retry = False
    except Exception as error:
        usb_retry = True
        print(f"error in commit data: {error}")


fcu_device = None # usb /dev/inputx device

datacache = {}

# List of datarefs without led connection to request.
datarefs = [
    ("AirbusFBW/HDGdashed", 2),
    ("AirbusFBW/SPDdashed", 2),
    ("AirbusFBW/VSdashed", 2),
    ("sim/cockpit/autopilot/airspeed", 2),
    ("sim/cockpit2/autopilot/airspeed_dial_kts_mach", 5),
    ("AirbusFBW/SPDmanaged", 2),
    ("sim/cockpit/autopilot/airspeed_is_mach", 2),
    ("sim/cockpit/autopilot/heading_mag", 5),
    ("AirbusFBW/HDGmanaged", 2),
    ("AirbusFBW/HDGTRKmode", 2),
    ("sim/cockpit/autopilot/altitude", 5),
    ("AirbusFBW/ALTmanaged", 2),
    ("sim/cockpit/autopilot/vertical_velocity", 5),
    ("sim/cockpit2/autopilot/fpa", 2),
    ("AirbusFBW/APVerticalMode", 5), # EXPED light on for vsmode >= 112
    ("sim/cockpit2/gauges/actuators/barometer_setting_in_hg_copilot", 2),
    ("AirbusFBW/BaroStdFO", 2),
    ("AirbusFBW/BaroUnitFO", 2)
  ]


buttons_press_event = [0] * BUTTONS_CNT
buttons_release_event = [0] * BUTTONS_CNT

fcu_out_endpoint = None
fcu_in_endpoint = None

usb_retry = False

xp = None


def create_button_list_fcu():
    buttonlist.append(Button(0, "MACH", "toliss_airbus/ias_mach_button_push", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(1, "LOC", "AirbusFBW/LOCbutton", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(2, "TRK", "toliss_airbus/hdgtrk_button_push", DREF_TYPE.CMD, BUTTON.TOGGLE))
    buttonlist.append(Button(3, "AP1", "AirbusFBW/AP1Engage", DREF_TYPE.DATA, BUTTON.TOGGLE, Leds.AP1_GREEN))
    buttonlist.append(Button(4, "AP2", "AirbusFBW/AP2Engage", DREF_TYPE.DATA, BUTTON.TOGGLE, Leds.AP2_GREEN))
    buttonlist.append(Button(5, "A/THR", "AirbusFBW/ATHRbutton", DREF_TYPE.CMD, BUTTON.TOGGLE))
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
    buttonlist.append(Button(25, "ALT 100", "AirbusFBW/ALT100_1000", DREF_TYPE.DATA, BUTTON.SEND_0))
    buttonlist.append(Button(26, "ALT 1000", "AirbusFBW/ALT100_1000", DREF_TYPE.DATA, BUTTON.SEND_1))
    buttonlist.append(Button(27, "BRIGHT", "AirbusFBW/SupplLightLevelRehostats[0]", DREF_TYPE.DATA, BUTTON.NONE, [Leds.BACKLIGHT, Leds.EFISR_BACKLIGHT, Leds.FLAG_GREEN, Leds.EFISR_FLAG_GREEN]))
    buttonlist.append(Button(27, "BRIGHT_LCD", "AirbusFBW/SupplLightLevelRehostats[1]", DREF_TYPE.DATA, BUTTON.NONE, [Leds.SCREEN_BACKLIGHT, Leds.EFISR_SCREEN_BACKLIGHT]))
    #buttonlist.append(Button(27, "BRIGHT", "sim/cockpit2/electrical/instrument_brightness_ratio_manual[14]", DREF_TYPE.DATA, BUTTON.NONE, Leds.BACKLIGHT)) # Laminar A330
    #buttonlist.append(Button(27, "BRIGHT_LCD", "sim/cockpit2/electrical/instrument_brightness_ratio_manual[10]", DREF_TYPE.DATA, BUTTON.NONE, Leds.SCREEN_BACKLIGHT)) # Laminar A330
    buttonlist.append(Button(28, "APPR_LED", "AirbusFBW/APPRilluminated", DREF_TYPE.DATA, BUTTON.NONE, Leds.APPR_GREEN))
    buttonlist.append(Button(29, "ATHR_LED", "AirbusFBW/ATHRmode", DREF_TYPE.DATA, BUTTON.NONE, Leds.ATHR_GREEN))
    buttonlist.append(Button(30, "LOC_LED", "AirbusFBW/LOCilluminated", DREF_TYPE.DATA, BUTTON.NONE, Leds.LOC_GREEN))

    if device_config & DEVICEMASK.EFISR:
        buttonlist.append(Button(32, "R_FD", "toliss_airbus/fd2_push", DREF_TYPE.CMD, BUTTON.TOGGLE, Leds.LOC_GREEN))
        buttonlist.append(Button(33, "R_LS", "toliss_airbus/dispcommands/CoLSButtonPush", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(34, "R_CSTR", "toliss_airbus/dispcommands/CoCstrPushButton", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(35, "R_WPT", "toliss_airbus/dispcommands/CoWptPushButton", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(36, "R_VOR.D", "toliss_airbus/dispcommands/CoVorDPushButton", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(37, "R_NDB", "toliss_airbus/dispcommands/CoNdbPushButton", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(38, "R_ARPT", "toliss_airbus/dispcommands/CoArptPushButton", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(39, "R_STD PUSH", "toliss_airbus/copilot_baro_push", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(40, "R_STD PULL", "toliss_airbus/copilot_baro_pull", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(41, "R_PRESS DEC", "sim/instruments/barometer_copilot_down", DREF_TYPE.CMD, BUTTON.TOGGLE)) # TODO send 3 cmd in hPa mode
        buttonlist.append(Button(42, "R_PRESS INC", "sim/instruments/barometer_copilot_up", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(43, "R_inHg", "AirbusFBW/BaroUnitFO", DREF_TYPE.DATA, BUTTON.SEND_0))
        buttonlist.append(Button(44, "R_hPa", "AirbusFBW/BaroUnitFO", DREF_TYPE.DATA, BUTTON.SEND_1))
        buttonlist.append(Button(45, "R_MODE LS", "AirbusFBW/NDmodeFO", DREF_TYPE.DATA, BUTTON.SEND_0))
        buttonlist.append(Button(46, "R_MODE VOR", "AirbusFBW/NDmodeFO", DREF_TYPE.DATA, BUTTON.SEND_1))
        buttonlist.append(Button(47, "R_MODE NAV", "AirbusFBW/NDmodeFO", DREF_TYPE.DATA, BUTTON.SEND_2))
        buttonlist.append(Button(48, "R_MODE ARC", "AirbusFBW/NDmodeFO", DREF_TYPE.DATA, BUTTON.SEND_3))
        buttonlist.append(Button(49, "R_MODE PLAN", "AirbusFBW/NDmodeFO", DREF_TYPE.DATA, BUTTON.SEND_4))
        buttonlist.append(Button(50, "R_RANGE 10", "AirbusFBW/NDrangeFO", DREF_TYPE.DATA, BUTTON.SEND_0))
        buttonlist.append(Button(51, "R_RANGE 20", "AirbusFBW/NDrangeFO", DREF_TYPE.DATA, BUTTON.SEND_1))
        buttonlist.append(Button(52, "R_RANGE 40", "AirbusFBW/NDrangeFO", DREF_TYPE.DATA, BUTTON.SEND_2))
        buttonlist.append(Button(53, "R_RANGE 80", "AirbusFBW/NDrangeFO", DREF_TYPE.DATA, BUTTON.SEND_3))
        buttonlist.append(Button(54, "R_RANGE 160", "AirbusFBW/NDrangeFO", DREF_TYPE.DATA, BUTTON.SEND_4))
        buttonlist.append(Button(55, "R_RANGE 320", "AirbusFBW/NDrangeFO", DREF_TYPE.DATA, BUTTON.SEND_5))
        buttonlist.append(Button(56, "R_1 VOR", "sim/cockpit2/EFIS/EFIS_1_selection_copilot", DREF_TYPE.DATA, BUTTON.SEND_2))
        buttonlist.append(Button(57, "R_1 OFF", "sim/cockpit2/EFIS/EFIS_1_selection_copilot", DREF_TYPE.DATA, BUTTON.SEND_1))
        buttonlist.append(Button(58, "R_1 ADF", "sim/cockpit2/EFIS/EFIS_1_selection_copilot", DREF_TYPE.DATA, BUTTON.SEND_0))
        buttonlist.append(Button(59, "R_2 VOR", "sim/cockpit2/EFIS/EFIS_2_selection_copilot", DREF_TYPE.DATA, BUTTON.SEND_2))
        buttonlist.append(Button(60, "R_2 OFF", "sim/cockpit2/EFIS/EFIS_2_selection_copilot", DREF_TYPE.DATA, BUTTON.SEND_1))
        buttonlist.append(Button(61, "R_2 ADF", "sim/cockpit2/EFIS/EFIS_2_selection_copilot", DREF_TYPE.DATA, BUTTON.SEND_0))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowARPTFO", DREF_TYPE.DATA, BUTTON.NONE, Leds.EFISR_ARPT_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowNDBFO", DREF_TYPE.DATA, BUTTON.NONE, Leds.EFISR_NDB_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowNDBFO", DREF_TYPE.DATA, BUTTON.NONE, Leds.EFISR_NDB_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowVORDFO", DREF_TYPE.DATA, BUTTON.NONE, Leds.EFISR_VORD_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowWPTFO", DREF_TYPE.DATA, BUTTON.NONE, Leds.EFISR_WPT_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowCSTRFO", DREF_TYPE.DATA, BUTTON.NONE, Leds.EFISR_CSTR_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/FD2Engage", DREF_TYPE.DATA, BUTTON.NONE, Leds.EFISR_FD_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/ILSonFO", DREF_TYPE.DATA, BUTTON.NONE, Leds.EFISR_LS_GREEN))
        buttonlist.append(Button(None, "None", "", DREF_TYPE.NONE, BUTTON.NONE, Leds.LOC_GREEN))
    if device_config & DEVICEMASK.EFISL:
        buttonlist.append(Button(64, "L_FD", "toliss_airbus/fd1_push", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(65, "L_LS", "toliss_airbus/dispcommands/CaptLSButtonPush", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(66, "L_CSTR", "toliss_airbus/dispcommands/CaptCstrPushButton", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(67, "L_WPT", "toliss_airbus/dispcommands/CaptWptPushButton", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(68, "L_VOR.D", "toliss_airbus/dispcommands/CaptVorDPushButton", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(69, "L_NDB", "toliss_airbus/dispcommands/CaptNdbPushButton", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(70, "L_ARPT", "toliss_airbus/dispcommands/CaptArptPushButton", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(71, "L_STD PUSH", "toliss_airbus/capt_baro_push", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(72, "L_STD PULL", "toliss_airbus/capt_baro_pull", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(73, "L_PRESS DEC", "sim/instruments/barometer_down", DREF_TYPE.CMD, BUTTON.TOGGLE)) # TODO send 3 cmd in hPa mode
        buttonlist.append(Button(74, "L_PRESS INC", "sim/instruments/barometer_up", DREF_TYPE.CMD, BUTTON.TOGGLE))
        buttonlist.append(Button(75, "L_inHg", "AirbusFBW/BaroUnitCapt", DREF_TYPE.DATA, BUTTON.SEND_0))
        buttonlist.append(Button(76, "L_hPa", "AirbusFBW/BaroUnitCapt", DREF_TYPE.DATA, BUTTON.SEND_1))
        buttonlist.append(Button(77, "L_MODE LS", "AirbusFBW/NDmodeCapt", DREF_TYPE.DATA, BUTTON.SEND_0))
        buttonlist.append(Button(78, "L_MODE VOR", "AirbusFBW/NDmodeCapt", DREF_TYPE.DATA, BUTTON.SEND_1))
        buttonlist.append(Button(79, "L_MODE NAV", "AirbusFBW/NDmodeCapt", DREF_TYPE.DATA, BUTTON.SEND_2))
        buttonlist.append(Button(80, "L_MODE ARC", "AirbusFBW/NDmodeCapt", DREF_TYPE.DATA, BUTTON.SEND_3))
        buttonlist.append(Button(81, "L_MODE PLAN", "AirbusFBW/NDmodeCapt", DREF_TYPE.DATA, BUTTON.SEND_4))
        buttonlist.append(Button(82, "L_RANGE 10", "AirbusFBW/NDrangeCapt", DREF_TYPE.DATA, BUTTON.SEND_0))
        buttonlist.append(Button(83, "L_RANGE 20", "AirbusFBW/NDrangeCapt", DREF_TYPE.DATA, BUTTON.SEND_1))
        buttonlist.append(Button(84, "L_RANGE 40", "AirbusFBW/NDrangeCapt", DREF_TYPE.DATA, BUTTON.SEND_2))
        buttonlist.append(Button(85, "L_RANGE 80", "AirbusFBW/NDrangeCapt", DREF_TYPE.DATA, BUTTON.SEND_3))
        buttonlist.append(Button(86, "L_RANGE 160", "AirbusFBW/NDrangeCapt", DREF_TYPE.DATA, BUTTON.SEND_4))
        buttonlist.append(Button(87, "L_RANGE 320", "AirbusFBW/NDrangeCapt", DREF_TYPE.DATA, BUTTON.SEND_5))
        buttonlist.append(Button(88, "L_1 ADF", "sim/cockpit2/EFIS/EFIS_1_selection_pilot", DREF_TYPE.DATA, BUTTON.SEND_0))
        buttonlist.append(Button(89, "L_1 OFF", "sim/cockpit2/EFIS/EFIS_1_selection_pilot", DREF_TYPE.DATA, BUTTON.SEND_1))
        buttonlist.append(Button(90, "L_1 VOR", "sim/cockpit2/EFIS/EFIS_1_selection_pilot", DREF_TYPE.DATA, BUTTON.SEND_2))
        buttonlist.append(Button(91, "L_2 ADF", "sim/cockpit2/EFIS/EFIS_2_selection_pilot", DREF_TYPE.DATA, BUTTON.SEND_0))
        buttonlist.append(Button(92, "L_2 OFF", "sim/cockpit2/EFIS/EFIS_2_selection_pilot", DREF_TYPE.DATA, BUTTON.SEND_1))
        buttonlist.append(Button(93, "L_2 VOR", "sim/cockpit2/EFIS/EFIS_2_selection_pilot", DREF_TYPE.DATA, BUTTON.SEND_2))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowARPTCapt", DREF_TYPE.DATA, BUTTON.NONE)) #, Leds.EFISR_ARPT_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowNDBCapt", DREF_TYPE.DATA, BUTTON.NONE)) #, Leds.EFISR_NDB_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowNDBCapt", DREF_TYPE.DATA, BUTTON.NONE)) #, Leds.EFISR_NDB_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowVORDCapt", DREF_TYPE.DATA, BUTTON.NONE)) #, Leds.EFISR_VORD_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowWPTCapt", DREF_TYPE.DATA, BUTTON.NONE)) #, Leds.EFISR_WPT_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/NDShowCSTRCapt", DREF_TYPE.DATA, BUTTON.NONE)) #, Leds.EFISR_CSTR_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/FD1Engage", DREF_TYPE.DATA, BUTTON.NONE)) #, Leds.EFISR_FD_GREEN))
        buttonlist.append(Button(None, "None", "AirbusFBW/ILSonCapt", DREF_TYPE.DATA, BUTTON.NONE)) #, Leds.EFISR_LS_GREEN))


def RequestDataRefs(xp):
    for idx,b in enumerate(buttonlist):
        datacache[b.dataref] = None
        if b.dreftype != DREF_TYPE.CMD and b.led != None:
            print(f"register dataref {b.dataref}")
            xp.AddDataRef(b.dataref, 3)
    for d in datarefs:
        print(f"register dataref {d[0]}")
        datacache[d[0]] = None
        xp.AddDataRef(d[0], d[1])


def xor_bitmask(a, b, bitmask):
    return (a & bitmask) != (b & bitmask)


def fcu_button_event():
    #print(f'events: press: {buttons_press_event}, release: {buttons_release_event}')
    for b in buttonlist:
        if not any(buttons_press_event) and not any(buttons_release_event):
            break
        if b.id == None:
            continue
        if buttons_press_event[b.id]:
            buttons_press_event[b.id] = 0
            #print(f'button {b.label} pressed')
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
            elif b.type == BUTTON.SEND_0:
                if b.dreftype== DREF_TYPE.DATA:
                    print(f'set dataref {b.dataref} to 0')
                    xp.WriteDataRef(b.dataref, 0)
            elif b.type == BUTTON.SEND_1:
                if b.dreftype== DREF_TYPE.DATA:
                    print(f'set dataref {b.dataref} to 1')
                    xp.WriteDataRef(b.dataref, 1)
            elif b.type == BUTTON.SEND_2:
                if b.dreftype== DREF_TYPE.DATA:
                    print(f'set dataref {b.dataref} to 2')
                    xp.WriteDataRef(b.dataref, 2)
            elif b.type == BUTTON.SEND_3:
                if b.dreftype== DREF_TYPE.DATA:
                    print(f'set dataref {b.dataref} to 3')
                    xp.WriteDataRef(b.dataref, 3)
            elif b.type == BUTTON.SEND_4:
                if b.dreftype== DREF_TYPE.DATA:
                    print(f'set dataref {b.dataref} to 4')
                    xp.WriteDataRef(b.dataref, 4)
            elif b.type == BUTTON.SEND_5:
                if b.dreftype== DREF_TYPE.DATA:
                    print(f'set dataref {b.dataref} to 5')
                    xp.WriteDataRef(b.dataref, 5)
            else:
                print(f'no known button type for button {b.label}')
        if buttons_release_event[b.id]:
            buttons_release_event[b.id] = 0
            print(f'button {b.label} released')
            if b.type == BUTTON.SWITCH:
                xp.WriteDataRef(b.dataref, 0)


def fcu_create_events(ep_in, ep_out):
        global values
        sleep(2) # wait for values to be available
        buttons_last = 0
        while True:
            if not xplane_connected: # wait for x-plane
                sleep(1)
                continue

            set_datacache(values)
            values_processed.set()
            sleep(0.005)
            try:
                data_in = ep_in.read(0x81, 105)
            except Exception as error:
                print(f' *** continue after usb-in error: {error} ***')
                continue
            if len(data_in) != 41:
                print(f'rx data count {len(data_in)} not valid')
                continue
            buttons=data_in[1] | (data_in[2] << 8) | (data_in[3] << 16) | (data_in[4] << 24) # FCU
            if device_config & DEVICEMASK.EFISR:
                buttons |= (data_in[9] << 32) | (data_in[10] << 40 ) | (data_in[11] << 48) | (data_in[12] << 56)
            if device_config & DEVICEMASK.EFISL:
                buttons |= (data_in[5] << 64) | (data_in[6] << 72 ) | (data_in[7] << 80) | (data_in[8] << 88)
            for i in range (BUTTONS_CNT):
                mask = 0x01 << i
                if xor_bitmask(buttons, buttons_last, mask):
                    #print(f"buttons: {format(buttons, "#04x"):^14}")
                    if buttons & mask:
                        buttons_press_event[i] = 1
                    else:
                        buttons_release_event[i] = 1
                    fcu_button_event()
            buttons_last = buttons


def set_button_led_lcd(dataref, v):
    global led_brightness
    for b in buttonlist:
        if b.dataref == dataref:
            if b.led == None:
                break
            if v >= 255:
                v = 255
            print(f'led: {b.led}, value: {v}')

            winwing_fcu_set_leds(fcu_out_endpoint, b.led, int(v))
            if b.led == Leds.BACKLIGHT:
                winwing_fcu_set_led(fcu_out_endpoint, Leds.EXPED_YELLOW, int(v))
                print(f'set led brigthness: {b.led}, value: {v}')
                led_brightness = v
            break


def set_datacache(values):
    global datacache
    global exped_led_state

    new = False
    for v in values:
        #print(f'cache: v:{v} val:{values[v]}')
        if v == 'AirbusFBW/SupplLightLevelRehostats[0]' and values[v] <= 1:
            # brightness is in 0..1, we need 0..255
            values[v] = int(values[v] * 255)
        if v == 'AirbusFBW/SupplLightLevelRehostats[1]' and values[v] <= 1:
            # brightness is in 0..1, we need 0..255
            values[v] = int(values[v] * 235 + 20)
        if v == 'sim/cockpit2/electrical/instrument_brightness_ratio_manual[10]' and values[v] <= 1:
            # brightness is in 0..1, we need 0..255
            values[v] = int(values[v] * 255)
        if v == 'sim/cockpit2/electrical/instrument_brightness_ratio_manual[14]' and values[v] <= 1:
            # brightness is in 0..1, we need 0..255
            values[v] = int(values[v] * 255)
        spd_mach = datacache['sim/cockpit/autopilot/airspeed_is_mach']
        if spd_mach and v == 'sim/cockpit2/autopilot/airspeed_dial_kts_mach' and values[v] < 1:
            values[v] = (values[v] +0.005 ) * 100
        if device_config & DEVICEMASK.EFISR and v == 'sim/cockpit2/gauges/actuators/barometer_setting_in_hg_copilot' and values[v] < 100:
            values[v] = (values[v] + 0.005) * 100
        if datacache[v] != int(values[v]):
            new = True
            print(f'cache: v:{v} val:{int(values[v])}')
            datacache[v] = int(values[v])
            set_button_led_lcd(v, int(values[v]))
    if new == True or usb_retry == True:
        speed = datacache['sim/cockpit2/autopilot/airspeed_dial_kts_mach']
        heading = datacache['sim/cockpit/autopilot/heading_mag']
        alt = datacache['sim/cockpit/autopilot/altitude']
        vs = datacache['sim/cockpit/autopilot/vertical_velocity']
        hdg = datacache['AirbusFBW/HDGTRKmode']
        if vs < 0:
            vs = abs(vs)
            flags['vs_vert'].value = False
        else:
            flags['vs_vert'].value = True

        flags['fpa_comma'].value = False
        if datacache['AirbusFBW/SPDdashed']:
            speed = '---'
        if datacache['AirbusFBW/HDGdashed']:
            heading = '---'
        if datacache['AirbusFBW/VSdashed']:
            vs = '----'
            flags['vs_vert'].value = False
        elif not hdg:
            # small 0 for hundred-feed chars in v/s mode
            vs = string_fix_length(int(vs/100), 2)
            vs = vs.ljust(4, '#')
            #print(f"vs: {v}")
        else:
            vs = string_fix_length(int(vs / 100), 2)
            vs = vs.ljust(4, ' ')
            flags['fpa_comma'].value = True
        flags['spd_managed'].value = not not datacache['AirbusFBW/SPDmanaged']
        flags['hdg_managed'].value = not not datacache['AirbusFBW/HDGmanaged']
        flags['alt_managed'].value = not not datacache['AirbusFBW/ALTmanaged']
        flags['spd'].value = not spd_mach
        flags['mach'].value = not not spd_mach
        flags['mach_comma'].value = not not spd_mach

        flags['hdg'].value = not hdg
        flags['trk'].value = not not hdg
        flags['fvs'].value = not hdg
        flags['vshdg'].value = not hdg
        flags['vs'].value = not hdg
        flags['ftrk'].value = not not hdg
        flags['ffpa'].value = not not hdg
        flags['ffpa2'].value = not not hdg

        if True:
            try: # dataref may not be received already, even when connected
                exped_led_state_desired = datacache['AirbusFBW/APVerticalMode'] >= 112
            except:
                exped_led_state_desired = False
            if exped_led_state_desired != exped_led_state:
                exped_led_state = exped_led_state_desired
                winwing_fcu_set_led(fcu_out_endpoint, Leds.EXPED_GREEN, led_brightness * exped_led_state_desired)

        winwing_fcu_set_lcd(fcu_out_endpoint, speed, heading, alt, vs)
        sleep(0.05)

        if device_config & DEVICEMASK.EFISR:
            std = datacache['AirbusFBW/BaroStdFO']
            unit = datacache['AirbusFBW/BaroUnitFO']
            flags['efisr_qnh'].value = not std
            if std:
                baro = 'Std '
            else:
                baro = datacache['sim/cockpit2/gauges/actuators/barometer_setting_in_hg_copilot']
                if unit:
                   baro = int((baro * 33.86388 + 50) / 100)
            flags['efisr_hpa_dec'].value = not unit and not std

            if datacache['baro_efisr_last'] != baro:
                winwing_efisr_set_lcd(fcu_out_endpoint, baro)
                sleep(0.05)
                datacache['baro_efisr_last'] = baro
        # TODO EFISL


def kb_wait_quit_event():
    print(f"*** Press ENTER to quit this script ***\n")
    while True:
        c = input() # wait for ENTER (not worth to implement kbhit for differnt plattforms, so make it very simple)
        print(f"Exit")
        os._exit(0)


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


def main():
    global xp
    global fcu_in_endpoint, fcu_out_endpoint
    global values, xplane_connected
    global device_config

    backend = find_usblib()

    devlist = [{'vid':0x4098, 'pid':0xbb10, 'name':'FCU', 'mask':DEVICEMASK.FCU},
               {'vid':0x4098, 'pid':0xbc1e, 'name':'FCU + EFIS-R', 'mask':DEVICEMASK.FCU | DEVICEMASK.EFISR},
               {'vid':0x4098, 'pid':0xbc1d, 'name':'FCU + EFIS-L (EFIS-L not supported)', 'mask':DEVICEMASK.FCU | DEVICEMASK.EFISL},
               {'vid':0x4098, 'pid':0xba01, 'name':'FCU + EFIS-L + EFIS-R (EFIS-L not supported)', 'mask':DEVICEMASK.FCU | DEVICEMASK.EFISL | DEVICEMASK.EFISR}]

    for d in devlist:
        print(f"now searching for winwing {d['name']} ... ", end='')
        device = usb.core.find(idVendor=d['vid'], idProduct=d['pid'], backend=backend)
        if device is not None:
            print(f"found")
            device_config |= d['mask']
            break
        else:
            print(f"not found")

    if device is None:
        exit(f"No compatible winwing device found, quit")


    print('compatible with X-Plane 11/12 and all Toliss Airbus')

    create_button_list_fcu()
    datacache['baro_efisr_last'] = None
    datacache['baro_efisl_last'] = None

    interface = device[0].interfaces()[0]
    if device.is_kernel_driver_active(interface.bInterfaceNumber):
        device.detach_kernel_driver(interface.bInterfaceNumber)

    device.set_configuration()

    endpoints = device[0].interfaces()[0].endpoints()
    fcu_out_endpoint = endpoints[1]
    fcu_in_endpoint = endpoints[0]
    
    leds = [Leds.SCREEN_BACKLIGHT]
    if device_config & DEVICEMASK.EFISR:
      leds.append(Leds.EFISR_BACKLIGHT)
    if device_config & DEVICEMASK.EFISL:
      leds.append(Leds.EFISL_BACKLIGHT)

    winwing_fcu_set_leds(fcu_out_endpoint, leds, 180)
    winwing_fcu_set_leds(fcu_out_endpoint, leds, 80)
    winwing_fcu_set_lcd(fcu_out_endpoint, "   ", "   ", "Schen", " lap")
    if device_config & DEVICEMASK.EFISR:
        winwing_efisr_set_lcd(fcu_out_endpoint, '----')
    #TODO set EFISL

    usb_event_thread = Thread(target=fcu_create_events, args=[fcu_in_endpoint, fcu_out_endpoint])
    usb_event_thread.start()

    kb_quit_event_thread = Thread(target=kb_wait_quit_event)
    kb_quit_event_thread.start()

    xp = XPlaneUdp.XPlaneUdp()
    xp.BeaconData["IP"] = UDP_IP # workaround to set IP and port
    xp.BeaconData["Port"] = UDP_PORT
    xp.UDP_PORT = xp.BeaconData["Port"]
    print(f'wait for X-Plane to connect on port {xp.BeaconData["Port"]}')

    while True:
        if not xplane_connected:
            try:
                xp.AddDataRef("sim/aircraft/view/acf_tailnum")
                values = xp.GetValues()
                xplane_connected = True
                print(f"X-Plane connected")
                RequestDataRefs(xp)
                xp.AddDataRef("sim/aircraft/view/acf_tailnum", 0)
            except XPlaneUdp.XPlaneTimeout:
                xplane_connected = False
                sleep(2)
                print(f"wait for X-Plane")
            continue

        try:
            values = xp.GetValues()
            values_processed.wait()
            #print(values)
            #values will be handled in fcu_create_events to write to usb only in one thread.
            # see function set_datacache(values)
        except XPlaneUdp.XPlaneTimeout:
            print(f'X-Plane timeout, could not connect on port {xp.BeaconData["Port"]}')
            xplane_connected = False
            sleep(2)

if __name__ == '__main__':
  main() 
