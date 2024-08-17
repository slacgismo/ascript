"""ASCRIPT Scenario Data Handling"""
import os, sys
import filelock as fl
import json
import datetime as dt
import git
import platform
import socket

# app info
__rootdir__ = os.path.realpath("..") if os.path.basename(os.getcwd()) == "Task6" else os.realpath(".")
__appname__ = "ascript"
__version__ = "0.0.0"

# repo info
try:
	__repo__ = git.Repo(__rootdir__)
	__branch__ = str(__repo__.active_branch)
	__commit__ = __repo__.active_branch.commit
	__build__ = str(dt.datetime.fromtimestamp(__commit__.committed_date).strftime("%y%m%d"))
except:
	__branch__ = None
	__commit__ = None
	__build__ = "local"

# user info
__user__ = os.getenv("USER")
__host__ = socket.gethostname()
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
	try:
		s.connect(("8.8.8.8",80))
		__ipaddr__ = s.getsockname()[0]
		s.close()
	except:
		__ipaddr__ = "127.0.0.1"
	try:
		__domain__ = socket.gethostbyaddr(__ipaddr__)[0].split('.',1)[1]
	except:
		__domain__ = "localhost"

class Scenario:
	"""API for scenario files
	
	Properties:
	created (datetime) - datetime scenario was created
	modified (datetime) - datetime scenario was modified
	accessed (datetime) - datetime scenario was accessed
	"""
	NEWFILE = "Untitled"
	NEWDATA = {

		# location
		"state" : "CA",
		"county" : "ORANGE",
		"city" : "SANTA ANA",
		"substations" : [],
	
		# demand
		"study-year" : dt.datetime.now().year+10,
		"ev-adoption-rate" : "Low (100-1,000)",
		"number-of-evs" : 500,
		"number-of-chargers" : 500,
		"charge-timers-enabled" : False,

		# supply
		"public-fraction" : 30.0,
		"commercial-fraction" : 30.0,
		"residential-fraction" : 40.0,
		"public-sector" : "Commercial",
		"commercial-sector" : "Commercial",
		"residential-sector" : "Residential",
		"public-tariff" : "General Service Time-of-use Electric Vehicle Charging: TOU-EV-3",
		"commercial-tariff" : "General Service Time-of-use Electric Vehicle Charging - Demand Metered:TOU-EV-4",
		"residential-tariff" : "Domestic Time-of-Use Electric Vehicle Charging: TOU-EV-1",

		# feeder
		"feeder-import-capacity" : 66.0,
		"feeder-export-capacity" : 0.0,
		"peak-load-fraction" : 1.0,

		# renewables
		"distributed-power-resources" : True,
		"solar-installed-capacity" : 0.0,
		"wind-installed-capacity" : 0.0,

		# storage
		"distributed-energy-resources" : True,
		"storage-power-capacity" : 0.0,
		"storage-energy-capacity" : 0.0,

		# loads
		"load-growth-rate" : 3.0,
		"residential-gas-electrification-rate" : 50.0,
		"residential-oil-electrification-rate" : 50.0,
		"residential-propane-electrification-rate" : 50.0,
		"residential-gas-electrification-impact" : 50.0,
		"residential-oil-electrification-impact" : 50.0,
		"residential-propane-electrification-impact" : 50.0,
		"commercial-gas-electrification-rate" : 50.0,
		"commercial-gas-electrification-impact" : 50.0,
	}

	def __init__(self,
			data: dict = None,
			*,
			file: str = None,
			):
		"""Construct a scenario handler

		Parameters:
		data (dict): data default template
		file (str): filename to use (default is Untitled_<num>.ascript)
		"""
		if file is None:
			n = 1
			while os.path.exists(file:=f"{self.NEWFILE}_{n}.{__appname__}"):
				n = n+1
			self.data = self.NEWDATA
			for x in ["created","modified","accessed"]:
				setattr(self,x,dt.datetime.now())
			self.save(file)
		else:
			self.load(file)
	
	def save(self,file=None):
		"""Save scenario to file

		Parameters:
		file (str): filename to use (default is scenario filename)
		"""
		if file:
			self.file = file
		content = dict(
			application=__appname__,
			version=dict(
				number=__version__,
				build=__build__,
				branch=__branch__,
				commit=str(__commit__) if __commit__ else None
				),
			creator=f"""{__user__}@{__host__}.{__domain__}""",
			created=self.created.isoformat(),
			modified=self.modified.isoformat(),
			accessed=self.accessed.isoformat(),
			platform=platform.platform(),
			data=self.data,
			)
		with open(self.file,"w") as fh:
			json.dump(content,fh,indent=4)

	def load(self,file=None) -> dict:
		"""Load scenario from file

		Parameters:
		file (str): filename to use (default is scenario filename)
		"""
		if file:
			self.file = file
		with open(self.file,"r") as fh:
			content = json.load(fh)
			assert(content["application"]==__appname__)
			for x in ["created","modified","accessed"]:
				setattr(self,x,dt.datetime.fromisoformat(content[x]))
			self.data = self.NEWDATA
			for key,value in content["data"].items():
				assert key in self.data, f"invalid property key '{key}' in '{self.file}'"
				self.data[key] = value

	def properties(self) -> list:
		"""List of properties in scenario

		"""
		return list(self.data)

	def types(self) -> dict:
		"""Dictionary of property types"""
		return {x:type(y) for x,y in self.data.items()}

	def as_dict(self) -> dict:
		"""Scenario properties as a dictionary"""
		return self.data

	def as_json(self,**kwargs) -> str:
		"""JSON representation of scenario properties

		Parameters:
		kwargs (dict): json.dumps() options
		"""
		return json.dumps(self.data,**kwargs)

	def delete(self):
		"""Delete scenario file"""
		os.remove(self.file)

	def __setitem__(self,name:str,value:any):
		assert name in self.data, f"invalid property name '{name}'"
		assert type(value) == type(self.data[name]), f"invalid property value type '{type(value)}' for property '{name}'"
		self.modified = dt.datetime.now()
		self.data[name] = value

	def __getitem__(self,name:str) -> any:
		assert name in self.data, f"invalid property name '{name}'"
		self.accessed = dt.datetime.now()
		return self.data[name]

	def getctime(self) -> dt.datetime:
		"""Get the scenario creation time"""
		return self.created

	def getmtime(self) -> dt.datetime:
		"""Get the scenario modification time"""
		assert self.modified >= self.created, "invalid modification time"
		return self.modified

	def getatime(self) -> dt.datetime:
		"""Get the scenario access time"""
		assert self.accessed >= self.created, "invalid access time"
		return self.accessed
#
# Self test
#
if __name__ == "__main__":
	from numpy.testing import assert_raises
	try:
		new = Scenario()
		old = Scenario(file=new.file)
		for key in new.properties():
			assert(old[key]==new[key]==Scenario.NEWDATA[key])
		with assert_raises(AssertionError): old["no-such-thing"]
		with assert_raises(AssertionError): old["no-such-thing"] = None
		with assert_raises(AssertionError): old["city"] = None
		assert(old.getctime()<old.getmtime()<old.getatime())
	finally:
		new.delete()
	new.save("/tmp/test.ascript")


