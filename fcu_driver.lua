require("bit")

function find_fcu()
    if (FCU ~= nil) then
        return ;
    end
    for i = 1,NUMBER_OF_HID_DEVICES do
        local device = ALL_HID_DEVICES[i]
        if ((device.vendor_id == 16536) and (device.product_id == 47888) )
        then
            logMsg("found fcu device "..device.product_string)
            FCU = hid_open(device.vendor_id, device.product_id)
            break
        end
    end
    if FCU == nil
    then
        logMsg("fcu device not found")
    end
    lcd_init()
end


function lcd_init()
    if FCU == nil then
        return
    end
    hid_write(FCU, 0, 0xf0, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)
    logMsg("init lcd")
end

--register event from xp
dataref("autopilot_spd", "sim/cockpit2/autopilot/airspeed_dial_kts_mach", "readonly")
dataref("autopilot_spd_is_mach" ,"sim/cockpit/autopilot/airspeed_is_mach", "readonly")
dataref("autopilot_hdg_mag", "sim/cockpit/autopilot/heading_mag", "readonly")
dataref("autopilot_alt", "sim/cockpit/autopilot/altitude", "readonly")
dataref("autopilot_vs", "sim/cockpit/autopilot/vertical_velocity", "readonly")
dataref("autopilot_fpa", "sim/cockpit2/autopilot/fpa", "readonly")
dataref("autopilot_ap1", "sim/cockpit2/autopilot/servos_on", "readonly")
dataref("autopilot_ap2", "sim/cockpit2/autopilot/servos2_on", "readonly")
dataref("autopilot_athr","sim/cockpit2/autopilot/autothrottle_arm", "readonly")
dataref("autopilot_appr", "sim/cockpit2/autopilot/approach_status", "readonly")
dataref("autopilot_loc", "sim/cockpit2/autopilot/nav_status", "readonly")
dataref("autopilot_spd_window","sim/cockpit2/autopilot/vnav_speed_window_open", "readonly")
dataref("autopilot_fpa_window", "laminar/A333/autopilot/vvi_fpa_window_open", "readonly")
dataref("autopilot_hdg_window", "laminar/A333/autopilot/hdg_window_open", "readonly")
dataref("autopilot_trkfpa", "sim/cockpit2/autopilot/trk_fpa", "readonly")
dataref("autopilot_alt_mode","laminar/A333/annun/autopilot/alt_mode", "readonly") --annun means annunciator 


--define button 
button_list = {}
button_list["MACH"] = {id=0,name="MACH",dataref="sim/autopilot/knots_mach_toggle"}
button_list["LOC"] = {id=1,name="LOC",dataref="sim/autopilot/NAV"}
button_list["TRK"] = {id=2,name="TRK",dataref="sim/autopilot/trkfpa"}
button_list["AP1"] = {id=3,name="AP1",dataref="sim/autopilot/servos_toggle"}
button_list["AP2"] = {id=4,name="AP2",dataref="sim/autopilot/servos2_toggle"}
button_list["A_THR"] = {id=5,name="A/THR",dataref="laminar/A333/autopilot/a_thr_toggle"}
button_list["EXPED"] = {id=6,name="EXPED",dataref="sim/autopilot/altitude_hold"}
button_list["METRIC"] = {id=7,name="METRIC",dataref="laminar/A333/autopilot/metric_alt_push"}
button_list["APPR"] = {id=8,name="APPR",dataref="sim/autopilot/approach"}
button_list["SPD_DEC"] = {id=9,name="SPD DEC",dataref="sim/autopilot/airspeed_down"}
button_list["SPD_INC"] = {id=10,name="SPD INC",dataref="sim/autopilot/airspeed_up"}
button_list["SPD_PUSH"] = {id=11,name="SPD PUSH",dataref="laminar/A333/autopilot/speed_knob_push"}
button_list["SPD_PULL"] = {id=12,name="SPD PULL",dataref="laminar/A333/autopilot/speed_knob_pull"}
button_list["HDG_DEC"] = {id=13,name="HDG DEC",dataref="sim/autopilot/heading_down"}
button_list["HDG_INC"] = {id=14,name="HDG INC",dataref="sim/autopilot/heading_up"}
button_list["HDG_PUSH"] = {id=15,name="HDG PUSH",dataref="laminar/A333/autopilot/heading_knob_push"}
button_list["HDG_PULL"] = {id=16,name="HDG PULL",dataref="laminar/A333/autopilot/heading_knob_pull"}
button_list["ALT_DEC"] = {id=17,name="ALT DEC",dataref="sim/autopilot/altitude_down"}
button_list["ALT_INC"] = {id=18,name="ALT INC",dataref="sim/autopilot/altitude_up"}
button_list["ALT_PUSH"] = {id=19,name="ALT PUSH",dataref="laminar/A333/autopilot/altitude_knob_push"}
button_list["ALT_PULL"] = {id=20,name="ALT PULL",dataref="laminar/A333/autopilot/altitude_knob_pull"}
button_list["VS_DEC"] = {id=21,name="VS DEC",dataref="sim/autopilot/vertical_speed_down"}
button_list["VS_INC"] = {id=22,name="VS INC",dataref="sim/autopilot/vertical_speed_up"}
button_list["VS_PUSH"] = {id=23,name="VS PUSH",dataref="laminar/A333/autopilot/vertical_knob_push"}
button_list["VS_PULL"] = {id=24,name="VS PULL",dataref="laminar/A333/autopilot/vertical_knob_pull"}
button_list["ALT100"] = {id=25,name="ALT100",dataref="laminar/A333/autopilot/alt_step_left"}
button_list["ALT1000"] = {id=26,name="ALT1000",dataref="laminar/A333/autopilot/alt_step_right"}

cache_data={}
cache_data["autopilot_spd"] = 0
cache_data["autopilot_spd_is_mach"] = 0
cache_data["autopilot_hdg_mag"] = 0
cache_data["autopilot_alt"] = 0
cache_data["autopilot_vs"] = 0
cache_data["autopilot_fpa"] = 0
cache_data["autopilot_ap1"] = 0
cache_data["autopilot_ap2"] = 0
cache_data["autopilot_athr"] = 0
cache_data["autopilot_appr"] = 0
cache_data["autopilot_loc"] = 0
cache_data["autopilot_spd_window"] = 0
cache_data["autopilot_fpa_window"] = 0
cache_data["autopilot_hdg_window"] = 0
cache_data["autopilot_trkfpa"] = 0
cache_data["autopilot_alt_mode"] = 0 

--define led 
led_list = {
    {id = 0,  bind="", val = 0}, --led backlight
    {id = 1,  bind="", val = 0}, --lcd backlight
    {id = 3,  bind="autopilot_loc", val = 0},
    {id = 5,  bind="autopilot_ap1", val = 0},
    {id = 7,  bind="autopilot_ap2", val = 0},
    {id = 9,  bind="autopilot_athr", val = 0},
    {id = 11, bind="autopilot_alt_mode", val = 0},
    {id = 13, bind="autopilot_appr", val = 0},
    {id = 17, bind="", val = 0},
    {id = 30, bind="", val = 0},
}

--define lcd
lcd_flags = {}
lcd_flags["spd"] = {byte = 1, mask = 0x08, value = 1}
lcd_flags["mach"] = {byte = 1, mask = 0x04, value = 0}
lcd_flags["hdg"] = {byte = 0, mask = 0x80, value = 0}
lcd_flags["trk"] = {byte = 0, mask = 0x40, value = 0}
lcd_flags["lat"] = {byte = 0, mask = 0x20, value = 1}
lcd_flags["vshdg"] = {byte = 7, mask = 0x08, value = 1}
lcd_flags["vs"] = {byte = 7, mask = 0x04, value = 1}
lcd_flags["ftrk"] = {byte = 7, mask = 0x02, value = 0}
lcd_flags["ffpa"] = {byte = 7, mask = 0x01, value = 0}
lcd_flags["alt"] = {byte = 6, mask = 0x10, value = 1}
lcd_flags["hdg_managed"] = {byte = 0, mask = 0x10, value = 0}
lcd_flags["spd_managed"] = {byte = 1, mask = 0x02, value = 0}
lcd_flags["alt_managed"] = {byte = 11, mask = 0x10, value = 0}
lcd_flags["vs_horz"] = {byte = 2, mask = 0x10, value = 1}
lcd_flags["vs_vert"] = {byte = 8, mask = 0x10, value = 0}
lcd_flags["lvl"] = {byte = 4, mask = 0x10, value = 1}
lcd_flags["lvl_left"] = {byte = 5, mask = 0x10, value = 1}
lcd_flags["lvl_right"] = {byte = 3, mask = 0x10, value = 1}
lcd_flags["fvs"] = {byte = 10, mask = 0x40, value = 1}
lcd_flags["ffpa2"] = {byte = 10, mask = 0x80, value = 0}
lcd_flags["fpa_comma"] = {byte = 9, mask = 0x10, value = 0}
lcd_flags["mach_comma"] = {byte = 12, mask = 0x01, value = 0}

button_press_event_list = {}

last_event_bit = 0

function on_button_event()
    if FCU == nil then
        return
    end
    local data_in = {hid_read_timeout(FCU, 42, 10)}
    local n = data_in[1] -- index start from 1.....
    if (n ~= 41)
    then
        --logMsg("invalid input data len skip "..n)
        return
    end

    local event_bit = 0
    for i = 3,6 do
        event_bit = event_bit+data_in[i]*2^((i-3)*8)
    end

    if (event_bit == last_event_bit) then
        return
    end

    local button = {}
    for index = 0,32 do
        local mask = 2^index
        local bit = math.floor(event_bit/mask)
        local bit_last = math.floor(last_event_bit/mask)
        if (bit ~= bit_last) then
            if (bit % 2 == 1) then
                local id = index+1
                button_press_event_list[index]=1
            end
        end
    end
    last_event_bit = event_bit

    --send cmd 
    for _, info  in pairs(button_list) do
        local id = info.id
        if ( button_press_event_list[id] == 1 ) then
            button_press_event_list[id] = 0
            logMsg("CMD "..info.dataref.." index"..id)
            command_once(info.dataref)
        end
    end


end

function config_led(led)
    if (led.bind ~= "") then
        local val,_= loadstring("return "..led.bind)
        local flag = val()
        if (flag ~= led.val) then
            logMsg("set led "..led.id.." "..flag)
            hid_write(FCU, 0, 0x02, 0x10, 0xbb, 0 , 0, 3, 0x49, led.id, flag, 0, 0, 0, 0, 0)
            led.val = flag
        end
    end
end


function set_led()
    for i, led in pairs(led_list) do
        config_led(led)
    end
end

--      A
--      ---
--   F | G | B
--      ---
--   E |   | C
--      ---
--       D
-- A=0x80, B=0x40, C=0x20, D=0x10, E=0x02, F=0x08, G=0x04
lcd_mapping = {}
lcd_mapping['0'] = 0xfa
lcd_mapping['1'] = 0x60
lcd_mapping['2'] = 0xd6
lcd_mapping['3'] = 0xf4
lcd_mapping['4'] = 0x6c
lcd_mapping['5'] = 0xbc
lcd_mapping['6'] = 0xbe
lcd_mapping['7'] = 0xe0
lcd_mapping['8'] = 0xfe
lcd_mapping['9'] = 0xfc
lcd_mapping['A'] = 0xee
lcd_mapping['B'] = 0xfe
lcd_mapping['C'] = 0x9a
lcd_mapping['D'] = 0x76
lcd_mapping['E'] = 0x9e
lcd_mapping['F'] = 0x8e
lcd_mapping['G'] = 0xbe
lcd_mapping['H'] = 0x6e
lcd_mapping['I'] = 0x60
lcd_mapping['J'] = 0x70
lcd_mapping['K'] = 0x0e
lcd_mapping['L'] = 0x1a
lcd_mapping['M'] = 0xa6
lcd_mapping['N'] = 0x26
lcd_mapping['O'] = 0xfa
lcd_mapping['P'] = 0xce
lcd_mapping['Q'] = 0xec
lcd_mapping['R'] = 0x06
lcd_mapping['S'] = 0xbc
lcd_mapping['T'] = 0x1e
lcd_mapping['U'] = 0x7a
lcd_mapping['V'] = 0x32
lcd_mapping['W'] = 0x58
lcd_mapping['X'] = 0x6e
lcd_mapping['Y'] = 0x7c
lcd_mapping['Z'] = 0xd6
lcd_mapping['-'] = 0x04
lcd_mapping['#'] = 0x36
lcd_mapping['/'] = 0x60
lcd_mapping['\\'] = 0xa
lcd_mapping[' ']  = 0x0

function swap_nibble(c)
    local high = math.floor(c/16)
    local low = c%16
    return low * 16 + high
end

function data_from_string(l, input, swap)
    local digit = {}
    local str = string.upper(input)
    for i = 0,l do
        digit[l-1-i] = lcd_mapping[string.sub(str,i+1,i+1)]
    end
    if swap ~= true then
        return digit
    end

    digit[l] = 0

    for i  = 0, l do
        digit[i] = swap_nibble(digit[i])
    end

    for i = 0,l - 1 do
        digit[l-i] = digit[l - i]%16 +  math.floor(digit[l-1-i]/16) * 16
        digit[l-1-i] = digit[l-1-i]%16
    end

    return digit
end

function fix_str_len(input, len)
    if type(input) == "string" then
        return string.format("%"..len.."s", input)
    end
    return string.format('%0'..len.."d", input)
end


function ljust(str, width, fillchar)
    fillchar = fillchar or " "
    local padding = width - #str
    if padding <= 0 then
        return str
    end
    return str .. string.rep(fillchar, padding)
end

function rjust(str, width, fillchar)
    fillchar = fillchar or " "
    local padding = width - #str
    if padding <= 0 then
        return str
    end
    return string.rep(fillchar, padding) .. str
end

function draw_lcd(spd, hdg, alt, vs)
    local s = data_from_string(3, spd)
    local h = data_from_string(3, hdg, true)
    local a = data_from_string(5, alt, true)
    local v = data_from_string(4, vs, true)


    local bl = {}
    for _, flag in pairs(lcd_flags) do
        if bl[flag.byte] == nil then
            bl[flag.byte] = 0
        end
        bl[flag.byte] = bit.bor(bl[flag.byte] ,(flag.mask *flag.value))
    end

    local pkg_nr = 1
    hid_write(FCU, 0, 0xf0, 0x0, pkg_nr, 0x31, 0x10, 0xbb, 0x0, 0x0, 0x2, 0x1, 0x0, 0x0, 0xff, 0xff, 0x2, 0x0, 0x0, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                bit.bor(s[2],bl[12]), s[1],
                s[0], bit.bor(h[3] , bl[1]),
                h[2], h[1], bit.bor(h[0] , bl[0]),  bit.bor(a[5] , bl[7]),
                bit.bor(a[4] , bl[6]), bit.bor(a[3] , bl[5]), bit.bor(a[2] ,bl[4]), bit.bor(a[1] , bl[3]),
                bit.bor(a[0], v[4] , bl[2]),
                bit.bor(v[3],bl[9]), bit.bor(v[2],bl[8]), bit.bor(v[1],bl[11]), bit.bor(v[0],bl[10]),
                0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)


    hid_write(FCU, 0, 0xf0, 0x0, pkg_nr, 0x11, 0x10, 0xbb, 0x0, 0x0, 0x3, 0x1, 0x0, 0x0, 0xff, 0xff, 0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0)
end

exped_led_state = 0

function round(x)
    return math.floor(x+0.5)
end

function refresh_dataref()
    if FCU == nil then
        return
    end
    local need_refresh = 0
    for ref, v in pairs(cache_data) do
        local val = loadstring("return "..ref)() 
        if ref == "autopilot_spd" and val < 1 then
            val = (val+0.00005)*1000
        end
        -- could be nagetive dont plus fpa here
        if v ~=  val then
            cache_data[ref] = val 
            need_refresh  = 1
        end 
    end

    if need_refresh == 0 then
        return
    end

    local spd_is_mach = cache_data["autopilot_spd_is_mach"]
    local trkfpa = cache_data['autopilot_trkfpa']
    --spd 
    local spd = cache_data["autopilot_spd"]
    --hdg
    local hdg = round(cache_data["autopilot_hdg_mag"])
    --alt 
    local alt = cache_data["autopilot_alt"]
    --vs 
    local vs = cache_data["autopilot_vs"]
    if trkfpa == 1 then
        vs = cache_data["autopilot_fpa"]
    end
    if vs < 0 then
        vs = math.abs(vs)
        lcd_flags["vs_vert"].value = 0
    else 
        lcd_flags["vs_vert"].value = 1
    end

    lcd_flags["fpa_comma"].value = 0
    --signal flags 
    lcd_flags["spd"].value = 1-spd_is_mach
    lcd_flags["mach"].value = spd_is_mach
    lcd_flags["mach_comma"].value = spd_is_mach
    lcd_flags["hdg"].value = 1-trkfpa 
    lcd_flags["trk"].value = trkfpa 
    lcd_flags["fvs"].value = 1-trkfpa
    lcd_flags["vshdg"].value = 1-trkfpa
    lcd_flags["vs"].value = 1-trkfpa
    lcd_flags["ftrk"].value = trkfpa 
    lcd_flags["ffpa"].value = trkfpa 
    lcd_flags["ffpa2"].value = trkfpa 
    
    local str_spd = fix_str_len(spd,3)
    local str_hdg = fix_str_len(hdg,3)
    local str_alt = fix_str_len(alt,5)
    local str_vs = fix_str_len(vs,4)
    
    --manage
    lcd_flags['spd_managed'].value = 0
    lcd_flags['hdg_managed'].value = 0
    lcd_flags['alt_managed'].value = 0
    if cache_data["autopilot_spd_window"] == 0 then
        str_spd = "---"
        lcd_flags['mach_comma'].value = 0
        lcd_flags['spd_managed'].value = 1
    end
    if cache_data["autopilot_hdg_window"] == 0 then
        str_hdg = "---"
        lcd_flags['hdg_managed'].value = 1
    end
    if cache_data["autopilot_fpa_window"] == 0 then
        str_vs = "----"
        lcd_flags["vs_vert"].value  = 0
        -- more complicated should depends on autopilot_status
        lcd_flags['alt_managed'].value = 1
    elseif trkfpa == 0 then 
        str_vs = rjust(tostring(math.floor(vs/100)), 2, '0')
        str_vs = ljust(str_vs, 4, "#")
        button_list["VS_DEC"].dataref = "sim/autopilot/vertical_speed_down"
        button_list["VS_INC"].dataref = "sim/autopilot/vertical_speed_up"
    else
        vs = (vs+0.05)*10
        str_vs = rjust(tostring(math.floor(vs)), 2, '0')
        str_vs = ljust(str_vs, 4, " ")
        logMsg("1 "..str_vs.." "..vs)
        lcd_flags["fpa_comma"].value = 1
        button_list["VS_DEC"].dataref = "laminar/A333/autopilot/fpa_decrease" 
        button_list["VS_INC"].dataref = "laminar/A333/autopilot/fpa_increase"
    end

    draw_lcd(str_spd, str_hdg, str_alt, str_vs)
    set_led()
end

do_often(find_fcu())
do_every_frame("on_button_event()")
do_every_frame("refresh_dataref()")