import pymysql

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