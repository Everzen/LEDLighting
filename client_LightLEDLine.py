import socket
import time
import colorsys

HOST = "localhost"
PORT = 5454

s= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST,PORT))


def processColours(colourStr):
	"""Messy function to work through the strings and return the RGB values"""
	LEDFinalColours = []
	LEDStringColours = colourStr.split("|")
	for s in LEDStringColours:
		channels = s.replace("["," ").replace(","," ").replace("]"," ").split() 
		hsVconversion = colorsys.hsv_to_rgb(float(channels[0]),float(channels[1]),float(channels[2]))
		LEDFinalColours.append([round(hsVconversion[0],2), round(hsVconversion[2],2), round(hsVconversion[1],2)])
	return LEDFinalColours


while 1:
	data = s.recv(128)
	colourList = processColours(data)
	print "ColourList : %s" % str(colourList) 
	# print "The data I have recieved is: " + data
	time.sleep(0.05)

