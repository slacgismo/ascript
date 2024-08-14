import marimo

__generated_with = "0.7.19"
app = marimo.App(width="full", app_title="")


@app.cell
def __(mo):
    mo.md(
        """
        # Scenario

        Start your scenario by defining the Charging Segments for your selected location, EV/charger populations, rates, feeders, and loads.
        """
    )
    return


@app.cell
def __(
    charger_items,
    feeder_items,
    loadshape_items,
    location_items,
    mo,
    overview_items,
    renewable_items,
    storage_items,
    tariff_items,
):
    #
    # Scenario Inputs
    #
    mo.accordion(
        items={
            "**Overview**": overview_items,
            "**Location**": location_items,
            "**Demand**": charger_items,
            "**Supply**": tariff_items,
            "**Feeders**": feeder_items,
            "**Renewables**": renewable_items,
            "**Storage**": storage_items,
            "**Loads**": loadshape_items,
        },
        multiple=True,
        lazy=True,
    )
    return


@app.cell
def __(
    base,
    city_ui,
    commercial_efficiency_ui,
    commercial_electrification_gas_ui,
    county_ui,
    dt,
    ev_adoption_rates,
    ev_adoption_ui,
    export_capacity_ui,
    import_capacity_ui,
    load,
    load_fraction_ui,
    mo,
    number_chargers_ui,
    number_evs_ui,
    public_fraction_ui,
    public_rate_ui,
    public_tariff_ui,
    residential_efficiency_ui,
    residential_electrification_gas_ui,
    residential_electrification_oil_ui,
    residential_electrification_propane_ui,
    residential_fraction_ui,
    residential_load_growth_ui,
    residential_rate_ui,
    residential_tariff_ui,
    state_ui,
    substation_ui,
    workplace_fraction_ui,
    workplace_rate_ui,
    workplace_tariff_ui,
    year_ui,
):
    substations = substation_ui.value.ZIP.to_dict()
    substation_names = ", ".join(substations.keys()) if substations else None
    _import_margin = 100-load["electric[kW]"].max()*load_fraction_ui.value/100/1000/import_capacity_ui.value*100
    overview_items = mo.md(f"""<table>
    <caption>Current scenario data<hr/><hr/></caption>

    <tr><th rowspan=2>Location</th>
        <th>City, County, State</th>
        <td>{city_ui.value.title()}, {county_ui.value.title()} County, {state_ui.value}</td>
        <td></td>
    </tr>
    <tr><th>Substations</th>
        <td>{"<br/>".join([x[0]+" ("+x[1]+")" for x in substations.items()]) if substation_names else '<font color="red"><b>NONE</b></font>'}</td>
        <td>{'<font color="red">&leftarrow; Select one or more substations</font>' if not substation_names else ''}</td>
    </tr>
    <tr><td colspan=4><hr/></td></tr>

    <tr><th rowspan=4>Demand</th>
        <th>Study year</th>
        <td>{year_ui.value}</td>
        <td></td>
    </tr>
    <tr><th>EV adoption rate</th>
        <td>{ {y:x for x,y in ev_adoption_rates.items()}[ev_adoption_ui.value]}</td>
        <td></td>
    </tr>
    <tr><th>Number of EVs</th>
        <td>{number_evs_ui.value:,.0f}</td>
        <td></td>
    </tr>
    <tr><th>Number of chargers</th>
        <td>{number_chargers_ui.value:,.0f}</td>
        <td></td>
    </tr>
    <tr><td colspan=4><hr/></td></tr>

    <tr><th rowspan=3>Supply</th>
        <th>Public</th>
        <td>{public_fraction_ui.value}% on {public_tariff_ui.value.lower()} tariff<br/>{public_rate_ui.value}</td>
        <td></td>
    </tr>
    <tr><th>Workplace</th>
        <td>{workplace_fraction_ui.value}% on {workplace_tariff_ui.value.lower()} tariff<br/>{workplace_rate_ui.value}</td>
        <td></td>
    </tr>
    <tr><th>Residential</th>
        <td>{residential_fraction_ui.value}% on {residential_tariff_ui.value.lower()} tariff<br/>{residential_rate_ui.value}</td>
        <td></td>
    </tr>
    <tr><td colspan=4><hr/></td></tr>

    <tr><th rowspan=2>Feeders</th>
        <th>Feeder import capacity</th>
        <td>{import_capacity_ui.value} MW
            ({_import_margin:.0f}% left)
        </td>
        <td>{"<font color=red><b>&leftarrow; Insufficient capacity<br/>Increase import limit or<br/>decrease load fraction.</b></font>" if _import_margin<=0 else ""}</td>
    </tr>
    <tr><th>Feeder export capacity</th>
        <td>{export_capacity_ui.value} MW</td>
        <td></td>
    </tr>
    <tr><td colspan=4><hr/></td></tr>
        
    <tr><th rowspan=2>Renewables</th>
        <th>TODO</th>
        <td></td>
    </tr>
    <tr><th>TODO</th>
        <td></td>
        <td></td>
    </tr>
    <tr><td colspan=4><hr/></td></tr>
        
    <tr><th rowspan=2>Storage</th>
        <th>TODO</th>
        <td></td>
    </tr>
    <tr><th>TODO</th>
        <td></td>
        <td></td>
    </tr>
    <tr><td colspan=4><hr/></td></tr>

    <tr><th rowspan=6>Loads</th>
        <th>Load growth</th>
        <td>{pow((1+residential_load_growth_ui.value/100),int(year_ui.value)-dt.datetime.now().year)*100:.0f}%</td>
        <td></td>
    </tr>

    <tr><th>Electrification impact</th>
        <td>Residential natural gas: {residential_electrification_gas_ui.value/residential_efficiency_ui.value*100:.0f}%<br/>
            Residential fuel oil: {residential_electrification_oil_ui.value/residential_efficiency_ui.value*100:.0f}%<br/>
            Residential propane: {residential_electrification_propane_ui.value/residential_efficiency_ui.value*100:.0f}%<br/>
            Commercial natural gas: {commercial_electrification_gas_ui.value/commercial_efficiency_ui.value*100:.0f}%<br/>
        </td>
        <td></td>
    </tr>

    <tr><th>Median load</th>
        <td>{load["electric[kW]"].median()/1000:.1f} MW ({load["electric[kW]"].median()/base["electric[kW]"].median()*100-100:+.0f}%)</td>
        <td></td>
    </tr>

    <tr><th>Average load</th>
        <td>{load["electric[kW]"].mean()/1000:.1f} MW ({load["electric[kW]"].mean()/base["electric[kW]"].mean()*100-100:+.0f}%)</td>
        <td></td>
    </tr>

    <tr><th>Peak load</th>
        <td>{load["electric[kW]"].max()/1000:.1f} MW ({load["electric[kW]"].max()/base["electric[kW]"].max()*100-100:+.0f}%)</td>
        <td></td>
    </tr>

    <tr><th>Light load</th>
        <td>{load["electric[kW]"].min()/1000:.1f} MW ({load["electric[kW]"].min()/base["electric[kW]"].min()*100-100:+.0f}%)</td>
        <td></td>
    </tr>
    <tr><td colspan=4><hr/></td></tr>

    </table>""")
    return overview_items, substation_names, substations


@app.cell
def __(pd):
    #
    # Substation data
    #
    substation_data = pd.read_csv(
        f"substations.csv.gz",
        low_memory=False,
        index_col=["STATE", "COUNTY", "CITY", "TYPE", "NAME"],
    ).sort_index()
    defaults = dict(STATE="CA",COUNTY="ORANGE",CITY="SANTA ANA",SUBSTATION=["CAMDEN"],UTILITY="Southern California Edison Co")
    return defaults, substation_data


@app.cell
def __(defaults, json, mo):
    #
    # State selection
    #
    utilities_data = json.load(open("utilities.json","r"))
    state_ui = mo.ui.dropdown(
        label="State:",
        options=list(utilities_data),
        value=(defaults['STATE'] if 'STATE' in defaults else _values[0]),
        # on_change=set_state,
        allow_select_none=False,
    )
    return state_ui, utilities_data


@app.cell
def __(defaults, mo, state_ui, substation_data):
    #
    # County selection
    #
    _values = (
        substation_data.loc[state_ui.value]
        .index.get_level_values(0)
        .unique()
        .tolist()
    )
    county_ui = mo.ui.dropdown(
        label="County:",
        options=_values,
        value=(defaults['COUNTY'] if 'COUNTY' in defaults else _values[0]),
        allow_select_none=False,
    )
    return county_ui,


@app.cell
def __(county_ui, defaults, mo, state_ui, substation_data):
    #
    # City selection
    #
    _values = (
        substation_data.loc[state_ui.value, county_ui.value]
        .index.get_level_values(0)
        .unique()
        .tolist()
    )
    city_ui = mo.ui.dropdown(
        label="City:",
        options=_values,
        value=(defaults['CITY'] if 'CITY' in defaults else _values[0]),
    )
    return city_ui,


@app.cell
def __(city_ui, county_ui, mo, state_ui, substation_data):
    #
    # Substation type selection
    #
    _values = (
        substation_data.loc[state_ui.value, county_ui.value, city_ui.value]
        .index.get_level_values(0)
        .unique()
        .tolist()
    )
    type_ui = mo.ui.dropdown(
        label="Substation type:",
        options=_values,
        value=("SUBSTATION" if "SUBSTATION" in _values else _values[0]),
    )
    return type_ui,


@app.cell
def __(mo):
    #
    # Substation filters
    #
    name_ui = mo.ui.checkbox(label="Known name",value=True)
    service_ui = mo.ui.checkbox(label="In service",value=True)
    voltage_ui = mo.ui.checkbox(label="Known voltage",value=True)
    return name_ui, service_ui, voltage_ui


@app.cell
def __(
    city_ui,
    county_ui,
    mo,
    name_ui,
    service_ui,
    state_ui,
    substation_data,
    type_ui,
):
    #
    # Substation selection
    #
    _substations = substation_data.loc[state_ui.value,county_ui.value,city_ui.value,type_ui.value][["ZIP","STATUS","MAX_VOLT","MIN_VOLT","LINES"]]
    _substations = _substations.loc[[x for x in _substations.index if not name_ui.value or not x.startswith("UNKNOWN")]].sort_values(["MAX_VOLT","MIN_VOLT","LINES"],ascending=False)
    _status = _substations["STATUS"].unique().tolist()
    substation_ui = mo.ui.table(_substations[(_substations["STATUS"].isin(["IN SERVICE"] if service_ui.value else _status)) &
                                             (_substations["MIN_VOLT"]>0)].sort_index(),
                                selection='multi',
                                # (defaults['SUBSTATION'] if 'SUBSTATION' in defaults else []),
                                pagination=None,
                                show_column_summaries=False,
                                )
    return substation_ui,


@app.cell
def __(
    city_ui,
    county_ui,
    mo,
    name_ui,
    service_ui,
    state_ui,
    substation_ui,
    type_ui,
    voltage_ui,
):
    #
    # Location UI
    #
    location_items = mo.vstack([
        # mo.md("Choose feeder from state, county, and city"),
        mo.hstack([state_ui, county_ui, city_ui,type_ui]), 
        mo.hstack([name_ui,service_ui,voltage_ui]),
        substation_ui,
    ])
    return location_items,


@app.cell
def __(mo):
    #
    # EV adoption rate
    #
    ev_adoption_rates = {
        "Low (100-1,000)": 1000,
        "Medium (1,000-10,000)": 10000,
        "High (10,000-100,000)": 100000,
        "Very high (100,000-1,000,000)": 1000000,
        }
    ev_adoption_ui = mo.ui.dropdown(
        label="EV adoption:",
        value=list(ev_adoption_rates)[0],
        options=ev_adoption_rates,
        allow_select_none=False,
    )
    return ev_adoption_rates, ev_adoption_ui


@app.cell
def __(dt, ev_adoption_ui, mo):
    year_ui = mo.ui.dropdown(
        label="Study year:",
        value=str(dt.datetime.now().year+10),
        options=[str(x) for x in range(dt.datetime.now().year, dt.datetime.now().year+21)],
    )
    number_evs_ui = mo.ui.slider(
        label="Number of EVs: ",
        value=float(ev_adoption_ui.value)/2,
        start=float(ev_adoption_ui.value)/10,
        stop=float(ev_adoption_ui.value),
        step=float(ev_adoption_ui.value)/100,
        debounce=True,
        show_value=True,
    )
    number_chargers_ui = mo.ui.slider(
        label="Number of chargers: ",
        value=float(ev_adoption_ui.value)/2,
        start=float(ev_adoption_ui.value)/10,
        stop=float(ev_adoption_ui.value),
        step=float(ev_adoption_ui.value)/100,
        debounce=True,
        show_value=True,
    )
    return number_chargers_ui, number_evs_ui, year_ui


@app.cell
def __(ev_adoption_ui, mo, number_chargers_ui, number_evs_ui, year_ui):
    charger_items = mo.vstack([
        mo.md("""Specify the study year, EV adoption rate, number of EV, and chargers."""),
        # mo.hstack([full_adoption_year_ui,peak_adoption_year_ui,adoption_rate_ui],justify='space-between'),
        mo.hstack([year_ui,ev_adoption_ui,number_evs_ui,number_chargers_ui],justify='space-between'),
    ])
    return charger_items,


@app.cell
def __(config, mo):
    #
    # Charger types
    #

    get_public_fraction, set_public_fraction = mo.state(
        round(config.DEFAULT_PUBLIC), 
        allow_self_loops=True
    )
    get_workplace_fraction, set_workplace_fraction = mo.state(
        round(config.DEFAULT_WORKPLACE), 
        allow_self_loops=True
    )
    get_residential_fraction, set_residential_fraction = mo.state(
        round(100 - config.DEFAULT_WORKPLACE - config.DEFAULT_PUBLIC),
        allow_self_loops=True,
    )
    return (
        get_public_fraction,
        get_residential_fraction,
        get_workplace_fraction,
        set_public_fraction,
        set_residential_fraction,
        set_workplace_fraction,
    )


@app.cell
def __(pd):
    #
    # Download NREL OpenEI tariff database
    #
    tariff_data = pd.read_csv(
        "https://openei.org/apps/USURDB/download/usurdb.csv.gz",
        low_memory=False,
        index_col=["utility","sector","name"],
    ).sort_index()
    return tariff_data,


@app.cell
def __(defaults, mo, state_ui, tariff_data, utilities_data):
    #
    # Read state utility database
    #
    _utilities = [x for x in utilities_data[state_ui.value] if x in tariff_data.index.get_level_values(0).unique()]
    utility_ui = mo.ui.dropdown(
        label="Utility name:",
        options=_utilities,
        value=defaults['UTILITY'] if 'UTILITY' in defaults else utilities_data[0],
        allow_select_none=False,
    )
    return utility_ui,


@app.cell
def __(mo, tariff_data, utility_ui):
    #
    # Tariff UI elements
    #
    _options=tariff_data.loc[utility_ui.value].index.get_level_values(0).unique()
    residential_tariff_ui = mo.ui.dropdown(
        options=_options,
        value=("Residential" if "Residential" in _options else _options[0])
    )
    workplace_tariff_ui = mo.ui.dropdown(
        options=_options,
        value=("Commercial" if "Commercial" in _options else _options[0])
    )
    public_tariff_ui = mo.ui.dropdown(
        options=_options,
        value=("Commercial" if "Commercial" in _options else _options[0])
    )
    return public_tariff_ui, residential_tariff_ui, workplace_tariff_ui


@app.cell
def __(
    mo,
    public_tariff_ui,
    residential_tariff_ui,
    tariff_data,
    utility_ui,
    workplace_tariff_ui,
):
    #
    # Rate UI elements
    #
    _tariffs = tariff_data.loc[utility_ui.value,residential_tariff_ui.value]
    residential_rate_ui = mo.ui.dropdown(
        options=_tariffs.index,
        value=_tariffs.index[0],
    )
    _tariffs = tariff_data.loc[utility_ui.value,workplace_tariff_ui.value]
    workplace_rate_ui = mo.ui.dropdown(
        options=_tariffs.index,
        value=_tariffs.index[0],
    )
    _tariffs = tariff_data.loc[utility_ui.value,public_tariff_ui.value]
    public_rate_ui = mo.ui.dropdown(
        options=_tariffs.index,
        value=_tariffs.index[0],
    )
    return public_rate_ui, residential_rate_ui, workplace_rate_ui


@app.cell
def __(
    get_public_fraction,
    get_residential_fraction,
    get_workplace_fraction,
    mo,
    set_public_fraction,
    set_residential_fraction,
    set_workplace_fraction,
):
    #
    # Charger sector fractions
    #
    def _set_public_fraction(x):
        total = get_workplace_fraction() + get_residential_fraction()
        set_workplace_fraction(round(get_workplace_fraction()*(100-x)/total))
        set_residential_fraction(round(get_residential_fraction()*(100-x)/total))
        return set_public_fraction(x)
        
    def _set_workplace_fraction(x):
        total = get_public_fraction() + get_residential_fraction()
        set_public_fraction(round(get_public_fraction()*(100-x)/total))
        set_residential_fraction(round(get_residential_fraction()*(100-x)/total))
        return set_workplace_fraction(x)
        
    def _set_residential_fraction(x):
        total = get_workplace_fraction() + get_public_fraction()
        set_workplace_fraction(round(get_workplace_fraction()*(100-x)/total))
        set_public_fraction(round(get_public_fraction()*(100-x)/total))
        return set_residential_fraction(x)
        
    public_fraction_ui = mo.ui.slider(
        start=0,
        stop=100,
        value=get_public_fraction(),
        on_change=_set_public_fraction,
        debounce=True,
        show_value=True,
    )
    workplace_fraction_ui = mo.ui.slider(
        start=0,
        stop=100,
        value=get_workplace_fraction(),
        on_change=_set_workplace_fraction,
        debounce=True,
        show_value=True,
    )
    residential_fraction_ui = mo.ui.slider(
        start=0,
        stop=100,
        value=get_residential_fraction(),
        on_change=_set_residential_fraction,
        debounce=True,
        show_value=True,    
    )
    return (
        public_fraction_ui,
        residential_fraction_ui,
        workplace_fraction_ui,
    )


@app.cell
def __(
    mo,
    number_chargers_ui,
    public_fraction_ui,
    public_rate_ui,
    public_tariff_ui,
    residential_fraction_ui,
    residential_rate_ui,
    residential_tariff_ui,
    utility_ui,
    workplace_fraction_ui,
    workplace_rate_ui,
    workplace_tariff_ui,
):
    #
    # Charger supply UI
    #
    tariff_items = mo.vstack([
        mo.md(f"""Specify the charger types and tariffs for {utility_ui}
        <table>
        <tr><th>Location</th><th>Fraction</th><th>Count</th><th>Sector</th><th>Tariff</th></tr>
        <tr><td>Public</td>
            <td>{public_fraction_ui}%</td>
            <td>{public_fraction_ui.value*number_chargers_ui.value/100:,.0f}</td>
            <td>{public_tariff_ui}</td>
            <td>{public_rate_ui}</td>
        </tr>
        <tr><td>Workplace</td>
            <td>{workplace_fraction_ui}%</td>
            <td>{workplace_fraction_ui.value*number_chargers_ui.value/100:,.0f}</td>
            <td>{workplace_tariff_ui}</td>
            <td>{workplace_rate_ui}</td>
        </tr>
        <tr><td>Residential</td>
            <td>{residential_fraction_ui}%</td>
            <td>{residential_fraction_ui.value*number_chargers_ui.value/100:,.0f}</td>
            <td>{residential_tariff_ui}</td>
            <td>{residential_rate_ui}</td>
        </tr>
        </table>
    """),
        # mo.hstack([public_ui,workplace_ui,residential_ui]),
    ])

    return tariff_items,


@app.cell
def __():
    #
    # Feeder
    #
    return


@app.cell
def __(math, mo, substation_ui):
    _value=max(10,sum([x*y*(int(x/100)+1) for x,y in substation_ui.value[['MAX_VOLT','LINES']].values]))
    _max=10**int(math.log10(_value)+1)
    import_capacity_ui = mo.ui.slider(
        label="Import limit (MW)",
        start=0,
        stop=_max,
        value=_value,
        debounce=True,
        show_value=True,
    )
    export_capacity_ui = mo.ui.slider(
        label="Export limit (MW)",
        start=0,
        stop=_max,
        value=0,
        debounce=True,
        show_value=True,
    )
    return export_capacity_ui, import_capacity_ui


@app.cell
def __(import_capacity_ui, load, mo):
    load_fraction_ui = mo.ui.slider(
        label=f"""Fraction of peak load served (% of {load["electric[kW]"].max()/1000:.1f} MW)""",
        start=0,
        stop=100,
        value=min(100,round(import_capacity_ui.value/(load["electric[kW]"].max()/1000)*100,0)),
        debounce=True,
        show_value=True,
    )
    return load_fraction_ui,


@app.cell
def __(export_capacity_ui, import_capacity_ui, load_fraction_ui, mo):

    feeder_items = mo.vstack([
        mo.md("""Set constraints on the network assets to include in the hotspot analysis."""),
        mo.hstack([import_capacity_ui,export_capacity_ui,load_fraction_ui]),
    ])
    return feeder_items,


@app.cell
def __():
    #
    # Loadshape
    #
    return


@app.cell
def __(loads, mo):
    residential_load_growth_ui = mo.ui.slider(
        label="Residential load growth (%/y)",
        start=0.0,
        stop=20.0,
        step=0.5,
        value=loads.ASSUMPTIONS["residential"]["growth"]*100,
        debounce=True,
        show_value=True,
    )
    residential_electrification_oil_ui = mo.ui.slider(
        label="Residential fuel oil electrification (%)",
        start=0.0,
        stop=100.0,
        step=1.0,
        value=loads.ASSUMPTIONS["residential"]["electrification"]["oil"]*100,
        debounce=True,
        show_value=True,
    )
    residential_electrification_gas_ui = mo.ui.slider(
        label="Residential natural electrification (%)",
        start=0.0,
        stop=100.0,
        step=1.0,
        value=loads.ASSUMPTIONS["residential"]["electrification"]["gas"]*100,
        debounce=True,
        show_value=True,
    )
    residential_electrification_propane_ui = mo.ui.slider(
        label="Residential propane electrification (%)",
        start=0.0,
        stop=100.0,
        step=1.0,
        value=loads.ASSUMPTIONS["residential"]["electrification"]["propane"]*100,
        debounce=True,
        show_value=True,
    )
    residential_efficiency_ui = mo.ui.slider(
        label="Residential electrification efficiency (%)",
        start=1.0,
        stop=100.0,
        step=1.0,
        value=loads.ASSUMPTIONS["residential"]["efficiency"]*100,
        debounce=True,
        show_value=True,
    )
    commercial_load_growth_ui = mo.ui.slider(
        label="Commercial load growth (%/y)",
        start=0.0,
        stop=20.0,
        step=0.5,
        value=loads.ASSUMPTIONS["commercial"]["growth"]*100,
        debounce=True,
        show_value=True,
    )
    commercial_electrification_gas_ui = mo.ui.slider(
        label="Commercial natural gas electrification (%)",
        start=0.0,
        stop=100.0,
        step=1.0,
        value=loads.ASSUMPTIONS["commercial"]["electrification"]["gas"]*100,
        debounce=True,
        show_value=True,
    )
    commercial_efficiency_ui = mo.ui.slider(
        label="Commercial electrification efficiency (%)",
        start=1.0,
        stop=100.0,
        step=1.0,
        value=loads.ASSUMPTIONS["commercial"]["efficiency"]*100,
        debounce=True,
        show_value=True,
    )
    return (
        commercial_efficiency_ui,
        commercial_electrification_gas_ui,
        commercial_load_growth_ui,
        residential_efficiency_ui,
        residential_electrification_gas_ui,
        residential_electrification_oil_ui,
        residential_electrification_propane_ui,
        residential_load_growth_ui,
    )


@app.cell
def __(
    commercial_efficiency_ui,
    commercial_electrification_gas_ui,
    commercial_load_growth_ui,
    load,
    mo,
    residential_efficiency_ui,
    residential_electrification_gas_ui,
    residential_electrification_oil_ui,
    residential_electrification_propane_ui,
    residential_load_growth_ui,
):
    loadshape_items = mo.vstack([
        mo.hstack([residential_load_growth_ui,commercial_load_growth_ui]),
        mo.hstack([residential_electrification_gas_ui,commercial_electrification_gas_ui]),
        mo.hstack([residential_electrification_oil_ui]),
        mo.hstack([residential_electrification_propane_ui]),
        mo.hstack([residential_efficiency_ui,commercial_efficiency_ui]),
        (load["electric[kW]"]/1000).plot(grid=True,linewidth=0.5,figsize=(15,5),xlabel='Load (MW)')
    ])    
    return loadshape_items,


@app.cell
def __(
    commercial_efficiency_ui,
    commercial_electrification_gas_ui,
    commercial_load_growth_ui,
    county_ui,
    dt,
    loads,
    residential_efficiency_ui,
    residential_electrification_gas_ui,
    residential_electrification_oil_ui,
    residential_electrification_propane_ui,
    residential_load_growth_ui,
    state_ui,
    year_ui,
):
    base = loads.get_forecast(dt.datetime.now().year,state=state_ui.value,county=county_ui.value.title()+" County",assumptions=loads.BASECASE)
    load = loads.get_forecast(
        year=int(year_ui.value),
        state=state_ui.value,
        county=county_ui.value.title()+" County",
        assumptions={
            "residential" : {
                "growth" : residential_load_growth_ui.value/100,
                "electrification" : {
                    "oil" : residential_electrification_oil_ui.value/100,
                    "gas" : residential_electrification_gas_ui.value/100,
                    "propane" : residential_electrification_propane_ui.value/100,
                },
                "efficiency" : residential_efficiency_ui.value/100,
            },
            "commercial" : {
                "growth" : commercial_load_growth_ui.value/100,        
                "electrification" : {
                    "gas" : commercial_electrification_gas_ui.value/100,
                },
                "efficiency" : commercial_efficiency_ui.value/100,
            },
        }
    )
    return base, load


@app.cell
def __(mo):
    #
    # Renewables
    #
    renewable_items = mo.md("TODO")
    return renewable_items,


@app.cell
def __(mo):
    #
    # Storage
    #
    storage_items = mo.md("TODO")
    return storage_items,


@app.cell
def __():
    import marimo as mo
    import datetime as dt
    import pandas as pd
    import json
    import config
    import loads
    import math
    return config, dt, json, loads, math, mo, pd


if __name__ == "__main__":
    app.run()
