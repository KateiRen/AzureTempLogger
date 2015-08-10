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
ac_name = 'khpistorage'
primary_key = 'GXLsHvq5fWp2DMHJtbBvTg+8FLLVcyCUglGi3MCaRCJBb+fecCh3hfcPV1Zonv8Lu6geD7Ii7MXmScpeb7niTw=='
secondary_key ='JrKjTTjTWzPGdFLFaIO8cMBU7FpBVzxE2u7zYpkcfoKFH3ZXLzqsHHlYAWFKtRrD04Yrp95TEquKw38sMNw1iQ=='
table_name = 'TemperaturLog'

global Sensor
global Ort
global Kommentar


if len(sys.argv) != 3:
	print sys.argv[0] + " <Ort> <Kommentar>"
	exit()


hostname = socket.gethostbyaddr(socket.gethostname())[0] 


if hostname == "raspberry1": 
	print "Einstellen der Konfiguration fuer den Pi Modell B"
	DHT_TYPE = Adafruit_DHT.DHT22 
	print "Sensor: DHT22"
	DHT_PIN  = 17
	Temperaturkorrektur = 0.05
	Luftfeuchtekorrektur = 0.95
	Sensor = "ModellB"
elif hostname == "raspberry2":
	print "Einstellen der Konfiguration fuer den Pi Modell B+"
	DHT_TYPE = Adafruit_DHT.AM2302 
	print "Sensor: AM2302"
	DHT_PIN  = 12
	Temperaturkorrektur = - 0.05
	Luftfeuchtekorrektur = - 0.95
	Sensor ="Modell B+"
else:
	print "Unbekannter Hostname."
	exit()

print "GPIO Pin: " + str(DHT_PIN)
print "Temperaturkorrektur: " + str(Temperaturkorrektur)
print "Luftfeuchtekorrektur: " + str(Luftfeuchtekorrektur) 
print "===============================\n"

try:
	Ort=sys.argv[1]
except:
	Ort ="unknown"
try:
	Kommentar =sys.argv[2]
except:
	Kommentar  ="unknown"

global DatumUhrzeit
global Uhrzeit
global Datum

def getData():
	humidity, temp = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN)
	if humidity is not None and temp is not None:
		Temp = str('{0:0.2f}'.format(temp)).replace(".",",")
		Hum = str('{0:0.2f}'.format(humidity)).replace(".",",")
			
		print 'Uhrzeit: ' + Uhrzeit
		print 'Temperatur: ' + Temp + ' C'
		print 'Luftfeuchte: ' + Hum + ' %' + '\n'
		
		print sendData(Temp, Hum)
		
		sleep(1) #falls der Ablauf zu schnell geht waeren sonst mehrere Eintraege pro Timestamp moeglich
	else:
		print 'Fehler beim Auslesen des Sensors'

def sendData(Temperatur, Hum):
	reading = Entity()
	reading.PartitionKey = Ort
	reading.RowKey = DatumUhrzeit
	reading.Datum = Datum
	reading.Uhrzeit = Uhrzeit
	reading.Temperatur = Temperatur
	reading.Luftfeuchte = Hum
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

		
while True:
	DatumUhrzeit = datetime.strftime(datetime.now(),'%d-%m-%Y %H:%M:%S')
	Datum = DatumUhrzeit[:-9]
	Uhrzeit = DatumUhrzeit[11:]
	
	Minute=Uhrzeit[3:-3]
	Sekunde=Uhrzeit[6:]
	
	print Uhrzeit
	#if int(Minute)%2 == 00 and int(Sekunde) == 0:
	if int(Sekunde)%2 == 0:
		print "es ist soweit"
		getData()

	#threading.Timer(0.5,sensorloop).start()
	sleep(0.5)



		


if __name__ == '__main__':
	getCmdlineArgs()
	get_connection_string_and_create_table()
	sensorloop()
