#!/usr/bin/python

#Beispielaufruf sudo ./KHAzureTimedLogger.py ModelB+ Schreibtisch Kalibrierung

# All in one version of this one: http://www.identitymine.com/blog/2015/06/19/iot-with-raspberry-pi-azure-and-windows-devices/

from azure.storage import TableService, Entity
from datetime import datetime
import socket
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
from time import *
import threading
import sys

# Azure Access Information
import AzureConfig.py

global Sensor
global Ort
global Kommentar
global DatumUhrzeit
global Uhrzeit
global Datum



def getData():
	hum, temp = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN)
	if hum is not None and temp is not None:
		temp +=	Temperaturkorrektur 
		hum += Luftfeuchtekorrektur
		StrTemp = str('{0:0.2f}'.format(temp)).replace(".",",")
		StrHum = str('{0:0.2f}'.format(hum)).replace(".",",")
			
		print 'Uhrzeit: ' + Uhrzeit
		print 'Temperatur: ' + StrTemp + ' C'
		print 'Luftfeuchte: ' + StrHum + ' %' + '\n'
		
		if hostname == "raspberry2":
			print "versetztes Senden fuer diesen Pi dann sind die Eintraege immer alternierend..."
			sleep(2)
		print sendData(temp, hum)
		
		sleep(1) #falls der Ablauf zu schnell geht waeren sonst mehrere Eintraege pro Timestamp moeglich
	else:
		print 'Fehler beim Auslesen des Sensors'

def sendData(temp, hum):
	reading = Entity()
	reading.PartitionKey = Ort
	if hostname == "raspberry1":
		reading.RowKey = DatumUhrzeit+"B"
	else:
		reading.RowKey = DatumUhrzeit+"B+"
	reading.Datum = Datum
	reading.Uhrzeit = Uhrzeit
	reading.Temperatur = round(temp, 2)
	#reading.TemperaturStr = str('{0:0.2f}'.format(temp)).replace(".",",")
	reading.Luftfeuchte = round(hum, 2)
	#reading.LuftfeuchteStr = str('{0:0.2f}'.format(hum)).replace(".",",")
	reading.Sensor = Sensor
	reading.Kommentar = Kommentar
	try:
		if check_internet_available():
			print "internet tut"
			table_service.insert_entity(table_name = table_name,entity = reading)
			return True
	except Exception, e:
		return False
			
	
def get_connection_string_and_create_table():
	global table_service
	table_service = TableService(account_name = ac_name,account_key=primary_key)
	#table_service.delete_table(table_name = table_name) #TO BE USED IF THE TABLE NEEDS TO BE DELETED
	table_service.create_table(table=table_name)


def check_internet_available():
	remote_server = 'www.google.com'
	try:
		host = socket.gethostbyname(remote_server)
		s = socket.create_connection((host,80),2)
		return True
	except:
		pass
	return False


if len(sys.argv) != 3:
	print sys.argv[0] + " <Ort> <Kommentar>"
	exit()


hostname = socket.gethostbyaddr(socket.gethostname())[0] 
print "================================================="

if hostname == "raspberry1": 
	print "Einstellen der Konfiguration fuer den Pi Modell B"
	DHT_TYPE = Adafruit_DHT.DHT22 
	DHT_PIN  = 17
	Temperaturkorrektur = 0.1
	Luftfeuchtekorrektur = 1.0
	Sensor = "raspberry1, DHT22"
elif hostname == "raspberry2":
	print "Einstellen der Konfiguration fuer den Pi Modell B+"
	DHT_TYPE = Adafruit_DHT.AM2302 
	DHT_PIN  = 12
	Temperaturkorrektur = - 0.1
	Luftfeuchtekorrektur = - 1.0
	Sensor ="raspberry2, AM2302"
else:
	print "Unbekannter Hostname."
	exit()

print Sensor
print "GPIO Pin: " + str(DHT_PIN)
print "Temperaturkorrektur: " + str(Temperaturkorrektur)
print "Luftfeuchtekorrektur: " + str(Luftfeuchtekorrektur) 
print "=================================================\n"

try:
	Ort=sys.argv[1]
except:
	Ort ="unknown"
try:
	Kommentar =sys.argv[2]
except:
	Kommentar  ="unknown"


	
get_connection_string_and_create_table()
	
while True:
	DatumUhrzeit = datetime.strftime(datetime.now(),'%d-%m-%Y %H:%M:%S')
	Datum = DatumUhrzeit[:-9]
	Uhrzeit = DatumUhrzeit[11:]
	
	Minute=Uhrzeit[3:-3]
	Sekunde=Uhrzeit[6:]
	
	#print Uhrzeit
	if int(Minute)%2 == 00 and int(Sekunde) == 0:
	#if int(Sekunde)%2 == 0:
		print "es ist soweit"
		getData()

	#threading.Timer(0.5,sensorloop).start()
	sleep(0.5)



if __name__ == '__main__':
	getCmdlineArgs()
	get_connection_string_and_create_table()
	sensorloop()