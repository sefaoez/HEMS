from functions_hems import *
from tabulate import tabulate


openwb = charging_station("192.168.4.1", 1, 11, 0, 0, 0, False, False, 0, 0, 0, False)
alex = True 
#write_register_int(0, 112, 1, openwb.unit_id, openwb.ip) ## Setting it to Sofort - Laden
#write_register_int(1, 10151, 1, openwb.unit_id, openwb.ip)
#write_register_int(12, 10152, 1, openwb.unit_id, openwb.ip)
#write_register_unint(0, 112, 1, openwb.unit_id, openwb.ip) ## Setting it to Sofort - Laden
#write_register_unint(1, 10151, 1, openwb.unit_id, openwb.ip)
#write_register_unint(12, 10152, 1, openwb.unit_id, openwb.ip)

#write_register_int_trial(0,112,openwb.unit_id, openwb.ip)
#write_register_unwrite_register_unint_trial (0,112,openwb.unit_id, openwb.ip)

l = [["HEMS Verbindung", alex, 35], ["Ladeleistung(kw)", 90, 80]]
table = tabulate(l, headers =['Information', 'OpenWB', 'Webasto'], tablefmt='orgtbl')

print(table)