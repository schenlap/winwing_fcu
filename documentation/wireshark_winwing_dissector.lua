 
winwing_protocol = Proto("USB Winwing",  "USB winwing protocol")

local buttons   = ProtoField.uint8("usb_mouse.buttons",   "Buttons",   base.DEC)
local scrolling = ProtoField.int8 ("usb_mouse.scrolling", "Scrolling", base.DEC)

usb_mouse_protocol.fields = { buttons, scrolling }

function usb_mouse_protocol.dissector(buffer, pinfo, tree)
  length = buffer:len()
  if length == 0 then return end

  pinfo.cols.protocol = usb_mouse_protocol.name

  local subtree = tree:add(usb_mouse_protocol, buffer(), "USB Mouse Data")

  subtree:add_le(buttons,   buffer(0,1))
  subtree:add_le(scrolling, buffer(3,1))
end

DissectorTable.get("usb.interrupt"):add(0xffff, usb_mouse_protocol)
