"""ASCRIPT Scenario Data Handling"""
import os, sys
import json
import datetime as dt
import git
import platform
import socket
import typing
import loads
import pandas as pd
from warnings import warn

# app info
__source__ = "Task6" # source folder path relative to project root folder
__rootdir__ = os.path.realpath("..") if os.getcwd().endswith(__source__) else os.realpath(".")
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

def find_file(name,call=None):
	if os.path.exists(name):
		path = name
	elif os.path.exists(os.path.join(__rootdir__,name)):
		path = os.path.join(__rootdir__,name)
	else:
		path = f"https://raw.githubusercontent.com/slacgismo/ascript/{__branch__}/{__source__}/{name}"
	if call:
		return call(path)
	else:
		return path

class ScenarioException(Exception):
	pass

class Scenario:
	"""API for scenario files
	
	Properties:
	created (datetime) - datetime scenario was created
	modified (datetime) - datetime scenario was modified
	accessed (datetime) - datetime scenario was accessed
	file (str) - name of scenario file
	substations (pd.DataFrame) - substation data
	utilities (list[str]) - list of utilities
	data (dict) - scenario data (see NEWDATA for defaults)
	"""
	NEWFILE = "Untitled"
	NEWDATA = {

		# location
		"state" : "CA",
		"county" : "LOS ANGELES",
		"city" : "LOS ANGELES",
		"substations" : [],
		"type": "SUBSTATION",
	
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
			content: dict = None,
			*,
			file: str = None,
			):
		"""Construct a scenario handler

		Parameters:
		data (dict): data default template
		file (str): filename to use (default is Untitled_<num>.ascript)
		"""
		self.comment = ""
		if file is None:
			self.data = self.NEWDATA
			for x in ["created","modified","accessed"]:
				setattr(self,x,dt.datetime.now())
			if not self.NEWFILE is None:
				n = 1
				while os.path.exists(file:=f"{self.NEWFILE}_{n}.{__appname__}"):
					n = n+1
				self.save(file)
			else:
				self.file = "New scenario.ascript"
		else:
			if content is None:
				self.load(file)
			else:
				self.file = file
				self.load_content(content)
		self.substations = None
		self.utilities = None
	
	def save(self,file=None) -> typing.TypeVar('Scenario'):
		"""Save scenario to file

		Parameters:
		file (str): filename to use (default is scenario filename)
		"""
		if file:
			self.file = file
		with open(self.file,"w") as fh:
			json.dump(self.get_content(),fh,indent=4)
		return self

	def load(self,file=None) -> typing.TypeVar('Scenario'):
		"""Load scenario from file

		Parameters:
		file (str): filename to use (default is scenario filename)
		"""
		if file:
			self.file = file
		with open(self.file,"r") as fh:
			self.load_content(json.load(fh))
		return self

	def properties(self) -> dict:
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

	def delete(self) -> None:
		"""Delete scenario file"""
		os.remove(self.file)

	def __setitem__(self,name:str,value:str|float|int) -> None:
		assert name in self.data, f"invalid property name '{name}'"
		assert type(value) == type(self.data[name]), f"invalid property value type '{type(value)}' for property '{name}'"
		self.modified = dt.datetime.now()
		self.data[name] = value

	def __getitem__(self,name:str) -> str|float|int:
		assert name in self.data, f"invalid property name '{name}'"
		self.accessed = dt.datetime.now()
		return self.data[name]

	def set_data(self,data:dict) -> None:
		"""Bulk data update"""
		for key,value in data.items():
			self.__setitem(key,value)

	def load_content(self,content:dict) -> typing.TypeVar('Scenario'):
		"""Load content into scenario

		Parameters:
		content(dict): content data to load

		Returns:
		Scenario: the new scenario object
		"""
		assert(content["application"]==__appname__)
		for x in ["created","modified","accessed"]:
			setattr(self,x,dt.datetime.fromisoformat(content[x]))
		self.data = self.NEWDATA
		self.comment = content["comment"]
		for key,value in content["data"].items():
			assert key in self.data, f"invalid property key '{key}' in '{self.file}'"
			self.data[key] = value
		return self

	def get_content(self) -> dict:
		"""Get the scenario content

		Returns:
		dict: content data
		"""
		return dict(
			application=__appname__,
			version=dict(
				number=__version__,
				build=__build__,
				branch=__branch__,
				commit=str(__commit__) if __commit__ else None
				),
			creator=self.get_author(),
			created=self.created.isoformat(),
			modified=self.modified.isoformat(),
			accessed=self.accessed.isoformat(),
			platform=platform.platform(),
			comment=self.comment,
			data=self.data,
			)

	def get_author(self) -> str:
		"""Get author name

		Returns:
		str: author name
		"""
		return f"""{__user__}@{__host__}.{__domain__}"""

	def get_version(self) -> str:
		"""Get the version used to create the scenario

		Returns:
		str: version ifno
		"""
		return f"{__version__}-{__build__} ({__branch__})"

	def get_platform(self) -> str:
		"""Get the platform on which the scenario was created

		Returns:
		str: platform info
		"""
		return f"{platform.platform()}"

	def get_commit(self) -> str:
		"""Get the github commit which contains the source to the version used to create the scenario

		Returns:
		str: the commit number
		"""
		return f"{str(__commit__) if __commit__ else None}"

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

	def get_substation_data(self) -> pd.DataFrame:
		"""Get the substation data

		Returns:
		pandas.DataFrame: the substation data
		"""
		if self.substations is None:
			self.substations = find_file("substations.csv.gz",
				call=lambda x:pd.read_csv(x,
				    low_memory=False,
				    index_col=["STATE", "COUNTY", "CITY", "TYPE", "NAME"],
					).sort_index())
		return self.substations

	def get_states(self,all:bool=False) -> list[str]:
		"""Get list of states

		Parameters:
		all (bool): return all states instead of only supported states

		Returns:
		list[str]: list of (supported) states
		"""
		return self.get_substation_data().index.get_level_values(0).unique().tolist() if all else self.get_utilities()

	def set_state(self,state:str) -> None:
		"""Set the scenario state

		Parameters:
		state(str): the state to use in the scenario
		"""
		if self.data["state"] != state:
			assert(state in self.get_states())
			self.data["state"] = state
			self.set_county(self.get_counties()[0])

	def get_counties(self,state:str|None=None) -> list[str]:
		"""Get counties in a state

		Parameters:
		state (str): state code, e.g. "CA"

		Returns:
		list[str]: list of county names in the state
		"""
		if state is None:
			state = self.data["state"]
		return self.get_substation_data().loc[state].index.get_level_values(0).unique().tolist()

	def set_county(self,county:str) -> None:
		"""Set the county to use in the scenario

		Parameters:
		county(str): the county name to use in the scenario
		"""
		if self.data["county"] != county:
			assert(county in self.get_counties())
			self.data["county"] = county
			self.set_city(self.get_cities()[0])

	def get_cities(self,state:str|None=None,county:str|None=None) -> list[str]:
		"""Get cities in a county

		Parameters:
		state (str): state code, e.g. "CA"
		county (str): county name, e.g., "ORANGE"

		Returns:
		list[str]: list of city names in the county
		"""
		if state is None:
			state = self.data["state"]
		if county is None:
			county = self.data["county"]
		return self.get_substation_data().loc[state,county].index.get_level_values(0).unique().tolist()

	def set_city(self,city:str) -> None:
		"""Set the city to use in the scenario

		Parameters:
		city(str): the city to use in the scenario
		"""
		if self.data["city"] != city:
			assert(city in self.get_cities())
			self.data["city"] = city
			types = self.get_substation_types()[0]
			self.set_type("SUBSTATION" if "SUBSTATION" in types else types[0])

	def get_substation_types(self,state:str|None=None,county:str|None=None,city:str|None=None) -> list[str]:
		"""Get substation types in a city

		Parameters:
		state (str): state code, e.g. "CA"
		county (str): county name, e.g., "ORANGE"
		city (str): city name, e.g., "SANTA ANA"

		Returns:
		list[str]: list of substation types in the city
		"""
		if state is None:
			state = self.data["state"]
		if county is None:
			county = self.data["county"]
		if city is None:
			city = self.data["city"]
		return self.get_substation_data().loc[state,county,city].index.get_level_values(0).unique().tolist()

	def set_type(self,type:str) -> None:
		"""Change the substation type
		
		Parameters:
		type(str): the substation type to use in the scenario
		"""
		if self.data["type"] != type:
			self.data["type"] = type
			# self.set_substation(self.get_substations()[0])

	def get_substations(self,
			state:str|None=None,
			county:str|None=None,
			city:str|None=None,
			types:str|list[str]=None,
			) -> list[str]:
		"""Get substations in a city

		Parameters:
		state (str): state code, e.g. "CA"
		county (str): county name, e.g., "ORANGE"
		city (str): city name, e.g., "SANTA ANA"
		types (str|list[str]|None): substation types (None is all)

		Returns:
		list[str]: list of substation names in the city
		"""
		if state is None:
			state = self.data["state"]
		if county is None:
			county = self.data["county"]
		if city is None:
			city = self.data["city"]
		if types is None:
			result = self.get_substation_data().loc[state,county,city].index.get_level_values(1).unique().tolist()
		elif type(types) is list:
			result = []
			for st in types:
				result.extend(self.get_substations(state,county,city,st))
		else:
			result = self.get_substation_data().loc[state,county,city,types].index.get_level_values(0).unique().tolist()
		return result

	def get_utilities(self,state:str|None=None) -> list[str]:
		"""Get the utilities in the scenario

		Parameters:
		state(str): state name (default None for all)

		Returns:
		list[str]: list of states
		"""
		if self.utilities is None:
			self.utilities = find_file("utilities.json",
				call=lambda x: json.load(open(x,"r")))
		if state is None:
			return list(self.utilities.keys())
		if not state in self.utilities:
			raise ScenarioException("state not supported")
		return self.utilities[state]

#
# Self test
#
if __name__ == "__main__":

	from numpy.testing import assert_raises
	try:

		# check basic functionalities
		new = Scenario()
		old = Scenario(file=new.file)
		for key in new.properties():
			assert(old[key]==new[key]==Scenario.NEWDATA[key])
		with assert_raises(AssertionError): old["no-such-thing"]
		with assert_raises(AssertionError): old["no-such-thing"] = None
		with assert_raises(AssertionError): old["city"] = None
		assert(old.getctime()<old.getmtime()<old.getatime())

		# check methods
		assert(len(new.get_substation_data())>0)
		assert("CA" in new.get_states())
		assert("ALAMEDA" in new.get_counties("CA"))
		assert("ALISO VIEJO" in new.get_cities("CA","ORANGE"))
		assert("SUBSTATION" in new.get_substation_types("CA","ORANGE","SANTA ANA"))
		assert("CAMDEN" in new.get_substations("CA","ORANGE","SANTA ANA"))
		assert("CAMDEN" in new.get_substations("CA","ORANGE","SANTA ANA","SUBSTATION"))
		assert("CAMDEN" not in new.get_substations("CA","ORANGE","SANTA ANA","RISER"))
		assert("CAMDEN" in new.get_substations("CA","ORANGE","SANTA ANA",["SUBSTATION","RISER"]))
		assert("CA" in new.get_utilities())
		assert("Southern California Edison Co" in new.get_utilities("CA"))

		# check whether public methods have docs
		for item in [getattr(Scenario,x) for x in dir(Scenario) if not x.startswith("_")]:
			if callable(item) and item.__doc__ is None:
				warn(f"{item.__name__} has no documentation")

	finally:
		new.delete()
	new.save("/tmp/test.ascript")


