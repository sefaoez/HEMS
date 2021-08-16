import pymysql

# Sefa's Variablen 
hems_verbindung1 = 1
hems_verbindung2 = 0
openwb_connection_state = 1
webasto_connection_state = 0
openwb_charge_priority = 3
webasto_charge_priority = 4
openwb_charging_power = 50
webasto_charging_power = 22
pv_energy_share_webasto = 30
pv_energy_share_openwb = 11
remaining_time_webasto = 12
remaining_time_openwb = 13
demand_energy_openwb = 14
demand_energy_webasto = 15
charging_state_openwb = 16
charging_state_webasto = 17

Strompreis_aktuell = 1.50
Stromnetzverwendung_aktuell = 20
StromnetzverwendungLaden_aktuell = 10
Ladekosten_aktuell = 12
Gewinn_HEMS = 10
Gewinn_HEMS_gesamt = 10000

ErzeugungPV_Energie = 13
Haushalt_Stromverbrauch = 190
Heimspeicher_Leistung = 180
Heimspeicher_Ladezustand = 120






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