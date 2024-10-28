-- Wireshark Dissector for Winwing-FCU protocol
-- Tested with Wireshark 4.4
--
-- Place it in ~/.local/lib/wireshark/plugins/
--
-- Alternatively start with: wireshark -X lua_script:path/to/wireshark_winwing_dissector.lua


-- Symbols
local IF_CLASS_UNKNOWN          = 0xFFFF
local HID                       = 0x0003

usb_winwing_protocol = Proto("USB_Winwing",  "USB winwing protocol")

local header   = ProtoField.uint16("fcu.header",   "Header",   base.HEX)
local pkg_number = ProtoField.uint8 ("fcu.pkg_number", "Packet Number", base.DEC)
local unknown1 = ProtoField.uint32 ("fcu.unknown1", "unknown1", base.HEX)
local unknown2 = ProtoField.uint8 ("fcu.unknown2", "unknown2", base.HEX)
local cmd1 = ProtoField.uint8 ("fcu.cmd1", "command 1", base.HEX)
local alwaysone = ProtoField.uint8 ("fcu.alwaysone", "always one", base.HEX)
local unknown3 = ProtoField.uint16 ("fcu.unknown3", "unknown3", base.HEX)
local chksum = ProtoField.uint16 ("fcu.chksum", "Checksum", base.HEX)
local unknown4 = ProtoField.uint16 ("fcu.unknown4", "unknown4", base.HEX)
local unknown5 = ProtoField.uint16 ("fcu.unknown5", "unknown5", base.HEX)
local cmd2 = ProtoField.uint8 ("fcu.cmd2", "command 2", base.HEX)
local alwayszero = ProtoField.uint8 ("fcu.alwayszero", "always zero", base.HEX)
local s2 = ProtoField.uint8 ("fcu.s2", "lcd speed segment 2", base.HEX)
local s1 = ProtoField.uint8 ("fcu.s1", "lcd speed segment 1", base.HEX)
local s0 = ProtoField.uint8 ("fcu.s0", "lcd speed segment 0", base.HEX)
local h3 = ProtoField.uint8 ("fcu.h3", "lcd heading segment 3 + SPD, MACH Flag", base.HEX)
local h2 = ProtoField.uint8 ("fcu.h2", "lcd heading segment 3,2", base.HEX)
local h1 = ProtoField.uint8 ("fcu.h1", "lcd heading segment 2,1", base.HEX)
local h0 = ProtoField.uint8 ("fcu.h0", "lcd heading segment 1,0 + LAT, HDG Flag, HDG MANAGED", base.HEX)
local a5 = ProtoField.uint8 ("fcu.a5", "lcd altitude segment 5 + HDG, TRK, V/S, FPA", base.HEX)
local a4 = ProtoField.uint8 ("fcu.a4", "lcd altitude segment 5,4, FPA", base.HEX)
local a3 = ProtoField.uint8 ("fcu.a3", "lcd altitude segment 4,3", base.HEX)
local a2 = ProtoField.uint8 ("fcu.a2", "lcd altitude segment 3,2", base.HEX)
local a1 = ProtoField.uint8 ("fcu.a1", "lcd altitude segment 2,1", base.HEX)
local a0 = ProtoField.uint8 ("fcu.a0", "lcd altitude segment 1,0 + V/S MINUS + lcd v/s seg4", base.HEX)
local v3 = ProtoField.uint8 ("fcu.v4", "lcd v/s segment 3,2 + seg4 dot", base.HEX)
local v2 = ProtoField.uint8 ("fcu.v3", "lcd v/s segment 2,1", base.HEX)
local v1 = ProtoField.uint8 ("fcu.v2", "lcd v/s segment 1,0", base.HEX)
local v0 = ProtoField.uint8 ("fcu.v1", "lcd v/s segment 0 + V/S FPA FLAG", base.HEX)
local res0 = ProtoField.uint8 ("fcu.res0", "lcd res0 ?", base.HEX)
local res1 = ProtoField.uint8 ("fcu.res1", "lcd res1 ?", base.HEX)
local res2 = ProtoField.uint8 ("fcu.res2", "lcd res2 ?", base.HEX)

usb_winwing_protocol.fields = { header, pkg_number, unknown1, unknown2, cmd1, alwaysone, unknown3, chksum, unknown4, unknown5, cmd2, alwayszero, s2, s1, s0, h3, h2, h1, h0, a5, a4, a3, a2, a1, a0, v3, v2, v1, v0, res0, res1, res2 }

function usb_winwing_protocol.dissector(buffer, pinfo, tree)
  length = buffer:len()
  if length == 0 then return end

  pinfo.cols.protocol = usb_winwing_protocol.name

  local subtree = tree:add(usb_winwing_protocol, buffer(), "USB Winwing FCU Data")

  subtree:add_le(header,   buffer(0,2))
  subtree:add_le(pkg_number, buffer(2,1))
  subtree:add_le(unknown1, buffer(3,4))
  subtree:add_le(unknown2, buffer(7,1))
  subtree:add_le(cmd1, buffer(8,1))
  subtree:add_le(alwaysone, buffer(9,1))
  subtree:add_le(unknown3, buffer(10,2))
  subtree:add_le(chksum, buffer(12,2))
  subtree:add_le(unknown4, buffer(14,1))
  subtree:add_le(unknown5, buffer(15,2))
  subtree:add_le(cmd2, buffer(17,1))
  subtree:add_le(alwayszero, buffer(18,1))
  subtree:add_le(alwayszero, buffer(19,1))
  subtree:add_le(alwayszero, buffer(20,1))
  subtree:add_le(alwayszero, buffer(21,1))
  subtree:add_le(alwayszero, buffer(22,1))
  subtree:add_le(alwayszero, buffer(23,1))
  subtree:add_le(alwayszero, buffer(24,1))
  subtree:add_le(s2, buffer(25,1))
  subtree:add_le(s1, buffer(26,1))
  subtree:add_le(s1, buffer(27,1))
  subtree:add_le(h3, buffer(28,1))
  subtree:add_le(h2, buffer(29,1))
  subtree:add_le(h1, buffer(30,1))
  subtree:add_le(h0, buffer(31,1))
  subtree:add_le(a5, buffer(32,1))
  subtree:add_le(a4, buffer(33,1))
  subtree:add_le(a3, buffer(34,1))
  subtree:add_le(a2, buffer(35,1))
  subtree:add_le(a1, buffer(36,1))
  subtree:add_le(a0, buffer(37,1))
  subtree:add_le(v3, buffer(38,1))
  subtree:add_le(v2, buffer(39,1))
  subtree:add_le(v1, buffer(40,1))
  subtree:add_le(v0, buffer(41,1))
  subtree:add_le(res0, buffer(42,1))
  subtree:add_le(res1, buffer(43,1))
  subtree:add_le(res2, buffer(44,1))
end

---DissectorTable.get("usb.interrupt"):add(7777, usb_winwing_protocol)
DissectorTable.get("usb.interrupt"):add(HID, usb_winwing_protocol)
DissectorTable.get("usb.control"):add(HID, usb_winwing_protocol)
