#Class to use the functions of the CAEN VME library to communicate with bridge
import ctypes #for C++ function binding (CAEN HV library for example)
import pathlib
import time
import sys

#import caen HV wrapper library
libname = "/usr/lib/libCAENVME.so.v3.4.1"
CAENVMELib = ctypes.CDLL(libname)

#VME error codes dictionary
#VMEcodes = {0:"Success",-1:"Bus Error",-2:"Communnication Error",-3:"Generic Error",
#-4:"Invalid Parameter",-5:"Timeout Error",-6:"Already Open Error",
#-7:"Max Board Count Error",-8:"Not Supported"}

VMEcodes = {0:"cvSuccess",-1:"cvBusError",-2:"cvCommError",-3:"cvGenericError",
-4:"cvInvalidParameter",-5:"cvTimeoutError",-6:"cvAlreadyOpenError",
-7:"cvMaxBoardCountError",-8:"cvNotSupported"}

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

	#Functions from the CAEN VME library

	#Open connection with VME bridge
	def connect(self):

		#Board not implemented, shut down program
		if self.boardType < 0 or self.boardType > 1:
			print("Sorry board not implemented")
			sys.exit("Exiting DAQ scan")

		#pythonic definition of function arguments
		cBoardType = ctypes.c_int(self.boardType)
		cLinkNumber = ctypes.c_uint32(self.linkNumber)
		cConetNode = ctypes.c_short(self.conetNode)
		handle = ctypes.c_int() #handle defined as int

		pyVMEinit = CAENVMELib.CAENVME_Init2
		pyVMEinit.argtypes = [ctypes.c_int,ctypes.c_void_p,ctypes.c_short,ctypes.POINTER(ctypes.c_int)]
		pyVMEinit.restype = ctypes.c_int

		ret = pyVMEinit(cBoardType,ctypes.pointer(cLinkNumber),cConetNode,ctypes.pointer(handle))

		print(VMEcodes[ret])

		return handle
	
	def disconnect(self,handle):

		pyVMEend = CAENVMELib.CAENVME_End
		pyVMEend.argtypes = [ctypes.c_int]
		pyVMEend.restype = ctypes.c_int

		ret2 = pyVMEend(handle)

		print(VMEcodes[ret2])

	#Write data at given address
	#handle, address, data, address modifier, data width
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

		ret3 = pyVMEwrite(handle,cAddress,ctypes.pointer(cData),cAM,cDW)

		print(VMEcodes[ret3])

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

		ret4 = pyVMEread(handle,cAddress,ctypes.pointer(cData),cAM,cDW)

		print(VMEcodes[ret4])
		print("Result of read",hex(cData.value))
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

		ret5 = pyVMEconfigPulser(handle,cPulSel,cPeriod,cWidth,cUnit,cPulseNum,cStart,cReset)
		print("ret5",ret5)
		print(VMEcodes[ret5])

	#Start pulser via software
	def startPulser(self,handle,pulSel):

		cPulSel = ctypes.c_uint(pulSel)

		pyVMEstartPulser = CAENVMELib.CAENVME_StartPulser
		pyVMEstartPulser.argtypes = [ctypes.c_int,ctypes.c_uint]
		pyVMEstartPulser.restype = ctypes.c_int

		ret6 = pyVMEstartPulser(handle,cPulSel)
		print("ret6",ret6)
		print(VMEcodes[ret6])

	#Stop pulser via software
	def stopPulser(self,handle,pulSel):

		cPulSel = ctypes.c_uint(pulSel)

		pyVMEstopPulser = CAENVMELib.CAENVME_StopPulser
		pyVMEstopPulser.argtypes = [ctypes.c_int,ctypes.c_uint]
		pyVMEstopPulser.restype = ctypes.c_int

		ret7 = pyVMEstopPulser(handle,cPulSel)
		print("ret7",ret7)
		print(VMEcodes[ret7])

	#Set configuration of bridge output
	def setOutputConf(self,handle,outputSel,outputPol,ledPolarity,ioSource):

		cOutputSel = ctypes.c_uint(outputSel)
		cOutputPol = ctypes.c_uint(outputPol)
		cLedPolarity = ctypes.c_uint(ledPolarity)
		cIOsource = ctypes.c_uint(ioSource)

		pyVMEsetOutputConf = CAENVMELib.CAENVME_SetOutputConf
		pyVMEsetOutputConf.argtypes = [ctypes.c_int,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint]
		pyVMEsetOutputConf.restype = ctypes.c_int

		ret7 = pyVMEsetOutputConf(handle,cOutputSel,cOutputPol,cLedPolarity,cIOsource)
		print("ret7",ret7)
		print(VMEcodes[ret7])

	#Enable IRQ status check
	def enableIRQ(self,handle,mask):

		cMask = ctypes.c_int(mask)

		pyVMEenableIRQ = CAENVMELib.CAENVME_IRQEnable
		pyVMEenableIRQ.argtypes = [ctypes.c_int,ctypes.c_int]
		pyVMEenableIRQ.restype = ctypes.c_int

		ret8 = pyVMEenableIRQ(handle,cMask)
		print("ret8",ret8)
		print(VMEcodes[ret8])

	
	#Check IRQ status
	def checkIRQ(self,handle):

		cMaskOut = ctypes.c_int()

		pyVMEcheckIRQ = CAENVMELib.CAENVME_IRQCheck
		pyVMEcheckIRQ.argtypes = [ctypes.c_int,ctypes.POINTER(ctypes.c_int)]
		pyVMEcheckIRQ.restype = ctypes.c_int

		ret9 = pyVMEcheckIRQ(handle,ctypes.pointer(cMaskOut))
		print(hex(cMaskOut.value))
		print("ret9",ret9)
		print(VMEcodes[ret9])
		return cMaskOut.value

	def IRQacknowledge(hself,handle,IRQlevel,DW):

		cIRQlevel = ctypes.c_uint(IRQlevel)
		cDW = ctypes.c_uint(DW)

		ret10 = pyVMEintAck = CAENVMELib.CAENVME_IACKCycle
		pyVMEintAck.argtypes = [ctypes.c_int]
		pyVMEintAck.restype = ctypes.c_int

		ret10 = pyVMEintAck()
		print("ret10",ret10)
		print(VMEcodes[ret10])

	def waitForIRQ(self,handle,mask,time):

		cMask = ctypes.c_uint32(mask)
		cTime = ctypes.c_uint32(time)

		pyVMEwaitForIRQ = CAENVMELib.CAENVME_IRQWait
		pyVMEwaitForIRQ.argtypes = [ctypes.c_int,ctypes.c_uint32,ctypes.c_uint32]
		pyVMEwaitForIRQ.restype = ctypes.c_int

		ret11 = pyVMEwaitForIRQ(handle,cMask,cTime)
		print("ret11",ret11)
		print(VMEcodes[ret11])

	def confScaler(self,handle,limit,autoReset,hit,gate,reset):
		cLimit = ctypes.c_short(limit)
		cAutoReset = ctypes.c_short(autoReset)
		cHit = ctypes.c_uint(hit)
		cGate = ctypes.c_uint(gate)
		cReset = ctypes.c_uint(reset)

		pyVMEconfScaler = CAENVMELib.CAENVME_SetScalerConf
		pyVMEconfScaler.argtypes = [ctypes.c_int,ctypes.c_short,ctypes.c_short,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint]
		pyVMEconfScaler.restype = ctypes.c_int

		ret12 = pyVMEconfScaler(handle,cLimit,cAutoReset,cHit,cGate,cReset)
		print("ret12",ret12)
		print(VMEcodes[ret12])

		
	def resetScalerCount(self,handle):

		pyVMEresetScalerCount = CAENVMELib.CAENVME_ResetScalerCount
		pyVMEresetScalerCount.argtypes = [ctypes.c_int]
		pyVMEresetScalerCount.restype = ctypes.c_int
        
		ret13 = pyVMEresetScalerCount(handle)
		print("ret13",ret13)
		print(VMEcodes[ret13])

	def enableScalerGate(self,handle):

		pyVMEenableScalerGate = CAENVMELib.CAENVME_EnableScalerGate
		pyVMEenableScalerGate.argtypes = [ctypes.c_int]
		pyVMEenableScalerGate.restype = ctypes.c_int

		ret14 = pyVMEenableScalerGate(handle)
		print("ret14",ret14)
		print(VMEcodes[ret14])

	def disableScalerGate(self,handle):

		pyVMEdisableScalerGate = CAENVMELib.CAENVME_DisableScalerGate
		pyVMEdisableScalerGate.argtypes = [ctypes.c_int]
		pyVMEdisableScalerGate.restype = ctypes.c_int

		ret15 = pyVMEdisableScalerGate(handle)
		print("ret15",ret15)
		print(VMEcodes[ret15])


	def readRegister(self,handle,reg):
    
		cReg = ctypes.c_uint(reg)

		pyVMEreadRegister = CAENVMELib.CAENVMEReadRegister
		pyVMEreadRegister.argtypes = [ctypes.c_int,cReg]
		pyVMEreadRegister.restype = ctypes.c_int

		cData = ctypes.c_uint()

		ret16 = pyVMEreadRegister(handle,cReg,ctypes.pointer(cData))

		print("ret16",ret16)
		print(VMEcodes[ret16])
		print("Result of read bridge register",cData.value)

		return cData.value
