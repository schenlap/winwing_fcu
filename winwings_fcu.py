#!/bin/env python3

# IP Address of machine running X-Plane. 
UDP_IP = "127.0.0.1"
UDP_PORT = 49000

import binascii
import socket
import struct

#for raw usb
import re
import subprocess

import pyglet

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
    ("AirbusFBW/HDGTRKmode", "-", "V/FPA Mode", 2)


  ]

def RequestDataRefs(sock):
  for idx,dataref in enumerate(datarefs):
    # Send one RREF Command for every dataref in the list.
    # Give them an index number and a frequency in Hz.
    # To disable sending you send frequency 0. 
    cmd = b"RREF\x00"
    freq=1
    string = datarefs[idx][0].encode()
    message = struct.pack("<5sii400s", cmd, freq, idx, string)
    assert(len(message)==413)
    sock.sendto(message, (UDP_IP, UDP_PORT))

def DecodePacket(data):
  retvalues = {}
  # Read the Header "RREFO".
  header=data[0:4]
  if(header!=b"RREF"):
    print("Unknown packet: ", binascii.hexlify(data))
  else:
    # We get 8 bytes for every dataref sent:
    #    An integer for idx and the float value. 
    values =data[5:]
    lenvalue = 8
    numvalues = int(len(values)/lenvalue)
    idx=0
    value=0
    for i in range(0,numvalues):
      singledata = data[(5+lenvalue*i):(5+lenvalue*(i+1))]
      (idx,value) = struct.unpack("<if", singledata)
      retvalues[idx] = (value, datarefs[idx][1], datarefs[idx][0])
  return retvalues

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

def main():
    print_usb_device()

    joysticks = pyglet.input.get_joysticks()
    devices = pyglet.input.get_devices()
    print(joysticks)

    # Open a Socket on UDP Port 49000
    sock = socket.socket(socket.AF_INET, # Internet
                       socket.SOCK_DGRAM) # UDP

    RequestDataRefs(sock)

    while True:
        # Receive packet
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        # Decode Packet
        values = DecodePacket(data)
        # Example values:
        # {
        #   0: (  47.85240554 , '°N'  , 'sim/flightmodel/position/latitude'           ),
        #   1: (  12.54742622 , '°E'  , 'sim/flightmodel/position/longitude'          ),
        #   2: (  1502.2      , 'ft'  , 'sim/flightmodel/misc/h_ind'                  ),
        #   3: (  0.01        , 'm'   , 'sim/flightmodel/position/y_agl'              ),
        #   4: (  76.41       , '°'   , 'sim/flightmodel/position/mag_psi'            ),
        #   5: ( -9.76e-05    , 'kt'  , 'sim/flightmodel/position/indicated_airspeed' ),
        #   6: (  1.39e-05    , 'm/s' , 'sim/flightmodel/position/groundspeed'        ),
        #   7: ( -1.37e-06    , 'm/s' , 'sim/flightmodel/position/vh_ind'             )
        # }

        # Print Values:
        for key,val in values.items():
          print(("{0:10."+str(datarefs[key][3])+"f} {1:<5} {2}").format(val[0],val[1],val[2]))
        print()
        # Example:
        # 47.852406 °N    sim/flightmodel/position/latitude
        # 12.547426 °E    sim/flightmodel/position/longitude
        #      1502 ft    sim/flightmodel/misc/h_ind
        #         0 m     sim/flightmodel/position/y_agl
        #        76 °     sim/flightmodel/position/mag_psi
        #        -0 kt    sim/flightmodel/position/indicated_airspeed
        #         0 m/s   sim/flightmodel/position/groundspeed
        #      -0.0 m/s   sim/flightmodel/position/vh_ind

if __name__ == '__main__':
  main() 
