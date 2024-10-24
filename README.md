# winwing_fcu
A X-Plane plugin for winwing fcu for ToLISS Airbus A319.
So far it is a framework to trigger buttons and set LEDs from the flight simulator. It currently works with the winwing rudder device because I haven't received my fcu yet.

Tested with XP11.

## installation
copy `udev/71-winwing.rules` to `/etc/udev/rules.d`
sudo cp udev/71-winwing.rules /etc/udev/rules.d/

sudo aptitude install python3-evdev python3-usb

reread config
`udevadm control --reload-rules`

## start
1. start X-Plane
2. ./winwing_rudder.py
