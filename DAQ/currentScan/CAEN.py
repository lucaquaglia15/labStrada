#Class to use the functions of the CAEN HV wrapper library
import ctypes #for C++ function binding (CAEN HV library for example)
import pathlib
import time
import sys

#import caen HV wrapper library
libname = "/lib/libcaenhvwrapper.so.6.3"
CAENhvLib = ctypes.CDLL(libname)

c_ushort_p = ctypes.POINTER(ctypes.c_ushort)

MAX_ATTEMPTS = 5 #maximum connection trals before giving up

class CAEN:

	#CAEN class constructor
	def __new__(cls, *args, **kwargs):
		return super().__new__(cls)

	def __init__(self, address, user, password):
		self.address = address
		self.user = user
		self.password = password

	def __repr__(self) -> str:
		return f"{type(self).__name__}(address={self.address}, user={self.user}, password={self.password})"

	#Open connection with CAEN module
	def connect(self):
		cIp = ctypes.c_char_p(self.address)
		cUser = ctypes.c_char_p(self.user)
		cPassword = ctypes.c_char_p(self.password)

		handle = ctypes.c_int() #handle defined as int

		#pythonic definition of init system function
		pyCAENinit = CAENhvLib.CAENHV_InitSystem
		pyCAENinit.argtypes = [ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(ctypes.c_int)]
		pyCAENinit.restype = ctypes.c_int
		
		ret = pyCAENinit(0,0,cIp,cUser,cPassword,ctypes.pointer(handle))

		#Connection not yet established, try 5 times and then give up
		attempts = 1 #Keep track of connection attempts 
		while ret != 0:
			if attempts <= MAX_ATTEMPTS:
				print("Connection not yet established")
				print("Retrying:")
				print("Attempt #:",attempts, " out of ",MAX_ATTEMPTS)
				ret = pyCAENinit(0,0,cIp,cUser,cPassword,ctypes.pointer(handle))
				attempts = attempts+1
				time.sleep(2)
			else:
				print("Max number of attempts reached (",MAX_ATTEMPTS,")")
				print("Giving up, check CAEN Connection")
				sys.exit("Exiting current scan")
		
		#print("ret:",ret)	

		#Return the handle for future connection
		return handle


	#disconnect from CAEN HV module
	def disconnect(self,handle):
		pyCAENend = CAENhvLib.CAENHV_DeinitSystem
		pyCAENend.argtypes = [ctypes.c_int]
		pyCAENend.restype = ctypes.c_int
		ret3 = pyCAENend(handle)

	#Set CAEN HV parameter
	def setParameter(self,handle,slot,paramName,channel,paramValue):
		#Define as c++ like variables
		cSlot = ctypes.c_ushort(slot)
		cParamName = ctypes.c_char_p(paramName)
		cChannel = ctypes.c_ushort(channel)

		if isinstance(paramValue,int):
			cParamValue = ctypes.c_int(paramValue)
		else:
			cParamValue = ctypes.c_float(paramValue)

		pyCAENsetChParam = CAENhvLib.CAENHV_SetChParam
		pyCAENsetChParam.argtypes = [ctypes.c_int,ctypes.c_ushort,ctypes.c_char_p,ctypes.c_ushort,c_ushort_p,ctypes.c_void_p]
		pyCAENsetChParam.restype = ctypes.c_int

		ret4 = pyCAENsetChParam(handle,cSlot,cParamName,1,ctypes.pointer(cChannel),ctypes.pointer(cParamValue))

	#Get CAEN HV parameter
	#Status 3 = ramp UP, 1 = ch on, 5 = ramp DOWN
	def getParameter(self,handle,slot,paramName,channel):
		cSlot = ctypes.c_ushort(slot)
		cParamName = ctypes.c_char_p(paramName)
		cChannel = ctypes.c_ushort(channel)

		pyCAENgetChParam = CAENhvLib.CAENHV_GetChParam
		pyCAENgetChParam.argtypes = [ctypes.c_int,ctypes.c_ushort,ctypes.c_char_p,ctypes.c_ushort,c_ushort_p,ctypes.c_void_p]
		pyCAENgetChParam.restype = ctypes.c_int

		if paramName == b"V0Set" or paramName == b"I0Set" or paramName == b"V1Set" or paramName == b"Rup" or paramName == b"RDWn" or paramName == b"Trip" or paramName == b"SVMax" or paramName == b"VMon" or paramName == b"IMon":
			param = (ctypes.c_float*1)()
		elif paramName == b"Status" or paramName == b"Pw" or paramName == b"Pon" or paramName == b"PDwn":
			param = (ctypes.c_int*1)()
		else:
			print("Wrong variable name")
			sys.exit("Exiting current scan")

		ret5 = pyCAENgetChParam(handle,cSlot,cParamName,1,ctypes.pointer(cChannel),ctypes.pointer(param))

		print(param[0])

		return param[0]

	def setChName(self,handle,slot,channel,name):
		cSlot = ctypes.c_ushort(slot)
		cChannel = ctypes.c_ushort(channel)
		cName = ctypes.c_char_p(name)

		pyCAENsetChName = CAENhvLib.CAENHV_SetChName
		pyCAENsetChName.argtypes = [ctypes.c_int,ctypes.c_ushort,ctypes.c_ushort,c_ushort_p,ctypes.c_char_p]
		pyCAENsetChName.restype = ctypes.c_int
		ret2 = pyCAENsetChName(handle,cSlot,1,ctypes.pointer(cChannel),cName)
		