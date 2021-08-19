from functions_hems import *
from tabulate import tabulate
import time 

openwb = charging_station('192.168.139.1', 1, 11, 0, 0, 0, False, False, 0, 0, 0, 0, False)
webasto = charging_station('192.168.123.123', 254, 11, 0, 0, 0, False, False, 0, 0, 0, 0, False)
#results_cars = number_of_cars(openwb,webasto) 
#print(results_cars)
#alex = True 
#write_register_int(0, 112, 1, openwb.unit_id, openwb.ip) ## Setting it to Sofort - Laden
#write_register_int(1, 10151, 1, openwb.unit_id, openwb.ip)
#write_register_int(12, 10152, 1, openwb.unit_id, openwb.ip)
#write_register_unint(0, 112, 1, openwb.unit_id, openwb.ip) ## Setting it to Sofort - Laden
#write_register_unint(1, 10151, 1, openwb.unit_id, openwb.ip)
#write_register_unint(12, 10152, 1, openwb.unit_id, openwb.ip)

#write_register_int(0,112,openwb.unit_id, openwb.ip)
#write_register_unwrite_register_unint (0,112,openwb.unit_id, openwb.ip)

###########################Consecutive Reading Register Test ####################################################
#charge_point_state_webasto = read_register(1000,1,webasto.unit_id,webasto.ip)
#print(charge_point_state_webasto)
#charge_state_webasto = read_register(1004,1,webasto.unit_id,webasto.ip)
#print(charge_state_webasto)
#evse_error_code = read_register(1006,1,webasto.unit_id,webasto.ip)
#print(evse_error_code)
#max_current = read_register(1100, 1, webasto.unit_id, webasto.ip)
#print(max_current)

# When running consecutively modbus can't read registers and runs into error.
###############################################################################

########################### Consecutive Reading Register Test with breaks ##############################

#charge_point_state_webasto = read_register(1000,1,webasto.unit_id,webasto.ip)
#print(charge_point_state_webasto)
#time.sleep(15)
#charge_state_webasto = read_register(1004,1,webasto.unit_id,webasto.ip)
#print(charge_state_webasto)
#time.sleep(15)
#evse_error_code = read_register(1006,1,webasto.unit_id,webasto.ip)
#print(evse_error_code)
#time.sleep(15)
#max_current = read_register(1100, 1, webasto.unit_id, webasto.ip)
#print(max_current)
# With a given time of 20 seconds, the modbus error always gives once a correct value and twice error, regardless of the time difference
#######################################################################

################################################ Checking multiple reading with 60 seconds ################
#charge_point_state_webasto = read_register(1000,1,webasto.unit_id,webasto.ip)
#print(charge_point_state_webasto)
#time.sleep(60)
#charge_state_webasto = read_register(1004,1,webasto.unit_id,webasto.ip)
#print(charge_state_webasto)
#time.sleep(60)
#evse_error_code = read_register(1006,1,webasto.unit_id,webasto.ip)
#print(evse_error_code)
#time.sleep(60)
#max_current = read_register(1100, 1, webasto.unit_id, webasto.ip)
#print(max_current)
#time.sleep(60)
#charge_point_state_webasto = read_register(1000,1,webasto.unit_id,webasto.ip)
#print(charge_point_state_webasto)
#time.sleep(60)
#charge_state_webasto = read_register(1004,1,webasto.unit_id,webasto.ip)
#print(charge_state_webasto)
#time.sleep(60)
#evse_error_code = read_register(1006,1,webasto.unit_id,webasto.ip)
#print(evse_error_code)
#time.sleep(60)
#max_current = read_register(1100, 1, webasto.unit_id, webasto.ip)
#print(max_current)
#time.sleep(60)
#charge_point_state_webasto = read_register(1000,1,webasto.unit_id,webasto.ip)
#print(charge_point_state_webasto)
#time.sleep(60)
#charge_state_webasto = read_register(1004,1,webasto.unit_id,webasto.ip)
#print(charge_state_webasto)
#time.sleep(60)
#evse_error_code = read_register(1006,1,webasto.unit_id,webasto.ip)
#print(evse_error_code)
#time.sleep(60)
#max_current = read_register(1100, 1, webasto.unit_id, webasto.ip)
#print(max_current)
#### Modbus doesn't answer every request altough a break for one minute is given#########
####################################################################################

#charge_point_state_webasto = read_register(1000,1,webasto.unit_id,webasto.ip)
#print(charge_point_state_webasto)
#time.sleep(15)
#charge_state_webasto = read_register(1004,1,webasto.unit_id,webasto.ip)
#print(charge_state_webasto)
#time.sleep(15)
#evse_error_code = read_register(1006,1,webasto.unit_id,webasto.ip)
#print(evse_error_code)
#time.sleep(15)
#max_current = read_register(1100, 1, webasto.unit_id, webasto.ip)
#print(max_current)
#time.sleep(15)
#charge_point_state_webasto = read_register(1000,1,webasto.unit_id,webasto.ip)
#print(charge_point_state_webasto)
#time.sleep(15)
#charge_state_webasto = read_register(1004,1,webasto.unit_id,webasto.ip)
#print(charge_state_webasto)
#time.sleep(15)
#evse_error_code = read_register(1006,1,webasto.unit_id,webasto.ip)
#print(evse_error_code)
#time.sleep(15)
#max_current = read_register(1100, 1, webasto.unit_id, webasto.ip)
#print(max_current)
#time.sleep(15)
#charge_point_state_webasto = read_register(1000,1,webasto.unit_id,webasto.ip)
#print(charge_point_state_webasto)
#time.sleep(15)
#charge_state_webasto = read_register(1004,1,webasto.unit_id,webasto.ip)
#print(charge_state_webasto)
#time.sleep(15)
#evse_error_code = read_register(1006,1,webasto.unit_id,webasto.ip)
#print(evse_error_code)
#time.sleep(15)
#max_current = read_register(1100, 1, webasto.unit_id, webasto.ip)
#print(max_current)


#### Also with 15 seconds, same phenomena can be seen. 
###############################################################################

#write_register_unint(0,5004,webasto.unit_id, webasto.ip)
#k = read_register(2000,1, webasto.unit_id, webasto.ip)
#print(k)

#Webasto can be writen succesfully and charging station reacts to the set current

#############################################################

################### OpenWB reading same register wihth #########
#for i in range (0,200):
#   reg = read_register(10114,1,openwb.unit_id, openwb.ip)
#    print (reg)
#    time.sleep(60)

#OpenWB reads more stable, however it also can't read the same register every 60 seconds
############################################################################################


##################### OpenWB Try different registers #####################################
#for i in range (0,200):
#   reg = read_register(10114,1,openwb.unit_id, openwb.ip)
#   print (reg)
#   time.sleep(30)
#   reg_2 = read_register (10115,1,openwb.unit_id, openwb.ip)
#   print(reg_2)
#   time.sleep(30)
#   reg_3 = read_register (10116,1,openwb.unit_id, openwb.ip)
#   print(reg_3)
#   time.sleep(30)
#   reg_4 = read_register (10100,1,openwb.unit_id, openwb.ip)
#   print(reg_4)

# Same issue arises, modbus doesn't show any consistency with its error frequencey
#################################################################################################

########################## Writing function for OpenWB ########################
#write_register_int(0,112,openwb.unit_id, openwb.ip)

#write_register_int(8,10152,openwb.unit_id, openwb.ip)
#### With a delay of 10 seconds, OpenWB correctly 
################################################################################################


#for i in range(0,100000000):
 #   charge_point_state_webasto = read_register(1000,1,webasto.unit_id,webasto.ip)
#    print(charge_point_state_webasto)