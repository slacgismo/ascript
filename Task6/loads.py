"""County-level load data

Sources:
	Residential - https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2021%2Fresstock_amy2018_release_1%2F
	Commercial - https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2021%2Fcomstock_amy2018_release_1%2F
"""
import pandas as pd
import json

REFYEAR=2018
CACHE={} # None disables caching
WEATHER=f"https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/resstock_amy{REFYEAR}_release_1/weather/amy{REFYEAR}"
RESIDENTIAL=f"https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/resstock_amy{REFYEAR}_release_1/timeseries_aggregates/by_county/state="
COMMERCIAL=f"https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/comstock_amy{REFYEAR}_release_1/timeseries_aggregates/by_county/state="
TZSPEC = {
	"US/Atlantic" : -4,
	"US/Eastern" : -5,
	"US/Central" : -6,
	"US/Mountain" : -7,
	"US/Pacific" : -8,
	"US/Alaska" : -9,
	"US/Hawaii" : -10,
}
TZINFO = {
	"AL":"US/Central", #	State; counties
	"AK":"US/Alaska", #	State; boroughs
	"AZ":"US/Mountain", #	State; counties
	"AR":"US/Central", #	State; counties
	"CA":"US/Pacific", #	State; counties
	"CO":"US/Mountain", #	State; counties
	"CT":"US/Eastern", #	State; counties
	"DE":"US/Eastern", #	State; counties
	"DC":"US/Eastern", #	Federal district[4]
	"FL":"US/Eastern", #	State; counties
	"GA":"US/Eastern", #	State; counties
	"HI":"US/Hawaii", #	State; counties
	"ID":"US/Mountain", #	State; counties
	"IL":"US/Central", #	State; counties
	"IN":"US/Eastern", #	State; counties
	"IA":"US/Central", #	State; counties
	"KS":"US/Central", #	State; counties
	"KY":"US/Central", #	State; counties
	"LA":"US/Central", #	State; parishes
	"ME":"US/Eastern", #	State; counties
	"MD":"US/Eastern", #	State; counties
	"MA":"US/Eastern", #	State; counties
	"MI":"US/Eastern", #	State; counties
	"MN":"US/Central", #	State; counties
	"MS":"US/Central", #	State; counties
	"MO":"US/Central", #	State; counties
	"MT":"US/Mountain", #	State; counties
	"NE":"US/Central", #	State; counties
	"NV":"US/Pacific", #	State; counties
	"NH":"US/Eastern", #	State; counties
	"NJ":"US/Eastern", #	State; counties
	"NM":"US/Mountain", #	State; counties
	"NY":"US/Eastern", #	State; counties
	"NC":"US/Eastern", #	State; counties
	"ND":"US/Mountain", #	State; counties
	"OH":"US/Eastern", #	State; counties
	"OK":"US/Central", #	State; counties
	"OR":"US/Pacific", #	State; counties
	"PA":"US/Eastern", #	State; counties
	"PR":"US/Atlantic", #	Outlying area under U.S. sovereignty
	"RI":"US/Eastern", #	State; counties
	"SC":"US/Eastern", #	State; counties
	"SD":"US/Central", #	State; counties
	"TN":"US/Central", #	State; counties
	"TX":"US/Central", #	State; counties
	"UT":"US/Mountain", #	State; counties
	"VT":"US/Eastern", #	State; counties
	"VA":"US/Eastern", #	State; counties
	"WA":"US/Pacific", #	State; counties
	"WV":"US/Eastern", #	State; counties
	"WI":"US/Central", #	State; counties
	"WY":"US/Mountain", #	State; counties
	}
STATEFIPS = {
	"AL":"01", #	State; counties
	"AK":"02", #	State; boroughs
	"AZ":"04", #	State; counties
	"AR":"05", #	State; counties
	"CA":"06", #	State; counties
	"CO":"08", #	State; counties
	"CT":"09", #	State; counties
	"DE":"10", #	State; counties
	"DC":"11", #	Federal district[4]
	"FL":"12", #	State; counties
	"GA":"13", #	State; counties
	"HI":"15", #	State; counties
	"ID":"16", #	State; counties
	"IL":"17", #	State; counties
	"IN":"18", #	State; counties
	"IA":"19", #	State; counties
	"KS":"20", #	State; counties
	"KY":"21", #	State; counties
	"LA":"22", #	State; parishes
	"ME":"23", #	State; counties
	"MD":"24", #	State; counties
	"MA":"25", #	State; counties
	"MI":"26", #	State; counties
	"MN":"27", #	State; counties
	"MS":"28", #	State; counties
	"MO":"29", #	State; counties
	"MT":"30", #	State; counties
	"NE":"31", #	State; counties
	"NV":"32", #	State; counties
	"NH":"33", #	State; counties
	"NJ":"34", #	State; counties
	"NM":"35", #	State; counties
	"NY":"36", #	State; counties
	"NC":"37", #	State; counties
	"ND":"38", #	State; counties
	"OH":"39", #	State; counties
	"OK":"40", #	State; counties
	"OR":"41", #	State; counties
	"PA":"42", #	State; counties
	"PR":"72", #	Outlying area under U.S. sovereignty
	"RI":"44", #	State; counties
	"SC":"45", #	State; counties
	"SD":"46", #	State; counties
	"TN":"47", #	State; counties
	"TX":"48", #	State; counties
	"UT":"49", #	State; counties
	"VT":"50", #	State; counties
	"VA":"51", #	State; counties
	"WA":"53", #	State; counties
	"WV":"54", #	State; counties
	"WI":"55", #	State; counties
	"WY":"56", #	State; counties	
}
COUNTYFIPS = pd.read_csv("fips.csv",header=0,names=["fips","county","state"],dtype='str').dropna().set_index(["state","county"])
COUNTYFIPS['fips'] = [f"{int(x[:-3]):02d}{int(x[-3:])*10:05d}" for x in COUNTYFIPS['fips']]

WEATHER_COLUMNS = {
	"Dry Bulb Temperature [°C]":"drybulb[degC]",
	"Relative Humidity [%]":"humidity[%]",
	"Wind Speed [m/s]":"windvel[m/s]",
	"Wind Direction [Deg]":"windir[deg]",
	"Global Horizontal Radiation [W/m2]":"ghr[W/m^2]",
	"Direct Normal Radiation [W/m2]":"dnr[W/m^2]",
	"Diffuse Horizontal Radiation [W/m2]":"dhr[W/m^2]",
	}
RESIDENTIAL_COLUMNS = {
    "timestamp":"timestamp",
    "units_represented":"floorarea[sf]",
    "out.electricity.total.energy_consumption":"electric[kW]",
    "out.fuel_oil.total.energy_consumption":"oil[kW]",
    "out.natural_gas.total.energy_consumption":"gas[kW]",
    "out.propane.total.energy_consumption":"propane[kW]",
    "out.site_energy.total.energy_consumption":"total[kW]",
}
COMMERCIAL_COLUMNS = {
    "timestamp":"timestamp",
    "floor_area_represented":"floorarea[sf]",
    "out.electricity.total.energy_consumption":"electric[kW]",
    "out.natural_gas.total.energy_consumption":"gas[kW]",
    "out.site_energy.total.energy_consumption":"total[kW]",
}

# residential building types
MOBILEHOME = "mobile_home"
CONDOMINIUM = "multi-family_with_2_-_4_units"
APARTMENT = "multi-family_with_5plus_units"
TOWNHOUSE = "single-family_attached"
HOUSE = "single-family_detached"

# commercial building types
RESTAURANT = "fullservicerestaurant"
HOSPITAL = "hospital"
LARGEHOTEL = "largehotel"
LARGEOFFICE = "largeoffice"
MEDIUMOFFICE = "mediumoffice"
OUTPATIENT = "outpatient"
PRIMARYSCHOOL = "primaryschool"
FASTFOOD = "quickservicerestaurant"
SMALLRETAIL = "retailstandalone"
MEDIUMRETAIL = "retailstripmall"
SECONDARYSCHOOL = "secondaryschool"
SMALLHOTEL = "smallhotel"
SMALLOFFICE = "smalloffice"
WAREHOUSE = "warehouse"

def get_states():
	"""Get list of states"""
	return list(COUNTYFIPS.index.get_level_values(0).unique())

def get_counties(state):
	"""Get list of counties"""
	return list(COUNTYFIPS.loc[state].index)

def get_buildings(sector):
	"""Get list of building types"""
	if sector == "residential":
		return [MOBILEHOME,CONDOMINIUM,APARTMENT,TOWNHOUSE,HOUSE]
	elif sector == "commercial":
		return [
			RESTAURANT,HOSPITAL,LARGEHOTEL,LARGEOFFICE,
			MEDIUMOFFICE,OUTPATIENT,PRIMARYSCHOOL,FASTFOOD,
			SMALLRETAIL,MEDIUMRETAIL,SECONDARYSCHOOL,SMALLHOTEL,
			SMALLOFFICE,WAREHOUSE,
			]
	else:
		return []

def get_weather(state,county):
	"""Get weather data for a county"""
	fips = f"{COUNTYFIPS.loc[state,county]['fips']}"
	tzname = TZINFO[state]
	url = f"{WEATHER}/G{fips}_{REFYEAR}.csv"
	data = pd.read_csv(url,
		index_col=[0],
		parse_dates=[0],
		)
	data.columns=[WEATHER_COLUMNS[x] if x in WEATHER_COLUMNS else x for x in data.columns]
	data.index = (data.index.tz_localize("UTC") + pd.Timedelta(hours=-TZSPEC[tzname]-1)).tz_convert(tzname)
	data.index.name="timestamp"
	return data.round(1)

def get_data(sector,url,tzname):
	columns = {"residential":RESIDENTIAL_COLUMNS,"commercial":COMMERCIAL_COLUMNS}[sector]
	data = pd.read_csv(url,
		usecols=list(columns),
		index_col=[0],
		parse_dates=[0],
		)
	data.columns=[columns[x] if x in columns else x for x in data.columns]
	data.index = (data.index.tz_localize("UTC") + pd.Timedelta(hours=-TZSPEC[tzname]-1,minutes=45)).tz_convert(tzname)
	data = data.resample("1h").sum()
	return data

def get_residential(state,county,building_type=None):
	"""Get residential loads"""
	fips = f"{COUNTYFIPS.loc[state,county]['fips']}"
	tzname = TZINFO[state]
	if building_type is None:
		building_type = {x:1.0 for x in get_buildings("residential")}
	result = None
	for bt,wt in building_type.items() if type(building_type) is dict else {building_type:1.0}.items():
		key = f"{fips}-R"
		if not CACHE is None and not key in CACHE:
			url = f"{RESIDENTIAL}{state}/g{fips}-{bt}.csv"
			CACHE[key] = data =  get_data("residential",url,tzname)
		else:
			data = CACHE[key]
		if result is None:
			result = data*wt
		else:
			result += data*wt
	return result.round(1)

def get_commercial(state,county,building_type=None):
	"""Get residential loads"""
	fips = f"{COUNTYFIPS.loc[state,county]['fips']}"
	tzname = TZINFO[state]
	if building_type is None:
		building_type = {x:1.0 for x in get_buildings("commercial")}
	result = None
	for bt,wt in building_type.items() if type(building_type) is dict else {building_type:1.0}.items():
		key = f"{fips}-C"
		if not CACHE is None and not key in CACHE:
			url = f"{COMMERCIAL}{state}/g{fips}-{bt}.csv"
			CACHE[key] = data = get_data("commercial",url,tzname)
		else:
			data = CACHE[key]
		if result is None:
			result = data*wt
		else:
			result += data*wt
	return result.round(1)

if __name__ == "__main__":

	# pd.options.display.max_columns = None
	# pd.options.display.width = None

	# verify the data can be retrieved and hasn't changed
	assert(len(get_states())==51)
	assert(len(get_counties("CA"))==58)
	assert(len(get_weather("CA","Alameda County"))==8760)
	assert(len(get_residential("CA","San Mateo County",HOUSE))==8760)
	assert(get_residential("CA","San Mateo County",HOUSE)["electric[kW]"].iloc[0]==182601.2)
	assert(len(get_commercial("CA","San Mateo County",LARGEOFFICE))==8760)
	assert(get_commercial("CA","San Mateo County",LARGEOFFICE)["electric[kW]"].iloc[0]==12119.8)
