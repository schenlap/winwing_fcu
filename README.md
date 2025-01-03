# Winwing Fcu
This script is to use Winwing A320 FCU on Linux (maybe Mac-OS) with X-Plane. 
All buttons, leds and lcd displays work the same way as in X-Plane.<br>
Tested with:
 * XP12 under linux (debian trixie)
 * XP11 under linux (debian bookworm)
 * XP12 under MacOs (Sequoia 15.0.1)
 * Toliss A319, A320Neo, A321Neo, A339, A340-600

Supported Hardware:
 * Winwing FCU: fully supported
 * Winwing EFIS-R: fully supported
 * Winwing EFIS-L: only buttons and switches supported, no lcd and no leds

## Installation

#### Debian based system
1. clone the repo where you want
2. copy `udev/71-winwing.rules` to `/etc/udev/rules.d`  
`sudo cp udev/71-winwing.rules /etc/udev/rules.d/`
3. install dependencies (on debian based systems)  
`sudo aptitude install python3-usb`
4. start script (with udev rule no sudo needed): `python3 ./winwing_fcu.py` when X-Plane with Toliss aircraft is loaded.


#### MAC-OS

1. clone the repo where you want
2. install homebrew
3. install dependencies
`python3 -m pip install pyusb`
4. brew install libusb
5. let pyusb find libusb: `ln -s /opt/homebrew/lib ~/lib` 
6. start script with sudo: `sudo python3 ./winwing_fcu.py` when X-Plane with Toliss aircraft is loaded.
7. A detailed installation instruction can be found on [x-plane forum](https://forums.x-plane.org/index.php?/forums/topic/310045-winwing-fcu-on-plane-12-on-a-mac-studio/&do=findComment&comment=2798635).

## Use FCU
1. start X-Plane
2. load Toliss A319
3. start script as written above
4. enjoy flying (and report bugs :-)  )

![fcu demo image](./documentation/fcu_demo.gif)

Change brightness with the two brightness knobs in the cockpit.
![fcu demo image](./documentation/xplane_fcu_brightness.png)


## developer documentation
See [documention](./documentation/README.md) for developers

## Notes
Use at your own risk. Updates to the FCU can make the script incompatible.
TODO: The data sent in the USB protocol by SimApp Pro has not yet been fully implemented, only to the extent that it currently works.

## Next steps
 * EFIS-L LCD and LEDs when EFIS-L arrives (first only for supporters of this project)

## Contact
<memo5@gmx.at> or as pm in https://forums.x-plane.org, user memo5.
