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
from tabulate import tabulate

#--------------------------------- Initialisation of charging stations, battery and grid -----------------------------------------------------------------#

openwb = charging_station('192.168.139.1', 1, 8, 0, 0, 0, False, False, 0, 0, 0, 0, False) 
webasto = charging_station('192.168.123.123', 254, 8, 0, 0, 0, False, False, 0, 0, 0, 0, False)
hbattery = battery (100, 200, 7, 6, False, 0, 0) 
grid_priority = False

#----------------------------------- Reading the inputs from sheets ----------------------------------------------------------------------#


pv_and_consumption = pd.read_excel(r'C:\Users\soe\Desktop\Input.xlsx') ## Reading inputs document containing solar production and household consumption
df = pd.read_csv(r'C:\Users\soe\Desktop\Day-ahead Prices_201901010000-202001010000.csv') # Reading electricity prices
newdf = pd.DataFrame(np.repeat(df.values,60,axis=0)) / 1000 * 100 + 23.37   ## Electricity price in from EUR/MWH to Cent/kWh + Other costs such as grid fees  Source: BDEW year 2019
all_inputs = pd.concat([pv_and_consumption, newdf], axis=1) #Concating all inputs into one dataframe

#----------------------------------------------------------------------------------------------------------------------------------------------#

counter = 0
total_charging_cost = 0 
total_charging_profit = 0
results_cars = number_of_cars(openwb,webasto)

for i in range(all_inputs.shape[0]):
   
    P_pv = all_inputs.iloc[i,1] * 36 * 0.2 / 1000 # Solar prodcution with a PV panel with 36 m2 and 0,2 efficiency in kW
    P_house = all_inputs.iloc[i,2] * 60 # Household energy consumption in kW
    c_elec = all_inputs.iloc[i,3] 
    results_cars_last = results_cars
    results_cars = number_of_cars(openwb,webasto)  
    openwb.connection_state = results_cars[1]
    webasto.connection_state = results_cars[2]
    
    if results_cars [0] == 0:
        
        hbattery.battery_state = battery_state_home_battery(hbattery) 
        grid_priority = priority_check(openwb, webasto, hbattery, grid_priority, results_cars)
        calculated_expensiveness = (0,0,0,0)
        calculated_power_values = charging_power_calculation(openwb, webasto, P_pv, P_house, hbattery, grid_priority,c_elec)
 
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
        calculated_power_values = charging_power_calculation(openwb, webasto, P_pv, P_house, hbattery, grid_priority,c_elec)

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
        grid_priority = priority_check(openwb, webasto, hbattery, grid_priority, results_cars)
        calculated_expensiveness = electricity_price_expensiveness(c_elec,openwb, webasto, all_inputs, counter)
        openwb.electricity_cheap = calculated_expensiveness[0]
        webasto.electricity_cheap = calculated_expensiveness[1]
        calculated_power_values = charging_power_calculation(openwb, webasto, P_pv, P_house, hbattery, grid_priority,c_elec)

    else:
        print("Error, number of cars don't meet the criterias")
  
    charging_cost = calculated_power_values[1] * c_elec / 6000
    charging_profit = calculated_power_values[3] / 6000 - charging_cost  
    total_charging_cost = total_charging_cost + charging_cost
    total_charging_profit = total_charging_profit + charging_profit   
   
    l = [["HEMS Verbindung", results_cars[3], results_cars[4]], 
         ["Auto - Angeschlossen", openwb.connection_state, webasto.connection_state], 
         ["Ladeprioritaet", openwb.charge_priority, webasto.charge_priority], 
         ["Ladeleistung [kW]", openwb.charging_power, webasto.charging_power], 
         ["PV - Strom Anteil [%]", (openwb.pv_elec / openwb.charging_power) * 100 if openwb.charging_power !=0 else 0, (webasto.pv_elec / webasto.charging_power) if webasto.charging_power !=0 else 0],
         ["Rest - Zeit [m]", openwb.charge_duration - counter if openwb.charge_duration != 0 else 0, webasto.charge_duration - counter if webasto.charge_duration != 0 else 0],
         ["Durchschnittpreis Strom [c./ kWh]", calculated_expensiveness[2], calculated_expensiveness[3]],
         ["Gefragte Energiemenge [kWh]", openwb.e_demand, webasto.e_demand],
         ["Gefragte maximale Energiemenge [kWh]", openwb.e_max_demand, webasto.e_max_demand],
         ["Ladezustand (Maximale Energie) [%]", (openwb.charged_energy / openwb.e_max_demand) * 100 if openwb.e_max_demand != 0 else 0, (webasto.charged_energy / webasto.e_max_demand) if webasto.e_max_demand != 0 else 0 ]]
   
    table_charge_stations = tabulate(l, headers =['Ladestationen', 'OpenWB', 'Webasto'], tablefmt='orgtbl')
       
    m = [["Aktueller Strompreis [c./ kWh]", round(c_elec,2)],
         ["Aktuelle Stromnetzverwendung [kW]", round(calculated_power_values[0],2)],
         ["Aktuelle Stromnetzverwendung für Laden [kW]", round(calculated_power_values[1],2)],
         ["Aktuelle Ladekosten [€] ", round(charging_cost,2)],
         ["Aktueller Gewinn durch HEMS [€]", round(charging_profit,2)],
         ["Gesamte Ladekosten [€]", round(total_charging_cost,2)],
         ["Gesamter Gewinn durch HEMS [€]", round(total_charging_profit,2)]]
         
    table_balance_sheet = tabulate(m, headers =['Bilanz', 'Wert'], tablefmt='orgtbl')
 
    n = [["PV Energie Erzeugung [kW]", round(P_pv,2)],
         ["Haushalt Stromverbrauch [kW]", round(P_house,2)],
         ["Heimspeicher Leistung [kW]", round(hbattery.used_power,2)],
         ["Heimspeicher Ladezustand [%]", round(hbattery.soc / hbattery.soc_max,2) * 100]]
         
    table_house = tabulate(n, headers =['Haus', 'Wert'], tablefmt='orgtbl')    
    
    print("---------------------------------------------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------------------------------------------")
    print(table_charge_stations)
    print("---------------------------------------------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------------------------------------------")
    print(table_balance_sheet)
    print("---------------------------------------------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------------------------------------------")
    print(table_house)
    print("---------------------------------------------------------------------------------------------------------------------------")
    print("---------------------------------------------------------------------------------------------------------------------------")
    
    counter = counter + 1
    sleep(60 -time() % 60) 

   


