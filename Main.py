from functions_hems import *
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import pandas as pd 
import os
from time import time, sleep
import numpy as np
import logging

### I am trying GitHUB


#---------------------------------- Initialisation of charging stations, battery and grid -----------------------------------------------------------------#

openwb = charging_station("192.168.4.1", 1, 11, 0, 0, 0, False, False, 0, 0, 0, False) # (ip, unit_id, max_charge_power, e_demand, e_max_demand, charge_duration, charge_priority, connection_state, charging_state, charged_energy, charging_power, electricity_cheap)
#openwb = charging_station("192.168.25.10", 1, 11, 0, 0, 0, False, False, 0, 0, 0, False)
webasto = charging_station("192.168.123.123", 254, 11, 0, 0, 0, False, False, 0, 0, 0, False)
hbattery = battery (50, 200, 7, 5, False, 0) # (soc, soc_max, soc_min, max_discharge_power, priority, battery_state)
grid_priority = False

#-------------------------------- Reading the inputs from sheets ----------------------------------------------------------------------#



results_cars = number_of_cars(openwb,webasto) # (1,True,False)
print(results_cars)

pv_and_consumption = pd.read_excel(r'C:\Users\soe\Desktop\Input.xlsx') ## Reading inputs document containing 
df = pd.read_csv(r'C:\Users\soe\Desktop\Day-ahead Prices_201901010000-202001010000.csv')
newdf = pd.DataFrame(np.repeat(df.values,60,axis=0)) / 1000 * 100 + 23.37   ## Electricity price in from EUR/MWH to Cent/kWh + Sonstige Kosten  Quelle: BDEW year 2019
all_inputs = pd.concat([pv_and_consumption, newdf], axis=1)

counter = 0

for i in range(all_inputs.shape[0]):
    #sleep(60 -time() % 60)
    P_pv = all_inputs.iloc[i,1] * 36 * 0.2 / 1000 # for a PV panel with 36 m2 and 0,2 efficiency in kW
    P_house = all_inputs.iloc[i,2] * 60 # House consumption in kW
    c_elec = all_inputs.iloc[i,3]   

    results_cars_last = results_cars
    results_cars = number_of_cars(openwb,webasto) #(1, True , False) 
    openwb.connection_state = results_cars[1]
    webasto.connection_state = results_cars[2]
    

    if results_cars [0] == 0:
        
        grid_priority = 1
        charging_power_calculation(openwb, webasto, P_pv, P_house, hbattery, grid_priority)
 
    elif results_cars [0] == 1:
        if (counter == 0 or results_cars != results_cars_last):
            if (openwb.connection_state == True and webasto.connection_state == False):
                print("Please enter values for OpenWB")
                (openwb.e_demand,openwb.e_max_demand, openwb.charge_duration) = read_user_inputs()
            elif (webasto.connection_state == True and openwb.connection_state == False):
                print("Please enter values for Webasto")
                (webasto.e_demand, webasto.e_max_demand, webasto.charge_duration) = read_user_inputs()
            else:
                print('Error: One car connected but could not get values')
        else: 
            pass
        
        openwb.charging_state = ev_charging_state(openwb.charged_energy, openwb.e_demand, openwb.e_max_demand)
        webasto.charging_state = ev_charging_state(webasto.charged_energy, webasto.e_demand, webasto.e_max_demand)
        hbattery.battery_state = battery_state_home_battery(hbattery) 
        grid_priority = priority_check(openwb, webasto, hbattery, grid_priority, results_cars)
        calculated_expensiveness = electricity_price_expensiveness(c_elec,openwb, webasto, all_inputs, counter)
        openwb.electricity_cheap = calculated_expensiveness[0]
        webasto.electricity_cheap = calculated_expensiveness[1]
        charging_power_calculation(openwb, webasto, P_pv, P_house, hbattery, grid_priority)

    elif results_cars [0] == 2:
        if (counter == 0 or results_cars != results_cars_last):
            print("Please enter values for OpenWB first")
            (openwb.e_demand,openwb.e_max_demand, openwb.charge_duration) = read_user_inputs()
            print("Please enter values for Webasto now")
            (webasto.e_demand, webasto.e_max_demand, webasto.charge_duration) = read_user_inputs()
 
        else:
            pass
        
        openwb.charging_state = ev_charging_state(openwb.charged_energy, openwb.e_demand, openwb.e_max_demand)
        webasto.charging_state = ev_charging_state(webasto.charged_energy, webasto.e_demand, webasto.e_max_demand)
        hbattery.battery_state = battery_state_home_battery(hbattery)     
        grid_priority = priority_check(openwb,webasto,hbattery,results_cars, grid_priority)
        openwb.electricity_cheap = calculated_expensiveness[0]
        webasto.electricity_cheap = calculated_expensiveness[1]
        charging_power_calculation(openwb, webasto, P_pv, P_house, hbattery, grid_priority)

    else:
        print("Error, number of cars don't meet the criterias")
    
    print("OpenWB connection state is {}. Maximum charging power is {} kW . User set requested energy of {} kWh and maximum energy of {} kWh for OpenWB. Given duration for charging is {} minutes and current price is cheap: {}  " .format(openwb.connection_state, openwb.max_charge_power, openwb.e_demand, openwb.e_max_demand, openwb.charge_duration, openwb.electricity_cheap))
    print("Webasto connection state is {}. Maximum charging power is {} kW . User set requested energy of {} kWh and maximum energy of {} kWh for OpenWB. Given duration for charging is {} minutes and current price is cheap: {}  " .format(webasto.connection_state, webasto.max_charge_power, webasto.e_demand, webasto.e_max_demand, webasto.charge_duration, webasto.electricity_cheap))
    print("Solar production power is {} kW " .format(round(P_pv,2)))
    print("House energy consumption power is {} kW " .format(round(P_house,2)))
    print("Energy price is {} is Cents / kWh " .format(round(c_elec,2)))

    counter = counter + 1

   


