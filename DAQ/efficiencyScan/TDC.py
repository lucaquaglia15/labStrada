#Class to implement all TDC functions for ease of use
import time
import sys
from VME import VME

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

AM = 0x0D #AM accepted by the V488, supervised access
DW = 0x02 #D16, only mode accepted by the TDCs
VMEbridge = VME(1,0,0) #Define VME object in order to perform read/write operations on the TDCs

class TDC:

	#VME class constructor
	def __new__(cls, *args, **kwargs):
		return super().__new__(cls)

	#mode = 0 -> common start, = 1 -> common stop + enabled channles
	def __init__(self, baseAddress, lowTh, highTh, timeWindow, mode, IRQ):
		self.baseAddress = baseAddress
		self.lowTh = lowTh
		self.highTh = highTh
		self.timeWindow =  timeWindow
		self.mode = mode
		self.IRQ = IRQ

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
	def resetModule(self,VMEbridge,handle): #BA + 0x1C, read or write
		print("Resetting module with base address",self.baseAddress)
		VMEbridge.read(handle,self.baseAddress,0x1C,AM,DW)
		print("Module with base address",self.baseAddress," successfully reset")
		
	#Set low threshold
	def setLowThr(self, VMEbridge, handle): #BA + 0x10, write only
		
		#Check if low thr is < 0
		if hex(self.lowTh) < hex(0x0):
			sys.exit("Low threshold cannot be negative")
		
		VMEbridge.write(handle,self.baseAddress,0x10,self.lowTh,AM, DW)
		print("Setting low threshold for module with base address",self.baseAddress)
		print("Low threshold value",self.lowTh)

	#Set high threshold
	def setHighThr(self, VMEbridge, handle): #BA + 0x12, write only
		
		#Check that high thr is below 0xC7 and above 0
		if hex(self.highTh) > hex(0xC7):
			sys.exit("High thr above higher limit")
		elif hex(self.highTh) < hex(0x0):
			sys.exit("High thr cannot be negative")

		VMEbridge.write(handle,self.baseAddress,0x12,self.highTh,AM, DW)
		print("Setting high threshold for module with base address",self.baseAddress)
		print("High threshold value",self.highTh)

	#Set time window
	def setTimeWindow(self, VMEbridge, handle):
		#The conversion for find N, with given time interval (T), is: N = (3840/T - 3840/90)*(-1/0.16821274)
		#Check that time window is below 770 ns and above 90 ns
		if hex(self.timeWindow) > hex(0xE0):
			sys.exit("Time window above 770ns")
		elif hex(self.timeWindow) < hex(0x0):
			sys.exit("Time window below 90ns")
		
		VMEbridge.write(handle,self.baseAddress,0x14,self.timeWindow,AM,DW)
		print("Setting time window for module with base address",self.baseAddress)
		print("Time window value: ", self.timeWindow)
	
	#Set IRQ level and status
	def accessIRQregister(self, VMEbridge, handle, accessMode):
		
		if accessMode == 0: #read
			VMEbridge.read(handle,self.baseAddress,0x0,AM,DW)
		elif accessMode == 1: #write
			VMEbridge.write(handle,self.baseAddress,0x0,self.IRQ,AM,DW)
			print("Setting IRQ parameters for module with base address", self.baseAddress)
			print("IRQ parameters: ", self.IRQ)

	#Read or write control register
	def accessControlRegister(self, VMEbridge, handle, accessMode):
		
		if accessMode == 0: #read
			VMEbridge.read(handle,self.baseAddress,0x1A,AM,DW)
		elif accessMode == 1: #write
			VMEbridge.write(handle,self.baseAddress,0x1A,self.mode,AM,DW)
			print("Setting DAQ mode for module with base address", self.baseAddress)
			print("DAQ mode: ", self.mode)
	
	#Read output buffer
	def readOutputBuffer(self,VMEbridge,handle):

		#to write result eactly as a 16 bit binary number (leading 0's)
		data = '{0:016b}'.format(VMEbridge.read(handle,self.baseAddress,0x18,AM,DW)) 
		print("data",data)
		if int(data[0]) == 1: #header
			print("HEADER")
			mult = ""
			evNum = ""
			for i in range(3):
				mult = mult + data[i+1]

			for i in range(12):
				print(i)
				evNum = evNum + data[i+4]

			print("Molteplicità :", int(mult,2)+1)
			print("Trigger number: ",evNum)
			#print(int(mult,10)+1)
			return [int(mult,2)+1,int(evNum,10)]
		
		elif int(data[0]) == 0: #event
			print("Event")
			ch = ""
			time = ""
			for i in range(3):
				ch = ch + data[i+1]

			for i in range(12):
				time = time+data[i+4]
			
			print("channel: ",type(int(ch,2)), " ", int(ch,2))
			print("time: ",int(time,2))
			
			eventTime = self.converter(int(time,2))
			
			if hex(self.baseAddress) == hex(0x02000000):
				print("Channel with sum: ",int(ch,2))
				return [int(ch,2),eventTime]
			elif hex(self.baseAddress) == hex(0x03000000):
				print("Channel with sum: ",int(ch,2)+8)
				return [int(ch,2)+8,eventTime]
			elif hex(self.baseAddress) == hex(0x04000000):
				print("Channel with sum: ",int(ch,2)+16)
				return [int(ch,2)+16,eventTime]
	
	def converter(self,eventTime):
			convfactor = 3.6/4096
			print(self.timeWindow, eventTime)
			tw = 3840/((-0.16821274*self.timeWindow)+(3840/90))

			tensione = convfactor*eventTime 
			return tensione*tw/3.75

