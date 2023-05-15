#Class to use the functions of the CAEN VME library to communicate with bridge
import ctypes #for C++ function binding (CAEN HV library for example)
import pathlib
import time
import sys

#import caen HV wrapper library
libname = "/usr/lib/libCAENVME.so.v3.4.1"
CAENVMELib = ctypes.CDLL(libname)

VMEcodes = {0:"cvSuccess",-1:"cvBusError",-2:"cvCommError",-3:"cvGenericError",
-4:"cvInvalidParameter",-5:"cvTimeoutError",-6:"cvAlreadyOpenError",
-7:"cvMaxBoardCountError",-8:"cvNotSupported"}

debug = False #debug variable

#Board types
#cvV1718 = 0 -> CAEN V1718 USB-VME bridge
#cvV2718 = 1 -> V2718 PCI-VME bridge with optical link

class VME:

	#VME class constructor
	def __new__(cls, *args, **kwargs):
		return super().__new__(cls)

	def __init__(self, boardType, linkNumber, conetNode):
		self.boardType = boardType
		self.linkNumber = linkNumber
		self.conetNode = conetNode

	def __repr__(self) -> str:
		return f"{type(self).__name__}(boardType={self.boardType}, linkNumber={self.linkNumber}, conetNode={self.conetNode})"


	#---Member functions---#

	###################
	#                 #
	#General functions#
	#                 #
	###################

	#Open connection with VME bridge
	def connect(self):

		#Board not implemented, shut down program
		if self.boardType < 0 or self.boardType > 1:
			print("Sorry board not implemented")
			sys.exit("Exiting DAQ scan")

		cBoardType = ctypes.c_int(self.boardType)
		cLinkNumber = ctypes.c_uint32(self.linkNumber)
		cConetNode = ctypes.c_short(self.conetNode)
		handle = ctypes.c_int()

		pyVMEinit = CAENVMELib.CAENVME_Init2
		pyVMEinit.argtypes = [ctypes.c_int,ctypes.c_void_p,ctypes.c_short,ctypes.POINTER(ctypes.c_int)]
		pyVMEinit.restype = ctypes.c_int

		ret = pyVMEinit(cBoardType,ctypes.pointer(cLinkNumber),cConetNode,ctypes.pointer(handle))

		if ret != 0:
			print("Error in connect: ",VMEcodes[ret])

		if debug:
			print("ret in connect: ",ret)
			print(VMEcodes[ret])

		return handle
	
	#Close connection with VME bridge
	def disconnect(self,handle):

		pyVMEend = CAENVMELib.CAENVME_End
		pyVMEend.argtypes = [ctypes.c_int]
		pyVMEend.restype = ctypes.c_int

		ret = pyVMEend(handle)

		if debug:
			print("ret in disconnect: ",ret)
			print(VMEcodes[ret])
		
		if ret == 0:
			print("Disconnect successfully from VME bridge")
		else:
			print("Error disconnecting from bridge, error code:",ret)

	#Write data at given address
	def write(self,handle,baseAddress,address,data,AM,DW):

		print("Writing baseAddress",hex(baseAddress),"address",hex(address))

		#if hex(AM) != 0x3D or hex(AM) != 0x39 or hex(AM) != 0x0D or hex(AM) != 0x09:
		#	sys.exit("Wrong address modifier for the CAEN TDC, exiting")

		#if DW != 0x01 or DW != 0x02 or DW != 0x04 or DW != 0x08:
		#	sys.exit("Sorry wrong data width, exiting")

		cAddress = ctypes.c_uint32(baseAddress+address)
		cData = ctypes.c_uint(data)
		cAM =  ctypes.c_uint(AM)
		cDW =  ctypes.c_uint(DW)

		pyVMEwrite = CAENVMELib.CAENVME_WriteCycle
		pyVMEwrite.argtypes = [ctypes.c_int,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint,ctypes.c_uint]
		pyVMEwrite.restype = ctypes.c_int

		ret = pyVMEwrite(handle,cAddress,ctypes.pointer(cData),cAM,cDW)

		if debug:
			print("ret in write",ret)
			print(VMEcodes[ret])

	#Perform read cycle at given address
	def read(self,handle,baseAddress,address,AM,DW):

		print("Reading baseAddress",hex(baseAddress),"address",hex(address))
		
		cAddress = ctypes.c_uint32(baseAddress+address)
		cAM =  ctypes.c_uint(AM)
		cDW =  ctypes.c_uint(DW)

		pyVMEread = CAENVMELib.CAENVME_ReadCycle
		pyVMEread.argtypes = [ctypes.c_int,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint,ctypes.c_uint]
		pyVMEread.restype = ctypes.c_int

		cData = ctypes.c_uint()

		ret = pyVMEread(handle,cAddress,ctypes.pointer(cData),cAM,cDW)

		#Check if read is successful
		if ret != 0:
			print("Error while reading: ",VMEcodes[ret])
			sys.exit("Exiting from program due to VME read error")

		if debug:
			print("ret in read: ",ret)
			print(VMEcodes[ret])
			print("Result of read (hex string)",hex(cData.value))
		
		return cData.value

	#Configure VME bridge pulse
	# pulSel = 0 -> pulser A, pulSel = 1 -> pulser B
	# unit = 0 -> units of 25 ns, 1 -> units of 1.6 microseconds, 2 -> units of 410 microseconds
	# unit = 3 -> units of 104 milliseconds, 4 -> units of 25 microseconds	
	def configPulser(self,handle,pulSel,period,width,unit,pulseNum,start,reset):

		cPulSel = ctypes.c_uint(pulSel)
		cPeriod = ctypes.c_ubyte(period)
		cWidth = ctypes.c_ubyte(width)
		cUnit = ctypes.c_uint(unit)
		cPulseNum = ctypes.c_uint(pulseNum)
		cStart = ctypes.c_uint(start)
		cReset = ctypes.c_uint(reset)

		pyVMEconfigPulser = CAENVMELib.CAENVME_SetPulserConf
		pyVMEconfigPulser.argtypes = [ctypes.c_int,ctypes.c_uint,ctypes.c_ubyte,ctypes.c_ubyte,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint]
		pyVMEconfigPulser.restype = ctypes.c_int

		ret = pyVMEconfigPulser(handle,cPulSel,cPeriod,cWidth,cUnit,cPulseNum,cStart,cReset)
		
		if debug:
			print("ret in configPulser: ",ret)
			print(VMEcodes[ret])

	#Start pulser via software
	def startPulser(self,handle,pulSel):

		cPulSel = ctypes.c_uint(pulSel)

		pyVMEstartPulser = CAENVMELib.CAENVME_StartPulser
		pyVMEstartPulser.argtypes = [ctypes.c_int,ctypes.c_uint]
		pyVMEstartPulser.restype = ctypes.c_int

		ret = pyVMEstartPulser(handle,cPulSel)
		if debug:
			print("ret in startPulser:2",ret)
			print(VMEcodes[ret])

	#Stop pulser via software
	def stopPulser(self,handle,pulSel):

		cPulSel = ctypes.c_uint(pulSel)

		pyVMEstopPulser = CAENVMELib.CAENVME_StopPulser
		pyVMEstopPulser.argtypes = [ctypes.c_int,ctypes.c_uint]
		pyVMEstopPulser.restype = ctypes.c_int

		ret = pyVMEstopPulser(handle,cPulSel)
		
		if debug:
			print("ret in stopPulser",ret)
			print(VMEcodes[ret])

	#Set configuration of bridge output
	def setOutputConf(self,handle,outputSel,outputPol,ledPolarity,ioSource):

		cOutputSel = ctypes.c_uint(outputSel)
		cOutputPol = ctypes.c_uint(outputPol)
		cLedPolarity = ctypes.c_uint(ledPolarity)
		cIOsource = ctypes.c_uint(ioSource)

		pyVMEsetOutputConf = CAENVMELib.CAENVME_SetOutputConf
		pyVMEsetOutputConf.argtypes = [ctypes.c_int,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint]
		pyVMEsetOutputConf.restype = ctypes.c_int

		ret = pyVMEsetOutputConf(handle,cOutputSel,cOutputPol,cLedPolarity,cIOsource)
		
		if debug:
			print("ret in setOutputConf: ",ret)
			print(VMEcodes[ret])

	def confScaler(self,handle,limit,autoReset,hit,gate,reset):
		cLimit = ctypes.c_short(limit)
		cAutoReset = ctypes.c_short(autoReset)
		cHit = ctypes.c_uint(hit)
		cGate = ctypes.c_uint(gate)
		cReset = ctypes.c_uint(reset)

		pyVMEconfScaler = CAENVMELib.CAENVME_SetScalerConf
		pyVMEconfScaler.argtypes = [ctypes.c_int,ctypes.c_short,ctypes.c_short,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint]
		pyVMEconfScaler.restype = ctypes.c_int

		ret = pyVMEconfScaler(handle,cLimit,cAutoReset,cHit,cGate,cReset)
		
		if debug:
			print("ret in confScaler",ret)
			print(VMEcodes[ret])

		
	def resetScalerCount(self,handle):

		pyVMEresetScalerCount = CAENVMELib.CAENVME_ResetScalerCount
		pyVMEresetScalerCount.argtypes = [ctypes.c_int]
		pyVMEresetScalerCount.restype = ctypes.c_int
        
		ret = pyVMEresetScalerCount(handle)
		
		if debug:
			print("ret in resetScalerCount: ",ret)
			print(VMEcodes[ret])

	def enableScalerGate(self,handle):

		pyVMEenableScalerGate = CAENVMELib.CAENVME_EnableScalerGate
		pyVMEenableScalerGate.argtypes = [ctypes.c_int]
		pyVMEenableScalerGate.restype = ctypes.c_int

		ret = pyVMEenableScalerGate(handle)
		
		if debug:
			print("ret in enableScalerGate",ret)
			print(VMEcodes[ret])

	def disableScalerGate(self,handle):

		pyVMEdisableScalerGate = CAENVMELib.CAENVME_DisableScalerGate
		pyVMEdisableScalerGate.argtypes = [ctypes.c_int]
		pyVMEdisableScalerGate.restype = ctypes.c_int

		ret = pyVMEdisableScalerGate(handle)
		
		if debug:
			print("ret in disableScalerGate",ret)
			print(VMEcodes[ret])

	##############################
	#                            #
	#VME bridge internal register#
	#                            #
	##############################

	#Read bridge internal register
	def readRegister(self,handle,reg):
    
		cReg = ctypes.c_uint(reg)

		pyVMEreadRegister = CAENVMELib.CAENVME_ReadRegister
		pyVMEreadRegister.argtypes = [ctypes.c_int,ctypes.c_uint]
		pyVMEreadRegister.restype = ctypes.c_int

		cData = ctypes.c_uint()

		ret = pyVMEreadRegister(handle,cReg,ctypes.pointer(cData))

		if ret != 0:
			print("Error while reading bridge register:",VMEcodes[ret])

		if debug:
			print("ret in readRegister",ret)
			print(VMEcodes[ret])
			print("Scaler count (hex string): ",hex(cData.value))

		return cData.value

	#Write bridge internal register
	def writeRegister(self,handle,reg,data):

		cReg = ctypes.c_uint(reg)
		cData = ctypes.c_uint(data)

		pyVMEwriteRegister = CAENVMELib.CAENVME_WriteRegister
		pyVMEwriteRegister.argtypes = [ctypes.c_int,ctypes.c_uint,ctypes.c_uint]
		pyVMEwriteRegister.restype = ctypes.c_int

		ret = pyVMEwriteRegister(handle,cReg,cData)

		if debug:
			print("ret in writeRegister: ",ret)
			print(VMEcodes[ret])

	#######################
	#                     #
	#IRQ-related functions#
	#                     #
	#######################


	#Enable IRQ status check
	def enableIRQ(self,handle,mask):

		cMask = ctypes.c_int(mask)

		pyVMEenableIRQ = CAENVMELib.CAENVME_IRQEnable
		pyVMEenableIRQ.argtypes = [ctypes.c_int,ctypes.c_int]
		pyVMEenableIRQ.restype = ctypes.c_int

		ret = pyVMEenableIRQ(handle,cMask)
		
		if debug:
			print("ret in enableIRQ: ",ret)
			print(VMEcodes[ret])

		print("Enabling IRQ on lines",mask)

	#Disable IRQ check
	def disableIRQ(self,handle,mask):

		cMask = ctypes.c_int(mask)

		pyVMEdisableIRQ = CAENVMELib.CAENVME_IRQDisable
		pyVMEdisableIRQ.argtypes = [ctypes.c_int,ctypes.c_int]
		pyVMEdisableIRQ.restype = ctypes.c_int

		ret = pyVMEdisableIRQ(handle,cMask)
		
		if debug:
			print("ret in disableIRQ",ret)
			print(VMEcodes[ret])

		print("Disabling IRQ on lines",mask)

	
	#Check IRQ status
	def checkIRQ(self,handle):

		cMaskOut = ctypes.c_int()

		pyVMEcheckIRQ = CAENVMELib.CAENVME_IRQCheck
		pyVMEcheckIRQ.argtypes = [ctypes.c_int,ctypes.POINTER(ctypes.c_int)]
		pyVMEcheckIRQ.restype = ctypes.c_int

		ret = pyVMEcheckIRQ(handle,ctypes.pointer(cMaskOut))
		
		if ret != 0:
			print("Error in checkIRQ: ",VMEcodes[ret])
			sys.exit("Exiting")
		
		if debug:
			print("ret in checkIRQ",ret)
			print(VMEcodes[ret])
			print("checkIRQ result (hex string)",hex(cMaskOut.value))

		return cMaskOut.value

	#Perform IACK cycle
	def iackCycle(self,handle,IRQlevel,DW):

		cIRQlevel = ctypes.c_uint(IRQlevel)
		cDW = ctypes.c_uint(DW)
		cData = ctypes.c_uint()

		pyVMEintAck = CAENVMELib.CAENVME_IACKCycle
		pyVMEintAck.argtypes = [ctypes.c_int,ctypes.c_uint,ctypes.c_void_p,ctypes.c_uint]
		pyVMEintAck.restype = ctypes.c_int

		ret = pyVMEintAck(handle,cIRQlevel,ctypes.pointer(cData),cDW)
		
		if debug:
			print("ret in iackCycle: ",ret)
			print(VMEcodes[ret])
			print("iackCycle result (hex string): ",hex(cData.value))
		
		return hex(cData.value)

	#Wait for IRQ
	def waitForIRQ(self,handle,mask,time):

		cMask = ctypes.c_uint32(mask)
		cTime = ctypes.c_uint32(time)

		pyVMEwaitForIRQ = CAENVMELib.CAENVME_IRQWait
		pyVMEwaitForIRQ.argtypes = [ctypes.c_int,ctypes.c_uint32,ctypes.c_uint32]
		pyVMEwaitForIRQ.restype = ctypes.c_int

		ret = pyVMEwaitForIRQ(handle,cMask,cTime)
		
		if debug:
			print("ret in waitIRQ: ",ret)
			print(VMEcodes[ret])

