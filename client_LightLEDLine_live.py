
from Adafruit_PWM_Servo_Driver import PWM
import socket
import time
import colorsys
import sys

#LIGHT DATA
class LightVoltage():
	def __init__(self,colourList):
		self.servoMin = 10  # Min pulse length out of 4096
		self.servoMax = 4096  # Max pulse length out of 4096
		self.colourList = colourList
		self.servoNumber = 0 #set this value and use it to tick up through the 

	def broadcast(self):
		for index, c in enumerate(self.colourList): #each of c is now an individual colour channel that we need to wire up in a big long line
			pwm.setPWM(index, 0, int(c*self.servoMax))
			print "Channel : " + str(index) + " - " + str(int(c*self.servoMax))
		print "\n"


# pwm = PWM(0x40, debug=True)


#CONNECTION DATA
HOST = str(sys.argv[1])
PORT = int(sys.argv[2])

s= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST,PORT))


def processColours(colourStr):
	"""Messy function to work through the strings and return the RGB values"""
	LEDFinalColours = []
	LEDStringColours = colourStr.split("|")
	for s in LEDStringColours:
		channels = s.replace("["," ").replace(","," ").replace("]"," ").split() 
		hsVconversion = colorsys.hsv_to_rgb(float(channels[0]),float(channels[1]),float(channels[2]))
		# LEDFinalColours.append([round(hsVconversion[0],2), round(hsVconversion[2],2), round(hsVconversion[1],2)])
		LEDFinalColours.append(round(hsVconversion[0],2))
		LEDFinalColours.append(round(hsVconversion[2],2))
		LEDFinalColours.append(round(hsVconversion[1],2))
	return LEDFinalColours


while 1:
	data = s.recv(128)
	colourList = processColours(data)
	colours = LightVoltage(colourList)
	colours.broadcast()
	# print "The data I have recieved is: " + data
	time.sleep(0.05)

