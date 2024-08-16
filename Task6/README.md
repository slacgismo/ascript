# ASCRIPT UI

## Prototype UI for ASCRIPT

Key capabilities

* Scenario
- [x] Specify location for charging infrastructure analysis
- [x] Specify charging infrastructure requirements
- [x] Specify feeder capacity
- [x] Generate charging loadshapes
- [ ] Analyze EV charging impact on loadshapes
- [ ] Display network impacts of loadshape change
* Analysis
- [x] Controls
- [x] Weather
- [x] Simulation
- [ ] Results
* Tariff
- [x] Public
- [x] Workplace
- [x] Residential
- [x] Tiered Tariffs
- [x] Weekday/weekend Schedule
* Map
- [x] Display map
- [x] Map navigation
- [ ] Address search
- [ ] Network topology
- [ ] Asset display
- [ ] Hotspot display
* Report
- [ ] Generate download

## Setup

~~~
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pip --upgrade -r requirements.txt
~~~

## Run

~~~
marimo run main.py
~~~

## Edit

~~~
marimo edit main.py
~~~
