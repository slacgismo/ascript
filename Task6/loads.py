"""County-level load data"""
import pandas as pd
import json

pd.options.display.max_columns = None
pd.options.display.width = None

REFYEAR=2018
WEATHER=f"https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/resstock_amy{REFYEAR}_release_1/weather/amy{REFYEAR}"
RESIDENTIAL=f"https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/resstock_amy{REFYEAR}_release_1/timeseries_aggregates/by_county/state="
COMMERCIAL=f"https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/comstock_amy{REFYEAR}_release_1/timeseries_aggregates/by_county/state="
TZSPEC = {
	"US/Eastern" : 5,
	"US/Central" : 6,
	"US/Mountain" : 7,
	"US/Pacific" : 8,
}
TZINFO = {"CA":"US/Pacific"}
STATEFIPS = {"CA":"06"}
COUNTYFIPS = pd.read_csv("fips.csv",header=0,names=["fips","county","state"],dtype='str').dropna().set_index(["state","county"])
COUNTYFIPS['fips'] = [f"{int(x[:-3]):02d}{int(x[-3:])*10:05d}" for x in COUNTYFIPS['fips']]
# print(COUNTYFIPS.loc['CA'])

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
}
COMMERCIAL_COLUMNS = {
    "timestamp":"timestamp",
    "floor_area_represented":"floorarea[sf]",
    "out.electricity.total.energy_consumption":"electric[kW]",
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
	data.index = (data.index.tz_localize("UTC") + pd.Timedelta(hours=TZSPEC[tzname]-1)).tz_convert(tzname)
	data.index.name="timestamp"
	return data.round(1)

def get_residential(state,county,building_type=None):
	"""Get residential loads"""
	fips = f"{COUNTYFIPS.loc[state,county]['fips']}"
	tzname = TZINFO[state]
	if building_type is None:
		building_type = {x:1.0 for x in get_buildings("residential")}
	result = None
	for bt,wt in building_type.items() if type(building_type) is dict else {building_type:1.0}.items():
		url = f"{RESIDENTIAL}{state}/g{fips}-{bt}.csv"
		data = pd.read_csv(url,
			usecols=list(RESIDENTIAL_COLUMNS),
			index_col=[0],
			parse_dates=[0],
			)
		data.columns=[RESIDENTIAL_COLUMNS[x] if x in RESIDENTIAL_COLUMNS else x for x in data.columns]
		data.index = (data.index.tz_localize("UTC") + pd.Timedelta(hours=TZSPEC[tzname]-1,minutes=45)).tz_convert(tzname)
		data = data.resample("1h").sum()
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
		url = f"{COMMERCIAL}{state}/g{fips}-{bt}.csv"
		data = pd.read_csv(url,
			usecols=list(COMMERCIAL_COLUMNS),
			index_col=[0],
			parse_dates=[0],
			)
		data.columns=[COMMERCIAL_COLUMNS[x] if x in COMMERCIAL_COLUMNS else x for x in data.columns]
		data.index = (data.index.tz_localize("UTC") + pd.Timedelta(hours=TZSPEC[tzname]-1,minutes=45)).tz_convert(tzname)
		data = data.resample("1h").sum()
		if result is None:
			result = data*wt
		else:
			result += data*wt
	return result.round(1)

if __name__ == "__main__":
	print(get_states())
	print(get_counties("CA"))
	print(get_weather("CA","Alameda County"))
	print(get_residential("CA","San Mateo County",HOUSE))
	print(get_commercial("CA","San Mateo County",LARGEOFFICE))

