from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import pandas as pd
import logging


class charging_station:
    
    #The class is created for different charging_stations. Parameters starting from e_demand until electricity_cheap should be set either to 0 or False. 
    #The IP, unit_id and max charge power can be taken from product manual.
    
    def __init__(self, ip, unit_id, max_charge_power, e_demand, e_max_demand, charge_duration, charge_priority, connection_state, charging_state, charged_energy, charging_power, pv_elec, electricity_cheap):
        self.ip = ip
        self.unit_id = unit_id
        self.max_charge_power = max_charge_power
        self.e_demand = e_demand
        self.e_max_demand = e_max_demand
        self.charge_duration = charge_duration 
        self.charge_priority = charge_priority
        self.connection_state = connection_state
        self.charging_state = charging_state # 0 when lower than requested energy, 1 when more than requested energy
        self.charged_energy = charged_energy
        self.charging_power = charging_power
        self.pv_elec = pv_elec
        self.electricity_cheap = electricity_cheap

class battery:
    
    #The class battery is used to simulate the home battery. The values can be given arbitrary. 
    
    def __init__(home, soc, soc_max, soc_min, max_discharge_power, priority, battery_state, used_power):
        home.soc = soc
        home.soc_max = soc_max
        home.soc_min = soc_min
        home.max_discharge_power = max_discharge_power
        home.priority = priority
        home.battery_state = battery_state
        home.used_power = used_power

def read_register(address, count, unit, station_ip):
    
    #This function reads the number of registers, which is equal to "count" in the "address". "Unit" and "station_ip" shall be taken from the charging station.
    #It initializes first the ModbusClient and then reads the register as long as it is possible. Later it returns also the values "decoded", which is the value in the 
    #register and "S_register_read", which gives true, if the register could be read and false, if not. "S_connection" deliver, if there has been a connection between
    #slave and client
    
    charge_station = ModbusClient(station_ip, port=502, unit_id=unit, auto_open=True, auto_close=True)
    S_connection = False
    S_register_read = False
    if (charge_station.connect() == False):
       
        decoded = 0
        
    else:     
        
        S_connection = True
        result = charge_station.read_holding_registers(address, count,  unit=unit)
        if (result.isError() == True):
            
            decoded = 0

        else:
            
            S_register_read = True
            decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            decoded = decoder.decode_16bit_uint() 
    return decoded, S_register_read, S_connection

def write_register_int(value, address, unit, station_ip):

    # This function writes the "value" in the register, which is located in the "address" for a device with unit number "unit 
    # and device ip "station_ip" as signed integer

    charge_station = ModbusClient(station_ip, port=502, unit_id=unit, auto_open=True, auto_close=True)
    
    if (charge_station.connect() == False):
        pass
    else:
        charge_station = ModbusClient(station_ip, port=502, unit_id=unit, auto_open=True, auto_close=True)
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        builder.add_16bit_int(value)		
        registers = builder.to_registers()
        charge_station.write_registers(address, registers, unit=unit)

def write_register_unint(value, address, unit, station_ip):

    # This function writes the "value" in the register, which is located in the "address" for a device with unit number "unit 
    # and device ip "station_ip" as signed integer

    charge_station = ModbusClient(station_ip, port=502, unit_id=unit, auto_open=True, auto_close=True)

    if (charge_station.connect() == False):
        pass
    else: 
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        builder.add_16bit_uint(value)		
        registers = builder.to_registers()
        charge_station.write_registers(address, registers, unit=unit)

def number_of_cars(openwb,webasto):
    
    #This functions returns the number charging station to which cars are connected "n" and 
    #whether the openWB or Webasto are connected in the connection_state_openwb or connection_state_webasto
        
    get_register_openwb = read_register(10114, 1, openwb.unit_id, openwb.ip)
    get_register_webasto = read_register(1004, 1, webasto.unit_id, webasto.ip) 
    openwb_hems_connection_state = get_register_openwb[2]
    webasto_hems_connection_state =get_register_webasto[2]
   
    if (get_register_openwb[2] == True): 
        
        if (get_register_openwb[1] == True):
            
            register_openwb = get_register_openwb[0]
            
        else:
            
            register_openwb = 100 # Arbitrary number for error

    else: 
        
        register_openwb = 100 # Arbitrary number for error
           
      
    if (get_register_webasto[2] == True):
        
        if (get_register_webasto[1] == True):
            
            register_webasto = get_register_webasto [0]
            
        else:
            
            register_webasto = 100 # Arbitrary number for error 
            
    else: 
        
        register_webasto = 100 # Arbitrary number for error
          
    connection_state_openwb = False
    connection_state_webasto = False
    
    if (register_openwb == 1 and (register_webasto == 2 or register_webasto == 3 or register_webasto == 4 or register_webasto == 5 or register_webasto == 6)):
        
        n = 2
        connection_state_openwb = True
        connection_state_webasto = True
    
    elif (register_openwb == 1 or (register_webasto == 2 or register_webasto == 3 or register_webasto == 4 or register_webasto == 5 or register_webasto == 6)):
        
        n = 1
       
        if (register_openwb == 1):
           
           connection_state_openwb = True 
           connection_state_webasto = False
        
        else: 
            connection_state_openwb = False
            connection_state_webasto = True
    else:
        n = 0
        connection_state_openwb = False
        connection_state_webasto = False

    return (n, connection_state_openwb, connection_state_webasto, openwb_hems_connection_state, webasto_hems_connection_state)

def pv_excess_power(P_pv, P_house):

    # This function delivers true, if there is excess PV production and false, if the house consumption is more than PV generation.
    
    if P_pv > P_house:
        
        excess_state = True 
        
    elif P_pv == P_house:
        
        excess_state = False 
        
    else: 
        
        excess_state = False 
        
    return excess_state

def read_user_inputs():
    
    # This function takes the inputs from the users and returns the values E_demand, E_max_demand and Charge_duration. 
    # In case the E_max_demand is smaller than E_demand it returns the error and asks for the values again. 

    wrong_input = True
    while wrong_input:
        
        E_demand = int(input("Please specify the requested charging energy kWh: "))
        E_max_demand = int(input("Please specify the maximum charging energy kWh: "))
        Charge_duration = int(input("Please specify the charging duration in minutes: "))
        
        if E_demand <= E_max_demand:
            
            wrong_input = False
            return (E_demand, E_max_demand, Charge_duration)
        
        print("Error: Maximum energy demand can't be smaller than requested energy demand")

def battery_state_home_battery(hbattery):
    
    #This function return the state of the home battery, while comparing the current charged energy and maximum, i.e. minumum energy capactiy of the battery.
    
    battery_state = 0
    if hbattery.soc == hbattery.soc_min:
        battery_state = 0 # "empty"
    elif hbattery.soc_min < hbattery.soc < hbattery.soc_max:
        battery_state= 1 #"between empty and full"
    elif hbattery.soc >= hbattery.soc_max:
        battery_state = 2 # "battery is full"
    else:
        print("Error: Battery state check was unsuccesfull")
    return battery_state

def ev_charging_state(E_charged, E_demand, E_max_demand):
    
    #The function compares the charged energy so far with E_demand and E_max_demand and delivers the charging state of the ev. 
    
    if E_charged < E_demand:
        
        ev_charge_state = 0 # charge power didn't reach requested energy #

    elif E_charged == E_demand:
        
        ev_charge_state = 1 #charge power reached requested energy

    elif E_demand < E_charged < E_max_demand: 
        
        ev_charge_state = 2 #charge poower reached requested energy but not to the maximum energy 

    else:
        
        ev_charge_state = 3 # car is totally charged

    return ev_charge_state

def priority_check(openwb, webasto, hbattery, grid_priority, results_cars):
    
    #This function sets priorities for the charging processes based on the number of cars connected and their charging states. 
    
    if (results_cars [0] == 0):
        
        print("There isn't any connected car.")
        

        if (hbattery.battery_state < 2):

            print("Home battery is not full. Home battery has the priority." )
            openwb.charge_priority = False
            webasto.charge_priority = False
            hbattery.priority = True
            grid_priority = False

        elif (hbattery.battery_state == 2):
            
            print("Home battery is full. Grid has priority. In case of excess power, the power will be given to the grid.")
            openwb.charge_priority = False
            webasto.charge_priority = False
            hbattery.priority = False
            grid_priority = True

    elif (results_cars [0] == 1):
        
        print("One car is connected")

        if (openwb.connection_state == True):
            
            print("Car is connected to the OpenWB charge station.")

            if (openwb.charging_state == 0):
                
                print("Car is not charged enough. Therefore it has the highest priority")
                openwb.charge_priority = True
                webasto.charge_priority = False
                hbattery.priority = False
                grid_priority = False

            elif ((openwb.charging_state == 1 or openwb.charging_state == 2) and hbattery.battery_state < 2):
                
                print("Car is charged enough. Home battery is not fully charged. Home battery has the priority.")
                hbattery.priority = True 
                openwb.charge_priority = False
                grid_priority = False
                webasto.charge_priority = False

            elif ((openwb.charging_state == 1 or openwb.charging_state == 2) and hbattery.battery_state == 2):
                
                print("Home battery is fully charged and car is not charged totally. Car has the priority.")                
                openwb.charge_priority = True
                hbattery.priority = False
                grid_priority = False
                webasto.charge_priority = False

            elif(openwb.charging_state == 3 and hbattery.battery_state == 2):
                
                print("Home battery and car are fully charged. Grid has the priority")
                grid_priority = True
                openwb.charge_priority = False
                hbattery.priority = False
                webasto.charge_priority = False

            else:
               
               print("Error: Priorites couldn't be set for only OpenWB is connected with a car.")

        elif (webasto.connection_state == True):
            
            print("Car is connected to the Webasto charge station.")

            if (webasto.charging_state == 0):
                
                print("Car is not charged enough. Therefore it has the highest priority")
                webasto.charge_priority = True
                hbattery.priority = False
                grid_priority = False
                openwb.charge_priority = False

            elif ((webasto.charging_state == 1 or webasto.charging_state == 2) and hbattery.battery_state < 2):
                
                print("Car is charged enough. Home battery is not fully charged. Home battery has the priority.")
                hbattery.priority = True 
                webasto.charge_priority = False
                grid_priority = False
                openwb.charge_priority = False

            elif ((webasto.charging_state == 1 or webasto.charging_state == 2) and hbattery.battery_state == 2):
                
                print("Home battery is fully charged and car is not charged totally. Car has the priority.")                
                webasto.charge_priority = True
                hbattery.priority = False
                grid_priority = False
                openwb.charge_priority = False

            elif(webasto.charging_state == 3 and hbattery.battery_state == 2):
                
                print("Home battery and car are fully charged. Grid has the priority")
                grid_priority = True
                webasto.charge_priority = False
                hbattery.priority = False 
                openwb.charge_priority = False

            else:
                
                print("Error: Priorites couldn't be set for only Webasto is connected with a car.")
        else: 
            
            print("Error: To which station the car is connected couldn't be found.")

    elif (results_cars[0] == 2):
        
        print("Cars are connected to OpenWB and Webasto")

        if(openwb.charging_state == 0 and webasto.charging_state == 0):
            
            print("Both cars are not charged enough.")

            if (openwb.e_demand <= webasto.e_demand):
                    
                    openwb.charge_priority = True
                    webasto.charge_priority = False
                    print("Car connected to OpenWB has less requested energy, so it will be charged first")

            else:
                    webasto.charge_priority = True
                    openwb.charge_priority = False
                    print("Car connected to Webasto has less requested energy, so it will be charged first")
            
            hbattery.priority = False
            grid_priority = False
        elif (openwb.charging_state == 0 and webasto.charging_state != 0):
            
            openwb.charge_priority = True
            webasto.charge_priority = False
            hbattery.priority = False
            grid_priority = False
            print("Car connected to Webasto is charged enough, car connected to OpenWB will be charged next.")

        elif (openwb.charging_state != 0 and webasto.charging_state == 0):
            
            webasto.charge_priority = True
            openwb.charge_priority = False
            hbattery.priority = False
            grid_priority = False
            print("Car connected to OpenWB is charged enough, car connected to Webasto will be charged next.")

        elif (openwb.charging_state >= 1 and webasto.charging_state >= 1 and hbattery.battery_state < 2):
            
            openwb.charge_priority = False
            webasto.charge_priority = False
            hbattery.priority = True
            grid_priority = False
            print("All cars are charged enough, priority is given to the home battery.")

        elif (openwb.charging_state >= 1 and webasto.charging_state >= 1 and hbattery.battery_state >= 2):
            
            if (openwb.charging_state == 3 and webasto.charging_state == 3 and hbattery.battery_state == 2):
                
                print("Cars are fully charged and home battery is full, in case of excess PV Power, it will be feed-in to the grid.")
                openwb.charge_priority = False
                webasto.charge_priority = False
                hbattery.priority = False
                grid_priority = True

            elif (openwb.charging_state == 3 and webasto.charging_state != 3 and hbattery.battery_state == 2):
                
                print("Car connected to OpenWB is charged fully and home battery is full, in case of excess PV Power, car connected to Webasto will be charged.")
                openwb.charge_priority = False
                webasto.charge_priority = True
                hbattery.priority = False
                grid_priority = False

            elif (openwb.charging_state != 3 and webasto.charging_state == 3 and hbattery.battery_state == 2):
                
                print("Car connected to Webasto is charged fully and home battery is full, in case of excess PV Power, car connected to OpenWB will be charged.")
                openwb.charge_priority = True
                webasto.charge_priority = False
                hbattery.priority = False
                grid_priority = False

            else:
                
                if (openwb.e_max_demand <= webasto.e_max_demand):
                        openwb.charge_priority = True
                        webasto.charge_priority = False
                        hbattery.priority = False
                        grid_priority = False
                        print("Cars are charged enough, but both are not charged fully. Car connected to OpenWB will be charged first, as it requires less maximum energy.")

                else:
                        webasto.charge_priority = True
                        openwb.charge_priority = False
                        hbattery.priority = False
                        grid_priority = False
                        print("Cars are charged enough, but both are not charged fully. Car connected to Webasto will be charged first, as it requires less maximum energy.")

        else:
            
            print("Error: No charging station could be prioritised.")
    else: 
        
        print("Error: Number of cars don't match 0, 1 or 2")

    return grid_priority

def electricity_price_expensiveness(c_elec,openwb, webasto, all_inputs, counter):
    
    # This function calculates first the average price in c_elex_frame_x in the charge intervall given by the user. 
    # It then compares theactual price with the average price and delivers true, if the electrictiy is cheap. 
  
    just_prices = all_inputs.iloc[:,3]

    if (openwb.connection_state == True and webasto.connection_state == True):
       just_prices_openwb = just_prices[counter: counter + openwb.charge_duration]
       c_elec_frame_openwb = just_prices_openwb.sum(axis=0, skipna=True) / openwb.charge_duration
       just_prices_webasto = just_prices[counter: counter + webasto.charge_duration]
       c_elec_frame_webasto = just_prices_webasto.sum(axis=0, skipna=True) / webasto.charge_duration

    elif (openwb.connection_state == True and webasto.connection_state == False):
       just_prices_openwb = just_prices[counter: counter + openwb.charge_duration]
       c_elec_frame_openwb = just_prices_openwb.sum(axis=0, skipna=True) / openwb.charge_duration
       c_elec_frame_webasto = c_elec
    elif (openwb.connection_state == False and webasto.connection_state == True):
       c_elec_frame_openwb = c_elec
       just_prices_webasto = just_prices[counter: counter + webasto.charge_duration]
       c_elec_frame_webasto = just_prices_webasto.sum(axis=0, skipna=True) / webasto.charge_duration
    elif (openwb.connection_state == False and webasto.connection_state == False):
       c_elec_frame_openwb = c_elec
       c_elec_frame_webasto = c_elec
    else:
        print("Error: C_elec_frame couldn't be calculated.")

    if (c_elec_frame_openwb >= c_elec):
        openwb_electricity_is_cheap = True
    else: 
        openwb_electricity_is_cheap = False
    
    if (c_elec_frame_webasto >= c_elec):
        webasto_electricity_is_cheap = True
    else:
        webasto_electricity_is_cheap = False
    return (openwb_electricity_is_cheap, webasto_electricity_is_cheap, c_elec_frame_openwb, c_elec_frame_webasto)

def charging_power_calculation(openwb, webasto,P_pv, P_house, hbattery, grid_priority,c_elec):
    
    # This function calculates charging power and battery discharging power based on different conditions.

    excess_state = pv_excess_power(P_pv, P_house)
    battery_state = hbattery.battery_state
    P_grid_charge = 0 
    P_charge = 0 
    P_positive_excess_power = (max(0, P_pv - P_house))
    P_feed_in = 0
    
    if (c_elec >= 0):

        if (openwb.charge_priority):
        
            print("Charging power for OpenWB is calculating.")
            P_bat_discharge = max(0,min(hbattery.max_discharge_power, openwb.max_charge_power - (P_pv - P_house))) # Setting boundaries for P_bat,discharge        
            P_grid_charge = max(0,openwb.max_charge_power - P_positive_excess_power - P_bat_discharge) # Deciding necessary power from the grid for charging with maximum power
            #P_feed_in = max(0,P_positive_excess_power - openwb.max_charge_power) # Calculating feed in power for the case that already the excess power might be more than maximum charing power
        
            if(openwb.charging_state == 0 and excess_state == True and battery_state != 0 and openwb.electricity_cheap == True ):
            
                if (P_positive_excess_power > openwb.max_charge_power):
                    P_bat_discharge = - (P_positive_excess_power - openwb.max_charge_power)
                    hbattery.soc= hbattery.soc - P_bat_discharge / 60

                    if (P_positive_excess_power > openwb.max_charge_power + hbattery.max_discharge_power):
                    
                        while (hbattery.soc != hbattery.soc_max):
                            P_bat_discharge = hbattery.max_discharge_power
                            P_feed_in = P_positive_excess_power - openwb.max_charge_power - hbattery.max_discharge_power
                        else:
                            P_feed_in = P_positive_excess_power - openwb.max_charge_power
                    else:
                        pass
                else: 
                    print("Car is not charged enough, home battery is not empty, electricity is inexpensive, charge with PV excess, and if needed first with battery and  then grid")
                    P_charge = P_grid_charge + P_positive_excess_power + P_bat_discharge
                    openwb.charged_energy = openwb.charged_energy + P_charge / 60 # Charged energy in a minute in kWh
                    hbattery.soc= hbattery.soc- P_bat_discharge / 60 #  Used battery energy


            elif (openwb.charging_state == 0 and excess_state == True and battery_state != 0 and openwb.electricity_cheap == False):

                if (P_positive_excess_power > openwb.max_charge_power):
                
                    P_bat_discharge = - (P_positive_excess_power - openwb.max_charge_power)
                    hbattery.soc= hbattery.soc - P_bat_discharge / 60

                    if (P_positive_excess_power > openwb.max_charge_power + hbattery.max_discharge_power):
                    
                        while (hbattery.soc != hbattery.soc_max):
                            P_bat_discharge = hbattery.max_discharge_power
                            P_feed_in = P_positive_excess_power - openwb.max_charge_power - hbattery.max_discharge_power
                        else:
                            P_feed_in = P_positive_excess_power - openwb.max_charge_power
                    else: 
                        pass

                else:            
                    print("Car is not charged enough, home battery is not empty, electricity is expensive, charge with PV excess and if needed with battery")
                    P_charge = P_positive_excess_power + P_bat_discharge
                    openwb.charged_energy = openwb.charged_energy + P_charge / 60 
                    hbattery.soc= hbattery.soc- P_bat_discharge / 60
                P_grid_charge = 0

            elif (openwb.charging_state == 0 and excess_state == True and battery_state == 0 and openwb.electricity_cheap == False):

                if (P_positive_excess_power > openwb.max_charge_power):
                    P_bat_discharge = - (P_positive_excess_power - openwb.max_charge_power)
                    hbattery.soc= hbattery.soc - P_bat_discharge / 60

                    if (P_positive_excess_power > openwb.max_charge_power + hbattery.max_discharge_power):
                    
                        while (hbattery.soc != hbattery.soc_max):
                            P_bat_discharge = hbattery.max_discharge_power
                            P_feed_in = P_positive_excess_power - openwb.max_charge_power - hbattery.max_discharge_power
                        else:
                            P_feed_in = P_positive_excess_power - openwb.max_charge_power
                    else: 
                        pass
                else:
            
                    print("Car is not charged enough, home battery is empty, electricity is expensive, charge with only PV excess")
                    P_charge = P_positive_excess_power
                    openwb.charged_energy = openwb.charged_energy + P_charge / 60 
                P_bat_discharge = 0
                P_grid_charge = 0

            elif (openwb.charging_state == 0 and excess_state == True  and battery_state == 0 and openwb.electricity_cheap == True):

                if (P_positive_excess_power > openwb.max_charge_power):
                    P_bat_discharge = - (P_positive_excess_power - openwb.max_charge_power)
                    hbattery.soc= hbattery.soc - P_bat_discharge / 60

                    if (P_positive_excess_power > openwb.max_charge_power + hbattery.max_discharge_power):
                    
                        while (hbattery.soc != hbattery.soc_max):
                            P_bat_discharge = hbattery.max_discharge_power
                            P_feed_in = P_positive_excess_power - openwb.max_charge_power - hbattery.max_discharge_power
                        else:
                            P_feed_in = P_positive_excess_power - openwb.max_charge_power
                    else: 
                        pass
                else:            

                    print("Car is not charged enough, home battery is empty, electricity is inexpensive, charge with PV excess and if needed with grid")                 
                    P_grid_charge = P_grid_charge + P_bat_discharge
                    P_charge = P_grid_charge + P_positive_excess_power
                    openwb.charged_energy = openwb.charged_energy + P_charge / 60 
                P_bat_discharge = 0
               
            elif(openwb.charging_state == 0 and excess_state == False and battery_state == 0 and openwb.electricity_cheap == False ):
           
               print("Car is not charged enough, home battery is empty, electricity is expensive, no PV excess, don't charge")
            
               P_charge = 0
               P_bat_discharge = 0
               P_grid_charge = 0

            elif(openwb.charging_state == 0 and excess_state == False and battery_state == 0 and openwb.electricity_cheap == True ):
            
                print("Car is not charged enough, home battery is empty, electricity is inexpensive, charge with grid")
                P_grid_charge = openwb.max_charge_power
                P_charge = P_grid_charge 
                openwb.charged_energy = openwb.charged_energy + P_charge / 60 
                P_bat_discharge = 0           

            elif(openwb.charging_state == 0 and excess_state == False and battery_state != 0 and openwb.electricity_cheap == False ):
            
                print("Car is not charged enough, home battery is not empty, electricity is expensive, charge with battery ")            
                P_charge = P_bat_discharge           
                openwb.charged_energy = openwb.charged_energy + P_charge / 60 
                hbattery.soc= hbattery.soc- P_bat_discharge / 60
                P_grid_charge = 0

            elif(openwb.charging_state == 0 and excess_state == False and battery_state != 0 and openwb.electricity_cheap == True):

                print("Car is not charged enough, home battery is not empty, electricity is inexpensive, , charge with battery and if needed with grid")
                P_bat_discharge = min(hbattery.max_discharge_power, openwb.max_charge_power)
                P_grid_charge = max(0,openwb.max_charge_power - P_bat_discharge)
                P_charge = P_grid_charge + P_bat_discharge
                openwb.charged_energy = openwb.charged_energy + P_charge / 60 
                hbattery.soc= hbattery.soc - P_bat_discharge / 60 

            elif(openwb.charging_state == 1 or 2 and excess_state == True):

                if (P_positive_excess_power > openwb.max_charge_power):
                
                    P_feed_in = P_positive_excess_power - openwb.max_charge_power
                else:             
                    print("Car is charged enough, excess power is used for charging until totally full")
                    P_charge = min(openwb.max_charge_power,P_positive_excess_power)
                    openwb.charged_energy = openwb.charged_energy + P_charge / 60  
                P_bat_discharge= 0 
                P_grid_charge = 0 
                P_charge = 0 
            
            
            elif(openwb.charging_state == 1 or 2 and excess_state == False):
                print("Car is charged enough, there is no excess power, don't charge")
                P_bat_discharge= 0 
                P_grid_charge = 0
                P_charge = 0

            else:
                print("Error: Charging power for OpenWB couldn't be calculated.")
        
            openwb.pv_elec = P_positive_excess_power / P_charge
            openwb.charging_power = P_charge
            charge_openwb(openwb)

        elif(webasto.charge_priority):
        
            print("Charging power for webasto is calculating.")
            P_bat_discharge = max(0,min(hbattery.max_discharge_power, webasto.max_charge_power - (P_pv - P_house))) # Setting boundaries for P_bat,discharge        
            P_grid_charge = max(0,webasto.max_charge_power - P_positive_excess_power - P_bat_discharge) # Deciding necessary power from the grid for charging with maximum power
            #P_feed_in = max(0,P_positive_excess_power - webasto.max_charge_power) # Calculating feed in power for the case that already the excess power might be more than maximum charing power
        
            if(webasto.charging_state == 0 and excess_state == True and battery_state != 0 and webasto.electricity_cheap == True ):
            
                if (P_positive_excess_power > webasto.max_charge_power):
                    P_bat_discharge = - (P_positive_excess_power - webasto.max_charge_power)
                    hbattery.soc= hbattery.soc - P_bat_discharge / 60

                    if (P_positive_excess_power > webasto.max_charge_power + hbattery.max_discharge_power):
                    
                        while (hbattery.soc != hbattery.soc_max):
                            P_bat_discharge = hbattery.max_discharge_power
                            P_feed_in = P_positive_excess_power - webasto.max_charge_power - hbattery.max_discharge_power
                        else:
                            P_feed_in = P_positive_excess_power - webasto.max_charge_power
                    else:
                        pass
                else: 
                    print("Car is not charged enough, home battery is not empty, electricity is inexpensive, charge with PV excess, and if needed first with battery and  then grid")
                    P_charge = P_grid_charge + P_positive_excess_power + P_bat_discharge
                    webasto.charged_energy = webasto.charged_energy + P_charge / 60 # Charged energy in a minute in kWh
                    hbattery.soc= hbattery.soc- P_bat_discharge / 60 #  Used battery energy


            elif (webasto.charging_state == 0 and excess_state == True and battery_state != 0 and webasto.electricity_cheap == False):

                if (P_positive_excess_power > webasto.max_charge_power):
                
                    P_bat_discharge = - (P_positive_excess_power - webasto.max_charge_power)
                    hbattery.soc= hbattery.soc - P_bat_discharge / 60

                    if (P_positive_excess_power > webasto.max_charge_power + hbattery.max_discharge_power):
                    
                        while (hbattery.soc != hbattery.soc_max):
                            P_bat_discharge = hbattery.max_discharge_power
                            P_feed_in = P_positive_excess_power - webasto.max_charge_power - hbattery.max_discharge_power
                        else:
                            P_feed_in = P_positive_excess_power - webasto.max_charge_power
                    else: 
                        pass

                else:            
                    print("Car is not charged enough, home battery is not empty, electricity is expensive, charge with PV excess and if needed with battery")
                    P_charge = P_positive_excess_power + P_bat_discharge
                    webasto.charged_energy = webasto.charged_energy + P_charge / 60 
                    hbattery.soc= hbattery.soc- P_bat_discharge / 60
                P_grid_charge = 0

            elif (webasto.charging_state == 0 and excess_state == True and battery_state == 0 and webasto.electricity_cheap == False):

                if (P_positive_excess_power > webasto.max_charge_power):
                    P_bat_discharge = - (P_positive_excess_power - webasto.max_charge_power)
                    hbattery.soc= hbattery.soc - P_bat_discharge / 60

                    if (P_positive_excess_power > webasto.max_charge_power + hbattery.max_discharge_power):
                    
                        while (hbattery.soc != hbattery.soc_max):
                            P_bat_discharge = hbattery.max_discharge_power
                            P_feed_in = P_positive_excess_power - webasto.max_charge_power - hbattery.max_discharge_power
                        else:
                            P_feed_in = P_positive_excess_power - webasto.max_charge_power
                    else: 
                        pass
                else:
            
                    print("Car is not charged enough, home battery is empty, electricity is expensive, charge with only PV excess")
                    P_charge = P_positive_excess_power
                    webasto.charged_energy = webasto.charged_energy + P_charge / 60 
                P_bat_discharge = 0
                P_grid_charge = 0

            elif (webasto.charging_state == 0 and excess_state == True  and battery_state == 0 and webasto.electricity_cheap == True):

                if (P_positive_excess_power > webasto.max_charge_power):
                    P_bat_discharge = - (P_positive_excess_power - webasto.max_charge_power)
                    hbattery.soc= hbattery.soc - P_bat_discharge / 60

                    if (P_positive_excess_power > webasto.max_charge_power + hbattery.max_discharge_power):
                    
                        while (hbattery.soc != hbattery.soc_max):
                            P_bat_discharge = hbattery.max_discharge_power
                            P_feed_in = P_positive_excess_power - webasto.max_charge_power - hbattery.max_discharge_power
                        else:
                            P_feed_in = P_positive_excess_power - webasto.max_charge_power
                    else: 
                        pass
                else:            

                    print("Car is not charged enough, home battery is empty, electricity is inexpensive, charge with PV excess and if needed with grid")                 
                    P_grid_charge = P_grid_charge + P_bat_discharge
                    P_charge = P_grid_charge + P_positive_excess_power
                    webasto.charged_energy = webasto.charged_energy + P_charge / 60 
                P_bat_discharge = 0
               
            elif(webasto.charging_state == 0 and excess_state == False and battery_state == 0 and webasto.electricity_cheap == False ):
           
               print("Car is not charged enough, home battery is empty, electricity is expensive, no PV excess, don't charge")
            
               P_charge = 0
               P_bat_discharge = 0
               P_grid_charge = 0

            elif(webasto.charging_state == 0 and excess_state == False and battery_state == 0 and webasto.electricity_cheap == True ):
            
                print("Car is not charged enough, home battery is empty, electricity is inexpensive, charge with grid")
                P_grid_charge = webasto.max_charge_power
                P_charge = P_grid_charge 
                webasto.charged_energy = webasto.charged_energy + P_charge / 60 
                P_bat_discharge = 0           

            elif(webasto.charging_state == 0 and excess_state == False and battery_state != 0 and webasto.electricity_cheap == False ):
            
                print("Car is not charged enough, home battery is not empty, electricity is expensive, charge with battery ")            
                P_charge = P_bat_discharge           
                webasto.charged_energy = webasto.charged_energy + P_charge / 60 
                hbattery.soc= hbattery.soc- P_bat_discharge / 60
                P_grid_charge = 0

            elif(webasto.charging_state == 0 and excess_state == False and battery_state != 0 and webasto.electricity_cheap == True):

                print("Car is not charged enough, home battery is not empty, electricity is inexpensive, , charge with battery and if needed with grid")
                P_bat_discharge = min(hbattery.max_discharge_power, webasto.max_charge_power)
                P_grid_charge = max(0,webasto.max_charge_power - P_bat_discharge)
                P_charge = P_grid_charge + P_bat_discharge
                webasto.charged_energy = webasto.charged_energy + P_charge / 60 
                hbattery.soc= hbattery.soc - P_bat_discharge / 60 

            elif(webasto.charging_state == 1 or 2 and excess_state == True):

                if (P_positive_excess_power > webasto.max_charge_power):
                
                    P_feed_in = P_positive_excess_power - webasto.max_charge_power
                else:             
                    print("Car is charged enough, excess power is used for charging until totally full")
                    P_charge = min(webasto.max_charge_power,P_positive_excess_power)
                    webasto.charged_energy = webasto.charged_energy + P_charge / 60  
                P_bat_discharge= 0 
                P_grid_charge = 0 
                P_charge = 0 
            
            
            elif(webasto.charging_state == 1 or 2 and excess_state == False):
                print("Car is charged enough, there is no excess power, don't charge")
                P_bat_discharge= 0 
                P_grid_charge = 0
                P_charge = 0

            else:
                print("Error: Charging power for webasto couldn't be calculated.")
        
            webasto.pv_elec = P_positive_excess_power / P_charge
            webasto.charging_power = P_charge
            charge_webasto(webasto)       


        elif (hbattery.priority):

            P_bat_discharge = 0 
        
            if(excess_state == True):
                while (P_positive_excess_power < hbattery.max_discharge_power):
                    P_bat_discharge = - P_positive_excess_power
                    hbattery.soc= hbattery.soc - P_bat_discharge / 60
                    print("Battery is charging with excess power")
                else:
                
                    P_bat_discharge = - hbattery.max_discharge_power
                    P_feed_in = P_positive_excess_power - hbattery.max_discharge_power

            else: 
                print("There is no excess power and battery will be charged, as soon as excess PV power is present")
                P_bat_discharge = min(hbattery.max_discharge_power, P_house - P_pv) if hbattery.soc != 0 else 0            
            hbattery.soc= hbattery.soc - P_bat_discharge / 60
            

        elif (grid_priority):

            if (excess_state == True):
                P_feed_in = P_positive_excess_power

            else: 
                print("The house doesn't exchange feed-in any power ")
                P_bat_discharge = P_house - P_pv
                hbattery.soc= hbattery.soc - P_bat_discharge / 60
        else:
            print("Error: No priority could be set.")
    else: 
        
        P_bat_discharge = hbattery.max_discharge_power
        openwb.charging_power = openwb.max_charge_power
        webasto.charging_power = webasto.max_charge_power

    hbattery.used_power = P_bat_discharge  
    P_grid = P_house + P_grid_charge - P_pv - P_bat_discharge
    
    return P_grid, P_grid_charge, P_feed_in, P_charge

def charge_webasto(webasto):
    if (webasto.connection_state == True):
        webasto_charge_current = webasto.charging_power / 0.230 ## Converting power to current, 1-phase
        print("Webasto charge curret is now:{}" .format(webasto_charge_current))
        write_register_unint(webasto_charge_current, 5004, webasto.unit_id, webasto.ip)
    else:
        print ("Connection to webasto is interrupted")
        webasto_charge_current = 0
        print("Charging station webasto is not controlled by HEMS.")
        print("Webasto charge curret is now:{}" .format(webasto_charge_current))
    return

def charge_openwb(openwb):
    if (openwb.connection_state == True):
        openwb_charge_current = openwb.charging_power / 0.230 ## Converting power to current, 1-phase
        print("Openwb charge curret is now:{}" .format(openwb_charge_current))
        write_register_int(0, 112, openwb.unit_id, openwb.ip) ## Setting it to Sofort - Laden
        write_register_int(openwb_charge_current, 10152, openwb.unit_id, openwb.ip) ## Setting the current
        write_register_int(1, 10151, openwb.unit_id, openwb.ip) ## Enable charge point
        
    else:
        #print ("Connection to webasto is interrupted")
        openwb_charge_current = 0
        print("Charging station openwb is not controlled by HEMS.")
        print("Openwb charge curret is now:{}" .format(openwb_charge_current))
    return

