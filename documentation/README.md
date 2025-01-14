# Documentation for developers

## usb device information ##
### kernel messages on connect ###
```
new full-speed USB device number 2 using xhci_hcd
New USB device found, idVendor=4098, idProduct=bb10, bcdDevice= 1.16
New USB device strings: Mfr=1, Product=2, SerialNumber=3
Product: WINWING FCU-320
Manufacturer: Winwing
SerialNumber: B4A27072F4661321B25XXXXX
Winwing WINWING FCU-320: Invalid code 768 type 1
Winwing WINWING FCU-320: Invalid code 769 type 1
Winwing WINWING FCU-320: Invalid code 770 type 1
Winwing WINWING FCU-320: Invalid code 771 type 1
Winwing WINWING FCU-320: Invalid code 772 type 1
Winwing WINWING FCU-320: Invalid code 773 type 1
Winwing WINWING FCU-320: Invalid code 774 type 1
Winwing WINWING FCU-320: Invalid code 775 type 1
Winwing WINWING FCU-320: Invalid code 776 type 1
Winwing WINWING FCU-320: Invalid code 777 type 1
```

### usb decriptor FCU ###
```
Bus 005 Device 002: ID 4098:bb10 Winwing WINWING FCU-320
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               2.00
  bDeviceClass            0 [unknown]
  bDeviceSubClass         0 [unknown]
  bDeviceProtocol         0 
  bMaxPacketSize0        64
  idVendor           0x4098 Winwing
  idProduct          0xbb10 WINWING FCU-320
  bcdDevice            1.16
  iManufacturer           1 Winwing
  iProduct                2 WINWING FCU-320
  iSerial                 3 B4A27072F4661321B25XXXXX
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength       0x0029
    bNumInterfaces          1
    bConfigurationValue     1
    iConfiguration          0 
    bmAttributes         0x80
      (Bus Powered)
    MaxPower              100mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           2
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      0 [unknown]
      bInterfaceProtocol      0 
      iInterface              0 
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength     249
          Report Descriptors: 
            ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81  EP 1 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval               1
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x02  EP 2 OUT
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval               1
Device Status:     0x0000
  (Bus Powered)
```
hid descriptor read `cat /sys/kernel/debug/hid/0003\:4098\:BB10.0006/rdesc`

```
0x05, 0x01,        // Usage Page (Generic Desktop Ctrls)
0x09, 0x04,        // Usage (Joystick)
0xA1, 0x01,        // Collection (Application)
0x85, 0x01,        //   Report ID (1)
0x05, 0x09,        //   Usage Page (Button)
0x19, 0x01,        //   Usage Minimum (0x01)
0x29, 0x80,        //   Usage Maximum (0x80)
0x15, 0x00,        //   Logical Minimum (0)
0x25, 0x01,        //   Logical Maximum (1)
0x35, 0x00,        //   Physical Minimum (0)
0x45, 0x01,        //   Physical Maximum (1)
0x75, 0x01,        //   Report Size (1)
0x95, 0x80,        //   Report Count (-128)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
0x09, 0x30,        //   Usage (X)
0x15, 0x00,        //   Logical Minimum (0)
0x27, 0xFF, 0xFF, 0x00, 0x00,  //   Logical Maximum (65534)
0x35, 0x00,        //   Physical Minimum (0)
0x47, 0xFF, 0xFF, 0x00, 0x00,  //   Physical Maximum (65534)
0x75, 0x10,        //   Report Size (16)
0x95, 0x01,        //   Report Count (1)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
0x09, 0x31,        //   Usage (Y)
0x15, 0x00,        //   Logical Minimum (0)
0x27, 0xFF, 0xFF, 0x00, 0x00,  //   Logical Maximum (65534)
0x35, 0x00,        //   Physical Minimum (0)
0x47, 0xFF, 0xFF, 0x00, 0x00,  //   Physical Maximum (65534)
0x75, 0x10,        //   Report Size (16)
0x95, 0x01,        //   Report Count (1)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
0x09, 0x32,        //   Usage (Z)
0x15, 0x00,        //   Logical Minimum (0)
0x27, 0xFF, 0xFF, 0x00, 0x00,  //   Logical Maximum (65534)
0x35, 0x00,        //   Physical Minimum (0)
0x47, 0xFF, 0xFF, 0x00, 0x00,  //   Physical Maximum (65534)
0x75, 0x10,        //   Report Size (16)
0x95, 0x01,        //   Report Count (1)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
0x09, 0x33,        //   Usage (Rx)
0x15, 0x00,        //   Logical Minimum (0)
0x27, 0xFF, 0xFF, 0x00, 0x00,  //   Logical Maximum (65534)
0x35, 0x00,        //   Physical Minimum (0)
0x47, 0xFF, 0xFF, 0x00, 0x00,  //   Physical Maximum (65534)
0x75, 0x10,        //   Report Size (16)
0x95, 0x01,        //   Report Count (1)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
0x09, 0x36,        //   Usage (Slider)
0x15, 0x00,        //   Logical Minimum (0)
0x27, 0xFF, 0xFF, 0x00, 0x00,  //   Logical Maximum (65534)
0x35, 0x00,        //   Physical Minimum (0)
0x47, 0xFF, 0xFF, 0x00, 0x00,  //   Physical Maximum (65534)
0x75, 0x10,        //   Report Size (16)
0x95, 0x01,        //   Report Count (1)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
0x09, 0x37,        //   Usage (Dial)
0x15, 0x00,        //   Logical Minimum (0)
0x27, 0xFF, 0xFF, 0x00, 0x00,  //   Logical Maximum (65534)
0x35, 0x00,        //   Physical Minimum (0)
0x47, 0xFF, 0xFF, 0x00, 0x00,  //   Physical Maximum (65534)
0x75, 0x10,        //   Report Size (16)
0x95, 0x01,        //   Report Count (1)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
0x15, 0x00,        //   Logical Minimum (0)
0x27, 0xFF, 0xFF, 0x00, 0x00,  //   Logical Maximum (65534)
0x35, 0x00,        //   Physical Minimum (0)
0x47, 0xFF, 0xFF, 0x00, 0x00,  //   Physical Maximum (65534)
0x09, 0xD0,        //   Usage (0xD0)
0x09, 0xD1,        //   Usage (0xD1)
0x09, 0xD2,        //   Usage (0xD2)
0x09, 0xD3,        //   Usage (0xD3)
0x09, 0xD4,        //   Usage (0xD4)
0x09, 0xD5,        //   Usage (0xD5)
0x75, 0x10,        //   Report Size (16)
0x95, 0x06,        //   Report Count (6)
0x81, 0x01,        //   Input (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x85, 0x02,        //   Report ID (2)
0x06, 0xFF, 0x00,  //   Usage Page (Reserved 0xFF)
0x09, 0x01,        //   Usage (0x01)
0x15, 0x00,        //   Logical Minimum (0)
0x26, 0xFF, 0x00,  //   Logical Maximum (255)
0x35, 0x00,        //   Physical Minimum (0)
0x46, 0xFF, 0x00,  //   Physical Maximum (255)
0x75, 0x08,        //   Report Size (8)
0x95, 0x0D,        //   Report Count (13)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x09, 0x02,        //   Usage (0x02)
0x91, 0x02,        //   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
0x85, 0xF0,        //   Report ID (-16)
0x06, 0xFF, 0x00,  //   Usage Page (Reserved 0xFF)
0x09, 0x03,        //   Usage (0x03)
0x95, 0x3F,        //   Report Count (63)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x09, 0x04,        //   Usage (0x04)
0x91, 0x02,        //   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
0xC0,              // End Collection

// 249 bytes
```

### usb decriptor FCU with EFIS Right ###

```
0x05, 0x01,        // Usage Page (Generic Desktop Ctrls)
0x09, 0x04,        // Usage (Joystick)
0xA1, 0x01,        // Collection (Application)
0x85, 0x01,        //   Report ID (1)
0x05, 0x09,        //   Usage Page (Button)
0x19, 0x01,        //   Usage Minimum (0x01)
0x29, 0x0F,        //   Usage Maximum (0x0F)
0x15, 0x00,        //   Logical Minimum (0)
0x25, 0x01,        //   Logical Maximum (1)
0x35, 0x00,        //   Physical Minimum (0)
0x45, 0x01,        //   Physical Maximum (1)
0x75, 0x01,        //   Report Size (1)
0x95, 0x0F,        //   Report Count (15)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x75, 0x01,        //   Report Size (1)
0x95, 0x01,        //   Report Count (1)
0x81, 0x01,        //   Input (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
0x09, 0x33,        //   Usage (Rx)
0x15, 0x00,        //   Logical Minimum (0)
0x27, 0xFF, 0xFF, 0x00, 0x00,  //   Logical Maximum (65534)
0x35, 0x00,        //   Physical Minimum (0)
0x47, 0xFF, 0xFF, 0x00, 0x00,  //   Physical Maximum (65534)
0x75, 0x10,        //   Report Size (16)
0x95, 0x01,        //   Report Count (1)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
0x09, 0x34,        //   Usage (Ry)
0x15, 0x00,        //   Logical Minimum (0)
0x27, 0xFF, 0xFF, 0x00, 0x00,  //   Logical Maximum (65534)
0x35, 0x00,        //   Physical Minimum (0)
0x47, 0xFF, 0xFF, 0x00, 0x00,  //   Physical Maximum (65534)
0x75, 0x10,        //   Report Size (16)
0x95, 0x01,        //   Report Count (1)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x05, 0x01,        //   Usage Page (Generic Desktop Ctrls)
0x09, 0x35,        //   Usage (Rz)
0x15, 0x00,        //   Logical Minimum (0)
0x27, 0xFF, 0xFF, 0x00, 0x00,  //   Logical Maximum (65534)
0x35, 0x00,        //   Physical Minimum (0)
0x47, 0xFF, 0xFF, 0x00, 0x00,  //   Physical Maximum (65534)
0x75, 0x10,        //   Report Size (16)
0x95, 0x01,        //   Report Count (1)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x85, 0x02,        //   Report ID (2)
0x06, 0xFF, 0x00,  //   Usage Page (Reserved 0xFF)
0x09, 0x01,        //   Usage (0x01)
0x15, 0x00,        //   Logical Minimum (0)
0x26, 0xFF, 0x00,  //   Logical Maximum (255)
0x35, 0x00,        //   Physical Minimum (0)
0x46, 0xFF, 0x00,  //   Physical Maximum (255)
0x75, 0x08,        //   Report Size (8)
0x95, 0x0D,        //   Report Count (13)
0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
0x09, 0x02,        //   Usage (0x02)
0x91, 0x02,        //   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
0xC0,              // End Collection

// 134 bytes
```

## test framework (without x-plane)
1. Make test_endpoint executable  
   `chmod +x ./test_endpoint.py`
2. test connection  
   `./test_endpoint.py`  
   AP1 and AP2 led should blink alternately

## sniff winwing usb protocol

I use Linux as host system and Windows in virt-manager that runs SimApp pro. Wirshark runs in Linux to sniff usb transfer.

![usb protocol mapping](./lcd_mapping.svg)

## wireshark

to start sniffing:
1. sudo mount -t debugfs none /sys/kernel/debug
2. sudo modprobe usbmon
3. sudo setfacl -m u:$USER:r /dev/usbmon*
4. wireshark


I wrote a [dissector ](..//wireshark_winwing_dissector.lua) for wirehark to parse the winwing protocol. Copy it to `~/.local/lib/wireshark/plugins/`to let wireshark use it. It will be use automtically for received usb data.
![winwing dissector](./dissector.png)


## Winwing Protocol (all devices)

| Report ID |ComponentID(1)|ComponentId(0)| | | Length Of Data | ? | led number | brightness | | | | | |
|--------|---------|----------|---------|----------|---------|----------|----|---|----------|----------|---------|----------|---------|
| 0x02 | 0xf0 | 0xbe | 0x00 | 0x00 | 0x03 | 0x49 | x | x | 0x00 | 0x00 | 0x00 | 0x00 | 0x00 |

A winwing device has many components. for example:
```
F18_GRIP:
  - WINWING_JOYSTICK_BASE1
  - JOYSTICK_BASE2
  - JOYSTICK_BASE2_2
```
Each component has its own ID that can be used to send cmd/data to it. Different devices may share same components, so we could use the same componentID to route cmd/data to it. At this time, it is not clear what the magic `0x49` means.

### Component ID

>Note: some of these are not recorded in HEX

>Note: if a componentId is `0xBB20`, the componentId(0) would be `20` and componentId(1) would be `bb`

|Name|ComponentID|
|----|---|
|F18_STARTUP_PANEL|48643|
|WINWING_THROTTLE_BASE1|48672|
|WINWING_THROTTLE_BASE1_F18_HANDLE|48674|
|F18_HANDLE|48642|
|WINWING_JOYSTICK_BASE1|48656|
|JOYSTICK_BASE1_F18_GRIP|48657|
|JOYSTICK_BASE1_ZAXIS|48660|
|JOYSTICK_BASE1_ZAXIS_F18_GRIP|48661|
|F18_GRIP|48641|
|F18_TAKEOFF_PANEL|0xBE04|
|F18_COMBAT_READY_PANEL|0xBE05|
|WINWING_THROTTLE_BASE2|0xBE30|
|Orion_Throttle_Base_II|0xBE60|
|WINWING_THROTTLE_BASE2_F18_HANDLE|0xBE32|
|TM_GRIP|0x4021|
|JOYSTICK_BASE2|0x0000BE40|
|JOYSTICK_BASE2_F18_GRIP|0x0000BE41|
|JOYSTICK_BASE2_ZAXIS|0x0000BE44|
|JOYSTICK_BASE2_ZAXIS_F18_GRIP|0x0000BE45|
|JOYSTICK_BASE2_2|0x0000BEA0|
|CGRIP_KA50|0xBE06|
|T3_BASE|0xBE50|
|JGRIP_320|0x1640|
|JGRIP_F16|0xBE07|
|TGRIP_F16|0xBE08|
|MFSSB|0xBE0C|
|MFD1|0xBE0D|
|UFC1|0xbed0|
|HUD1|48654|
|F15EX_HANDLE_L|0xBF0|
|F15EX_HANDLE_R|0xBF0|
|F15_HANDLE_R|0xBF0|
|F15_HANDLE_L|0xBF0|
|TAKEOFF_PLANEL_2|0xBF0|
|R1|0xBEF|
|ICP|0xBF0|
|JGRIP_C1_L|0xBF0|
|JGRIP_C1_R|0x0BF0|
|J5_BASE|0xBB2|
|FCU|0xBB1|
|JGRIP_F1_L|0xBF0|
|JGRIP_F1_R|0xBF0|
|JGRIP_S1_L|0xBF0|
|JGRIP_S1_R|0xBF0|
|EFIS_320_L|0xBF0|
|EFIS_320_R|0xBF0|
|PFP_3N|0xBB3|
|MCDU_32|0xBB3|
|PFP_7|0xBB3|
|PFP_4|0xBB3|
|MCP_73|0xBF0|

### Device - Components
|Device|Components|
|---|---|
|F18_HANDLE|[WINWING_THROTTLE_BASE1, WINWING_THROTTLE_BASE2, Orion_Throttle_Base_II, T3_BASE]|
|F18_GRIP|[WINWING_JOYSTICK_BASE1, JOYSTICK_BASE2, JOYSTICK_BASE2_2]|
|TM_GRIP|[WINWING_JOYSTICK_BASE1, JOYSTICK_BASE2, JOYSTICK_BASE2_2]|
|CGRIP_KA50|[WINWING_THROTTLE_BASE2, Orion_Throttle_Base_II, T3_BASE, WINWING_THROTTLE_BASE1]|
|JGRIP_320|[WINWING_JOYSTICK_BASE1, JOYSTICK_BASE2, JOYSTICK_BASE2_2]|
|JGRIP_F16|[WINWING_JOYSTICK_BASE1, JOYSTICK_BASE2, JOYSTICK_BASE2_2]|
|TGRIP_F16|[WINWING_THROTTLE_BASE2, Orion_Throttle_Base_II, T3_BASE, WINWING_THROTTLE_BASE1]|
|MFSSB|[JOYSTICK_BASE2_2]|
|HUD1|[UFC1]|
|F15EX_HANDLE_L|[WINWING_THROTTLE_BASE1,WINWING_THROTTLE_BASE2,T3_BASE,Orion_Throttle_Base_II]|
|F15EX_HANDLE_R|[WINWING_THROTTLE_BASE1,WINWING_THROTTLE_BASE2,T3_BASE,Orion_Throttle_Base_II]|
|F15_HANDLE_R|[WINWING_THROTTLE_BASE1,WINWING_THROTTLE_BASE2,T3_BASE,Orion_Throttle_Base_II]|
|JGRIP_C1_L|[J5_BASE]|
|JGRIP_C1_R|[J5_BASE]|
|JGRIP_F1_L|[J5_BASE]|
|JGRIP_F1_R|[J5_BASE]|
|JGRIP_S1_L|[J5_BASE]|
|JGRIP_S1_R|[J5_BASE]|
|EFIS_320_L|[FCU]|
|EFIS_320_R|[FCU]|


