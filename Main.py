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
import pymysql

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
   
    ########################################################################################################################
    # Sefa's variable calculations ################
    pv_elec_slice_openwb = (openwb.pv_elec / openwb.charging_power) * 100 if openwb.charging_power !=0 else 0
    pv_elec_slice_webasto = (webasto.pv_elec / webasto.charging_power) if webasto.charging_power !=0 else 0
    residual_time_openwb = openwb.charge_duration - counter if openwb.charge_duration != 0 else 0
    residual_time_webasto = webasto.charge_duration - counter if webasto.charge_duration != 0 else 0
    c_elec_frame_openwb = calculated_expensiveness[2]
    c_elec_frame_webasto = calculated_expensiveness[3]
    charging_level_openwb = (openwb.charged_energy / openwb.e_max_demand) * 100 if openwb.e_max_demand != 0 else 0
    charging_level_webasto = (webasto.charged_energy / webasto.e_max_demand) if webasto.e_max_demand != 0 else 0
    c_elec_rounded = round(c_elec,2)
    grid_usage = round(calculated_power_values[0])
    grid_usage_for_charging = round(calculated_power_values[1])
    charging_cost_rounded = round(charging_cost,2)
    charging_profit_rounded = round(charging_profit,2)
    total_charging_cost_rounded = round(total_charging_cost,2)
    total_charging_profit_rounded = round(total_charging_profit,2)
    P_pv_rounded = round(P_pv,2)
    P_house_rounded = round(P_house,2)
    used_battery = round(hbattery.used_power,2)
    battery_soc = round(hbattery.soc / hbattery.soc_max,2) * 100

    ############################################# Addition for User Interface #############################

    #database connection
    connection = pymysql.connect(host="localhost", user="root", passwd="", database="test")
    cursor = connection.cursor()
    # Query for creating table
    HEMSTableSql = """CREATE TABLE HEMS_values(
    ID INT(20) PRIMARY KEY AUTO_INCREMENT,
    VARIABLENAME varchar(50),
    VARIABLEVALUE numeric(9,2),
    VARIABLEUNIT varchar(50)
    )"""

    cursor.execute(HEMSTableSql)
    connection.close()
    
    
    hems_verbindung1 = 1 # Intentioanlly set hard-coded, will be changed
    hems_verbindung2 = 1 # Intentionally set hard-coded, will be changed 
    openwb_connection_state = openwb.connection_state
    webasto_connection_state = webasto.connection_state
    openwb_charge_priority = openwb.charge_priority
    webasto_charge_priority = webasto.charge_priority
    openwb_charging_power = openwb.charging_power
    webasto_charging_power = webasto.charging_power
    pv_energy_share_webasto = pv_elec_slice_webasto
    pv_energy_share_openwb = pv_elec_slice_openwb
    remaining_time_webasto = residual_time_webasto
    remaining_time_openwb = residual_time_openwb
    demand_energy_openwb = openwb.e_demand
    demand_energy_webasto = webasto.e_demand
    charging_state_openwb = charging_level_openwb
    charging_state_webasto = charging_level_webasto
    Strompreis_aktuell = c_elec_rounded
    Stromnetzverwendung_aktuell = grid_usage
    StromnetzverwendungLaden_aktuell = grid_usage_for_charging
    Ladekosten_aktuell = charging_cost_rounded
    Gewinn_HEMS = charging_profit_rounded
    Gewinn_HEMS_gesamt = total_charging_profit_rounded
    ErzeugungPV_Energie = P_pv_rounded
    Haushalt_Stromverbrauch = P_house_rounded
    Heimspeicher_Leistung = used_battery
    Heimspeicher_Ladezustand = battery_soc

    #database connection
    connection = pymysql.connect(host="localhost", user="root", passwd="", database="test")
    cursor = connection.cursor()

    #executing the queries for inserting values
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('1', 'hems_verbindung1', %s, '-' ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(hems_verbindung1, hems_verbindung1))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('2','hems_verbindung2', %s, '-')ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(hems_verbindung2, hems_verbindung2))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('3','openwb_connection_state', %s, '-'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(openwb_connection_state, openwb_connection_state))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('4','webasto_connection_state', %s, '-'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(webasto_connection_state, webasto_connection_state))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('5','openwb_charge_priority', %s, '-'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(openwb_charge_priority, openwb_charge_priority))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('6','webasto_charge_priority', %s, '-'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(webasto_charge_priority,webasto_charge_priority ))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('7','openwb_charging_power', %s, 'kW'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(openwb_charging_power,openwb_charging_power ))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('8','webasto_charging_power', %s, 'kW'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(webasto_charging_power,webasto_charging_power ))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('9','pv_energy_share_webasto', %s, '%'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(pv_energy_share_webasto, pv_energy_share_webasto))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('10','pv_energy_share_openwb', %s, '%'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(pv_energy_share_openwb, pv_energy_share_openwb))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('11','remaining_time_webasto', %s, 'min'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(remaining_time_webasto, remaining_time_webasto))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('12','remaining_time_openwb', %s, 'min'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(remaining_time_openwb, remaining_time_openwb))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('13','demand_energy_openwb', %s, 'kW'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(demand_energy_openwb, demand_energy_openwb))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('14','demand_energy_webasto', %s, 'kW'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(demand_energy_webasto, demand_energy_webasto))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('15','charging_state_openwb', %s, '%'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(charging_state_openwb, charging_state_openwb))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('16','charging_state_webasto', %s, '%'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(charging_state_webasto, charging_state_webasto))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('17','Strompreis_aktuell', %s, 'EUR'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(Strompreis_aktuell, Strompreis_aktuell))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('18','Stromnetzverwendung_aktuell', %s, 'kW'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(Stromnetzverwendung_aktuell, Stromnetzverwendung_aktuell))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('19','StromnetzverwendungLaden_aktuell', %s, 'kW'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(StromnetzverwendungLaden_aktuell, StromnetzverwendungLaden_aktuell))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('20','Ladekosten_aktuell', %s, 'EUR'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(Ladekosten_aktuell, Ladekosten_aktuell))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('21','Gewinn_HEMS', %s, 'EUR'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(Gewinn_HEMS, Gewinn_HEMS))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('22','Gewinn_HEMS_gesamt', %s, 'EUR'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(Gewinn_HEMS_gesamt, Gewinn_HEMS_gesamt))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('23','ErzeugungPV_Energie', %s, 'kW'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(ErzeugungPV_Energie, ErzeugungPV_Energie))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('24','Haushalt_Stromverbrauch', %s, 'kW'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(Haushalt_Stromverbrauch, Haushalt_Stromverbrauch))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('25','Heimspeicher_Leistung', %s, 'kW'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(Heimspeicher_Leistung, Heimspeicher_Leistung))
    cursor.execute("""INSERT INTO HEMS_values(id, VARIABLENAME, VARIABLEVALUE, VARIABLEUNIT) VALUES('26','Heimspeicher_Ladezustand', %s, '%'  ) ON DUPLICATE KEY UPDATE VARIABLEVALUE=%s""",(Heimspeicher_Ladezustand, Heimspeicher_Ladezustand))

    #commiting the connection then closing it.
    connection.commit()
    connection.close()

    
    counter = counter + 1
    sleep(60 -time() % 60) 

   


