#!/bin/env python3

# IP Address of machine running X-Plane. 
UDP_IP = "127.0.0.1"
UDP_PORT = 49000

import binascii
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

BUTTONS_CNT = 7

class BUTTON(Enum):
    SWITCH = 0
    TOGGLE = 1

class Leds(Enum):
    LEFT = 0
    RIGHT = 1
    LEFT_AND_RIGHT = 2
    LOGO = 3

class Button:
    def __init__(self, nr, label, dataref, button_type = BUTTON.SWITCH, led = None):
        self.id = nr
        self.label = label
        self.dataref = dataref
        #self.data = None
        self.type = button_type
        self.led = led

buttonlist = []

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



def create_button_list():
    buttonlist.append(Button(0, "AP2", "AirbusFBW/AP2Engage", BUTTON.TOGGLE, Leds.RIGHT))
    buttonlist.append(Button(1, "AP1", "AirbusFBW/AP1Engage", BUTTON.TOGGLE, Leds.LEFT))

def create_button_list_fcu():
    buttonlist.append(Button(0, "MACH"))
    buttonlist.append(Button(1, "LOC"))
    buttonlist.append(Button(2, "TRK"))
    buttonlist.append(Button(3, "AP1"))
    buttonlist.append(Button(4, "AP2"))
    buttonlist.append(Button(5, "A/THR"))
    buttonlist.append(Button(6, "EXPED"))
    buttonlist.append(Button(7, "METRIC"))
    buttonlist.append(Button(8, "APPR"))
    buttonlist.append(Button(9, "SPD DEC"))
    buttonlist.append(Button(10, "SPD INC"))
    buttonlist.append(Button(11, "SPD PUSH"))
    buttonlist.append(Button(12, "SPD PULL"))
    buttonlist.append(Button(13, "HDG DEC"))
    buttonlist.append(Button(14, "HDG INC"))
    buttonlist.append(Button(15, "HDG PUSH"))
    buttonlist.append(Button(16, "HDG PULL"))
    buttonlist.append(Button(17, "ALT DEC"))
    buttonlist.append(Button(18, "ALT INC"))
    buttonlist.append(Button(19, "ALT PUSH"))
    buttonlist.append(Button(20, "ALT PULL"))
    buttonlist.append(Button(21, "VS DEC"))
    buttonlist.append(Button(22, "VS INC"))
    buttonlist.append(Button(23, "VS PUSH"))
    buttonlist.append(Button(24, "VS PULL"))
    buttonlist.append(Button(25, "ALT 100"))
    buttonlist.append(Button(26, "ALT 1000"))
    buttonlist.append(Button(27, "FD"))
    buttonlist.append(Button(28, "RES"))


def RequestDataRefs(xp):
  for idx,b in enumerate(buttonlist):
    datacache[b.dataref] = None
    xp.AddDataRef(b.dataref, 3)


def print_usb_device():
    device_re = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split(b'\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)

    print(*devices, sep="\n")

def get_usb_fcu_device():
    dev_list = evdev.list_devices()

    fcu_device = None
    for device in dev_list:
        d = evdev.InputDevice(device)
        print(d.name)
        if d.name == 'Winwing WINWING SKYWALKER Metal Rudder Pedals':
            print(f'found {d.name}')
            print(d.capabilities(verbose=True))
            d.close()
            return device
        d.close()
    return None

def fcu_set_led(ep_out, led, brightness):
    #02 f0 be 00 00 08 06 e8 00 00 8d 06 bc ff         l,r, logo  -> speichert werte?
    data = [0x02, 0xf0, 0xbe, 0, 0, 3, 0x49, led.value, brightness, 0,0,0,0,0]
    cmd = bytes(data)
    ep_out.write(cmd)

def xor_bitmask(a, b, bitmask):
    return (a & bitmask) != (b & bitmask)


def fcu_button_event():
    print(f'evets: press: {buttons_press_event}, release: {buttons_release_event}')
    for b in buttonlist:
        if buttons_press_event[b.id]:
            buttons_press_event[b.id] = 0
            print(f'button {b.label} pressed')
            val = datacache[b.dataref]
            print(f'set dataref {b.dataref} from {bool(val)} to {not bool(val)}')
            if b.type == BUTTON.TOGGLE:
                xp.WriteDataRef(b.dataref, not bool(val))
            else:
                xp.WriteDataRef(b.dataref, 1)
        if buttons_release_event[b.id]:
            buttons_release_event[b.id] = 0
            print(f'button {b.label} released')
            if b.type == BUTTON.SWITCH:
                xp.WriteDataRef(b.dataref, 0)


def fcu_create_events(ep_in, ep_out, event):
        buttons_last = 0
        while True:
            sleep(0.1)
            data_in = ep_in.read(0x81, 7)
            #print(f'usb ep data in: {data_in}')
            buttons=data_in[1]
            for i in range (3):
                mask = 0x01 << i
                if xor_bitmask(buttons, buttons_last, mask):
                    if buttons & mask:
                        buttons_press_event[i] = 1
                        #fcu_set_led(ep_out, Leds.LOGO, 255)
                    else:
                        buttons_release_event[i] = 1
                        #fcu_set_led(ep_out, Leds.LOGO, 0)
                    event.set()
                    fcu_button_event()
            buttons_last = buttons
            #print(f'evets: press: {buttons_press_event}, release: {buttons_release_event}')

def set_button_led(dataref, v):
    for b in buttonlist:
        if b.dataref == dataref:
            if v >= 1:
                v = 200
            print(f'led: {b.led}, value: {v}')
            fcu_set_led(fcu_out_endpoint, b.led, int(v))
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

    create_button_list()
    #print_usb_device()

    device = usb.core.find(idVendor=0x4098, idProduct=0xbb10)
    if device is None:
        raise RuntimeError('Device not found')
    print('Found winwing rudder device')
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
