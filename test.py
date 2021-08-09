from functions_hems import *

openwb = charging_station("192.168.4.1", 1, 11, 0, 0, 0, False, False, 0, 0, 0, False)
write_register_int(0, 112, 1, openwb.unit_id, openwb.ip) ## Setting it to Sofort - Laden
write_register_int(1, 10151, 1, openwb.unit_id, openwb.ip)

write_register_int(12, 10152, 1, openwb.unit_id, openwb.ip)


