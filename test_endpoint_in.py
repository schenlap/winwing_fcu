#!/bin/env python3

from dataclasses import dataclass
import time
import usb.core
import usb.backend.libusb1
import usb.util

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

device.set_configuration()

endpoints = device[0].interfaces()[0].endpoints()
print(endpoints)

endpoint_in = endpoints[0]
print(endpoint_in)

while True:
    buf_in = [None] * 7
    num_bytes = endpoint_in.read(0x81, 7)
    print(num_bytes)
    time.sleep(0.5)
