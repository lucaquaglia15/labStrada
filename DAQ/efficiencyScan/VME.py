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

	#Write data at given address
	#handle, address, data, address modifier, data width
	def write(self,handle,baseAddress,address,data,AM,DW):

		#if DW != 0x01 or DW != 0x02 or DW != 0x04 or DW != 0x08:
		#	sys.exit("Sorry wrong data width, exiting")
		print("Type of baseAddress in write function",type(baseAddress))
		print("Type of address in write function",type(address))

		cAddress = ctypes.c_uint32(baseAddress+address)
		cData = ctypes.c_uint(data)
		cAM =  ctypes.c_uint(AM)
		cDW =  ctypes.c_uint(DW)

		print("cAddress in write function",cAddress)
		print("baseAddress in write function",hex(baseAddress))
		print("address in write function",hex(address))
		print("total address in write function",hex(baseAddress + address))

		pyVMEwrite = CAENVMELib.CAENVME_WriteCycle
		pyVMEwrite.argtypes = [ctypes.c_int,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint,ctypes.c_uint]
		pyVMEwrite.restype = ctypes.c_int

		ret2 = pyVMEwrite(handle,cAddress,ctypes.pointer(cData),cAM,cDW)

		print(VMEcodes[ret2])

	#Perform read cycle at given address
	def read(self,handle,baseAddress,address,data,AM,DW):
		
		cAddress = ctypes.c_uint32(baseAddress+address)
		cData = ctypes.c_uint(data)
		cAM =  ctypes.c_uint(AM)
		cDW =  ctypes.c_uint(DW)

		pyVMEread = CAENVMELib.CAENVME_ReadCycle
		pyVMEread.argtypes = [ctypes.c_int,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint,ctypes.c_uint]
		pyVMEread.restype = ctypes.c_int

		ret3 = pyVMEwrite(handle,cAddress,ctypes.pointer(cData),cAM,cDW)

		print(VMEcodes[ret3])

		#return cData.value

	
	#Functions for ease of use with the V2718 module
	def statusRegister(baseAddress,address): #r/w, BA + 0x00, D16

	def controlRegister(): #r/w, BA + 0x01, D16

	def fwRevisionRegister(): #r, BA + 0x02, D16

	def fwDownladRegister(): #r/w, BA + 0x03, D16

	def flashEnableRegister(): #r/w, BA + 0x04, D16

	def IRQStatusRegister(): #r, BA + 0x05, D16

	def IRQMaskRegister(): #r/w, BA + 0x06, D16

	def inputRegister(): #r/w, BA + 0x0A, D16

	def outputSetRegister(): #r/w, BA + 0x0A, D16

	def outputClearRegister(): #w, BA + 0x10, D16

	def inputMultiplexerSetRegister(): #r/w, BA + 0x0B, D16

	def inputMultiplexerClearRegister() #w, BA + 0x11, D16
	