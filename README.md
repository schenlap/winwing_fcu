# winwing_fcu
The goal is to develop a X-Plane plugin for winwing fcu for ToLISS Airbus A319.
So far it is a framework to trigger buttons and set LEDs on winwing fcu device.

Tested with XP12 under linux (debian trixie).

## installation (debian bases system)
1. copy `udev/71-winwing.rules` to `/etc/udev/rules.d`  
`sudo cp udev/71-winwing.rules /etc/udev/rules.d/`
2. install dependencies (on debian based systems)  
`sudo aptitude install python3-evdev python3-usb`

## MAC-OS
If you can help with the MAX-OS integration, please create a pull request.

## test framework
1. Make test_endpoint executable  
   `chmod +x ./test_endpoint.py`
2. test connection  
   `./test_endpoint.py`  
   AP1 and AP2 led should blink alternately

## developers
See [documention](./documentation/README.md) for developers
