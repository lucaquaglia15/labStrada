#Class to implement all TDC functions for ease of use
#BA = base address (A32 mode)
import time
import sys
from VME import VME

#General hex to bin function
#def hexToBin():

#Board features
#V488A CAEN TDC

#ADC is 12 bit from 0 to 3840, values from 3841 to 4095 are not corrected
#max high threshold value is 0xC7

#Full scale time range, range register at BA + 0x14
#0x00 = 90 ns, 0xE0 = 770 ns

#Access to the reset register (read or write) to reset at BA + 0x1C

#Operation mode select bit 15 of the control register at BA + 0x1A
#<15> = 0 -> common start
#<15> = 1 -> common stop

#Enable/disable channels through control register (BA + 0x1A)
#<n> = 0 -> channel disabled
#<n> = 1 -> channel enabled

#Low and high thr setting at BA + 0x10 (low) and BA + 0x12 (high)

#FIFO mode, half full mode <12> of range register (BA + 0x14) -> 0
#FIFO mode, fifo full mode <12> of range register (BA + 0x14) -> 1

class TDC:

	#VME class constructor
	def __new__(cls, *args, **kwargs):
		return super().__new__(cls)

	#mode = 0 -> common start, = 1 -> common stop
	#enabled channels must be a 7-bit binary number, keeping in mind that
	#channels go from 7 to 0, e.g. 00100101 means that ch 0-2-5 are enabled
	def __init__(self, baseAddress, lowTh, highTh, timeWindow, mode, enChannels):
		self.baseAddress = baseAddress
		self.lowTh = lowTh
		self.highTh = highTh
		self.timeWindow =  timeWindow

	def __repr__(self) -> str:
		return f"{type(self).__name__}(baseAddress={self.baseAddress}, lowTh={self.lowTh}, highTh={self.highTh})"


	#---Member functions---#

	#TDC functions

	#Read module identifier words
	def idWords(self,address):
		print("Addess requested:",address)
		
		if address == 0xFA:
			print("Address corresponds to a fixed code")
		elif address == 0xFC:
			print("Address corresponds to ID of the module")
		elif address == 0xFE:
			print("Address corresponds to serial number and code")
		else:
			sys.exit("Address not recognized, stopping DAQ")

	#reset register
	def resetModule(self): #BA + 0x1C, read or write
		print("Resetting module with base address",self.baseAddress)

	def accessControlRegister(self): #BA + 0x1A
		#<15> read and write = 0 -> common start, = 1 -> common stop
		#<14> read only = 0 -> Output buffer is empty
		#<13> read only = 0 -> Output buffer is full
		#<12> read only = 0 -> Output buffer is half full
		#<7...0> -> channels 7...0, if <n> = 1 -> ch is enabled
		print("enabled channels (bin)",self.enChannels)


	def accessRangeRegister(self): #BA + 0x14
		#<12> read only, if = 0 -> HF; if = 1 -> FF
		#<7...0> full scale time, 0x00 = 90 ns; 0xE0 = 770 ns

	def accessInterruptRegister(self): #BA + 0x0

		#<15...13> interrupt level
		#<7...0> interrupt status/id what is placed on the interrupt 
		#<12> interrupt start condition, if = 0 -> interrupt on buffer HALF FULL
		#<12> interrupt start condition, if = 1 -> interrupt on buffer NOT EMPTY


	#Set low threshold
	def setLowThr(self): #BA + 0x10, write only
		#Check if low thr is < 0
		if self.lowTh < 0x0:
			sys.exit("Low threshold cannot be negative")

		print("Setting low threshold for module with base address",self.baseAddress)
		print("Low threshold value",self.lowTh)

	#Set high threshold
	def setHighThr(self): #BA + 0x12, write only
		#Check that high thr is below 0xC7
		if self.highTh > 0xC7:
			sys.exit("High thr above higher limit")
		elif self.highTh < 0x0:
			sys.exit("High thr cannot be negative")

		print("Setting high threshold for module with base address",self.baseAddress)
		print("High threshold value",self.highTh)

	#Set FIFO in half full mode
	def setFifoHalfFull(self): #BA + 0x1E read or write
		print("Setting FIFO to Half Full mode for module with base address",self.baseAddress)

	#Set FIFO in full mode 
	def setFifoFull(self): #BA + 0x16 read or write
		print("Setting FIFO to Full mode for module with base address",self.baseAddress)

	