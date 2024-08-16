import marimo

__generated_with = "0.7.19"
app = marimo.App(width="full", app_title="")


@app.cell
def __(mo):
    mo.md(
        """
        # ASCRIPT -- Advanced Smart-Charging Infrastructure Planning Tool

        Version 2.0
        """
    )
    return


@app.cell
def __(mo):
    welcome_items = mo.md("""
    Welcome to ASCRIPT, the Advanced Smart-Charging Infrastructure Planning Tool.

    ASCRIPT identifies substations that may reach import/export capacity limits in coming years by using load, renewable, energy storage, and electric vehicle adoption forecasts. You can study scenarios where these resources give rise to conditions where too much load or too much generation is encountered at certain times of year, days of the week, or hours of the day.

    Each scenario requires you to specify which which county and substations you are studying, what demand for EV charging is present, where EV chargers are located, what the substations and feeder limits are, how the weather is affecting renewables, how much energy storage is available and how it is controlled, and how much customer load growth and electrification there is.
    """)
    return welcome_items,


@app.cell
def __(
    charger_items,
    feeder_items,
    loadshape_items,
    location_items,
    mo,
    overview_items,
    renewable_items,
    scenario_items,
    storage_items,
    tariff_items,
    weather_items,
    welcome_items,
):
    #
    # Scenario Inputs
    #
    mo.ui.tabs({
        "Welcome" : welcome_items,
        "Files" : scenario_items,
        "Scenario" : mo.accordion(
            items={
                "**Overview**": overview_items,
                "**Location**": location_items,
                "**Demand**": charger_items,
                "**Supply**": tariff_items,
                "**Feeders**": feeder_items,
                "**Weather**" : weather_items,
                "**Renewables**": renewable_items,
                "**Storage**": storage_items,
                "**Loads**": loadshape_items,
            },
            multiple=True,
            lazy=True,
            ),
        "Results" : overview_items,
        },
      lazy=True,
    )
    return


@app.cell
def __(mo):
    get_filename,set_filename = mo.state("")
    get_scenario,set_scenario = mo.state({})
    return get_filename, get_scenario, set_filename, set_scenario


@app.cell
def __(get_filename, mo, set_filename):
    #
    # Scenario files
    #
    get_filename()
    scenario_file_ui = mo.ui.file_browser(
        label="<b>Select file...</b>",
        filetypes=[".ascript"],
        multiple=False,
        on_change=lambda x:set_filename(x[0].path if len(x)>0 else ""),
    )
    return scenario_file_ui,


@app.cell
def __(get_filename, get_scenario, json, mo, os, set_scenario):
    scenario_load_ui = mo.ui.button(
        label="Load",
        disabled=not get_filename(),
        on_click=lambda _:set_scenario(json.load(open(get_filename(),"r"))),
    )
    scenario_save_ui = mo.ui.button(
        label="Save",
        disabled=not get_filename(),
        on_click=lambda _:json.dump(get_scenario(),open(get_filename(),"w")),
    )
    scenario_delete_ui = mo.ui.button(
        label="Delete",
        disabled=not get_filename(),
        on_click=lambda _:os.remove(get_filename())
    )
    return scenario_delete_ui, scenario_load_ui, scenario_save_ui


@app.cell
def __(get_filename, mo, os, set_filename):
    def _set_filename(x):
        return set_filename(os.path.join(os.getcwd(),x+".ascript") if x else "")
    scenario_name_ui = mo.ui.text(
        label="Scenario name:",
        value=os.path.splitext(os.path.basename(get_filename()))[0] if get_filename() else "",
        on_change=_set_filename,
    )
    return scenario_name_ui,


@app.cell
def __(
    mo,
    scenario_delete_ui,
    scenario_file_ui,
    scenario_load_ui,
    scenario_name_ui,
    scenario_save_ui,
):
    scenario_items = mo.vstack([
        scenario_file_ui,
        mo.hstack([scenario_load_ui,scenario_save_ui,scenario_name_ui,scenario_delete_ui],justify='start'),
    ])
    return scenario_items,


@app.cell
def __(
    demand_overview,
    feeder_overview,
    get_filename,
    load_overview,
    location_overview,
    mo,
    os,
    renewables_overview,
    storage_overview,
    supply_overview,
    weather_overview,
):
    #
    # Overview
    #
    overview_items = mo.md(f"""
    <table>
        <caption>{os.path.splitext(os.path.basename(get_filename()))[0]} scenario<hr/><hr/></caption>
        {location_overview}
        {demand_overview}
        {supply_overview}
        {feeder_overview}
        {weather_overview}
        {renewables_overview} 
        {storage_overview}
        {load_overview}
    </table>
    """)
    return overview_items,


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
def __(substation_ui):
    substations = substation_ui.value.ZIP.to_dict()
    substation_names = ", ".join(substations.keys()) if substations else None

    return substation_names, substations


@app.cell
def __(defaults, json, loads, mo):
    #
    # State selection
    #
    utilities_data = json.load(open("utilities.json","r"))
    _values = loads.get_states()
    state_ui = mo.ui.dropdown(
        label="State:",
        options=list(utilities_data),
        value=(defaults['STATE'] if 'STATE' in defaults and defaults['STATE'] in _values else _values[0]),
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
        value=(defaults['COUNTY'] if 'COUNTY' in defaults and defaults['COUNTY'] in _values else _values[0]),
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
        value=(defaults['CITY'] if 'CITY' in defaults and defaults['CITY'] in _values else _values[0]),
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
def __(city_ui, county_ui, state_ui, substation_names, substations):
    location_overview=f"""
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
    """
    return location_overview,


@app.cell
def __(
    ev_adoption_rates,
    ev_adoption_ui,
    number_chargers_ui,
    number_evs_ui,
    year_ui,
):
    #
    # Demand
    #
    demand_overview=f"""
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
    """
    return demand_overview,


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
    ev_timer_ui = mo.ui.switch(label="Enable residential EV charger timers")
    return ev_timer_ui, number_chargers_ui, number_evs_ui, year_ui


@app.cell
def __(
    ev_adoption_ui,
    ev_config,
    ev_loadshape,
    ev_model,
    ev_timer_ui,
    mo,
    number_chargers_ui,
    number_evs_ui,
    public_fraction_ui,
    public_rate_ui,
    public_tariff_ui,
    residential_fraction_ui,
    residential_rate_ui,
    residential_tariff_ui,
    speech,
    workplace_fraction_ui,
    workplace_rate_ui,
    workplace_tariff_ui,
    year_ui,
):
    #
    # Supply
    #
    supply_overview = f"""
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
    """
    ev_plots = speech.Plotting(ev_model, ev_config)
    charger_items = mo.vstack(
        [
            mo.md(
                """Specify the study year, EV adoption rate, number of EV, and chargers."""
            ),
            # mo.hstack([full_adoption_year_ui,peak_adoption_year_ui,adoption_rate_ui],justify='space-between'),
            mo.hstack([year_ui, ev_adoption_ui,number_evs_ui], justify="start"),
            mo.hstack([number_chargers_ui,ev_timer_ui], justify="start"),
            mo.hstack(
                [
                    ev_loadshape[x].plot(
                        title=x.title(),
                        xlabel="Hour of day",
                        ylabel="EV charger load (MW)",
                        grid=True,
                        legend=True,
                        xticks=ev_loadshape[x].index[3::6],
                    )
                    for x in ["weekday", "weekend"]
                ],
                justify="space-between",
            ),
        ]
    )
    return charger_items, ev_plots, supply_overview


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
def __(export_capacity_ui, import_capacity_ui, load, load_fraction_ui):
    #
    # Feeder
    #
    _import_margin = 100-load["electric[kW]"].max()*load_fraction_ui.value/100/1000/import_capacity_ui.value*100
    feeder_overview=f"""
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
    """
    return feeder_overview,


@app.cell
def __(math, mo, substation_ui):
    #
    # Import/export capacities
    #
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
    #
    # Peak load fraction
    #
    load_fraction_ui = mo.ui.slider(
        label=f"""Fraction of peak load served (% of {load["electric[kW]"].max()/1000:.1f} MW)""",
        start=0,
        stop=100,
        value=min(100,round(import_capacity_ui.value/(load["electric[kW]"].max()/1000)*85,0)),
        debounce=True,
        show_value=True,
    )
    return load_fraction_ui,


@app.cell
def __(export_capacity_ui, import_capacity_ui, load_fraction_ui, mo):
    #
    # Feeder UI items
    #
    feeder_items = mo.vstack([
        mo.md("""Set constraints on the network assets to include in the hotspot analysis."""),
        mo.hstack([import_capacity_ui,export_capacity_ui,load_fraction_ui]),
    ])
    return feeder_items,


@app.cell
def __(
    base,
    commercial_efficiency_ui,
    commercial_electrification_gas_ui,
    dt,
    load,
    residential_efficiency_ui,
    residential_electrification_gas_ui,
    residential_electrification_oil_ui,
    residential_electrification_propane_ui,
    residential_load_growth_ui,
    year_ui,
):
    load_overview=f"""
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
    """
    return load_overview,


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
    net_load_ui = mo.ui.switch(label="Show net load")
    return (
        commercial_efficiency_ui,
        commercial_electrification_gas_ui,
        commercial_load_growth_ui,
        net_load_ui,
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
    county_ui,
    load,
    mo,
    net_load_ui,
    plt,
    residential_efficiency_ui,
    residential_electrification_gas_ui,
    residential_electrification_oil_ui,
    residential_electrification_propane_ui,
    residential_load_growth_ui,
    sb,
    solar_capacity_ui,
    state_ui,
    weather_data,
    wind_capacity_ui,
):
    plt.figure(figsize=(15, 5))
    if net_load_ui.value:
        if solar_capacity_ui.value > 0:
            _solar = weather_data["ghr[W/m^2]"]
            _solar.index = load.index
            _solar = _solar / _solar.max() * solar_capacity_ui.value
        else:
            _solar = 0.0
        if wind_capacity_ui.value > 0:
            _wind = weather_data["windvel[m/s]"]
            _wind.index = load.index
            _wind = _wind / _wind.max() * wind_capacity_ui.value
        else:
            _wind = 0.0
        _load = load["electric[kW]"] / 1000 - _solar - _wind
    else:
        _load = load["electric[kW]"] / 1000
    _load = sb.heatmap(
        _load.to_numpy().reshape((365, 24)).transpose(),
        cmap="jet",
        cbar_kws={"label": "Load (MW)"},
    )
    _load.set_xlabel("Day")
    _load.set_ylabel("Hour")
    _load.set_title(f"{county_ui.value.title()} County, {state_ui.value}")
    loadshape_items = mo.vstack(
        [
            mo.hstack([residential_load_growth_ui, commercial_load_growth_ui]),
            mo.hstack(
                [
                    residential_electrification_gas_ui,
                    commercial_electrification_gas_ui,
                ]
            ),
            mo.hstack([residential_electrification_oil_ui]),
            mo.hstack([residential_electrification_propane_ui]),
            mo.hstack([residential_efficiency_ui, commercial_efficiency_ui]),
            net_load_ui,
            _load,
        ]
    )
    return loadshape_items,


@app.cell
def __(
    commercial_efficiency_ui,
    commercial_electrification_gas_ui,
    commercial_load_growth_ui,
    county_ui,
    dt,
    ev_load,
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
    _evloads = ev_load.sum(axis=1).values*1000
    load["electric[kW]"] += _evloads
    load["total[kW]"] += _evloads

    return base, load


@app.cell
def __(mo):
    #
    # Renewables
    #
    distributed_renewables_ui=mo.ui.switch(label="Distributed renewables only")
    get_solar_capacity,set_solar_capacity = mo.state(0)
    get_wind_capacity,set_wind_capacity = mo.state(0)
    return (
        distributed_renewables_ui,
        get_solar_capacity,
        get_wind_capacity,
        set_solar_capacity,
        set_wind_capacity,
    )


@app.cell
def __(distributed_renewables_ui, solar_capacity_ui, wind_capacity_ui):
    #
    # Renewables overview
    #
    renewables_overview=f"""  
    <tr><th rowspan=3>Renewables</th>
        <th>Solar capacity</th>
        <td>{solar_capacity_ui.value:,.0f} MW</td>
        <td></td>
    </tr>
    <tr><th>Wind capacity</th>
        <td>{wind_capacity_ui.value:,.0f} MW</td>
        <td></td>
    </tr>
    <tr><th>Distributed resources</th>
        <td>{'Included' if distributed_renewables_ui.value else 'None'}</td>
        <td></td>
    </tr>
    <tr><td colspan=4><hr/></td></tr>
    """
    return renewables_overview,


@app.cell
def __(
    distributed_renewables_ui,
    get_solar_capacity,
    get_wind_capacity,
    load,
    math,
    mo,
    set_solar_capacity,
    set_wind_capacity,
    substation_ui,
):
    #
    # Renewable generation
    #
    _value=max(10,sum([x*y*(int(x/100)+1) for x,y in substation_ui.value[['MAX_VOLT','LINES']].values])) if distributed_renewables_ui.value else load["electric[kW]"].max()/1000
    _max=10**int(math.log10(_value)+1) 
    solar_capacity_ui = mo.ui.slider(
        label="Installed solar capacity (MW):",
        start=0,
        stop=_max,
        step=_max/100,
        value=min(_max,get_solar_capacity()),
        on_change=set_solar_capacity,
        debounce=True,
        show_value=True,
    )
    wind_capacity_ui = mo.ui.slider(
        label="Installed wind capacity (MW):",
        start=0,
        stop=_max,
        step=_max/100,
        value=min(_max,get_wind_capacity()),
        on_change=set_wind_capacity,
        debounce=True,
        show_value=True,
    )
    renewable_items = mo.hstack([distributed_renewables_ui,solar_capacity_ui,wind_capacity_ui])
    return renewable_items, solar_capacity_ui, wind_capacity_ui


@app.cell
def __(distributed_storage_ui, mo, storage_energy_ui, storage_power_ui):
    #
    # Storage
    #
    storage_items = mo.hstack([distributed_storage_ui,storage_power_ui,storage_energy_ui])
    if storage_power_ui.value > 0:
        _days,_hours = divmod(storage_energy_ui.value/storage_power_ui.value,24)
        _hours,_minutes = divmod(_hours*60,60)
        _days = f"{_days:.0f} days" if _days>0 else ""
        _hours = f"{_hours:.0f} hours" if _hours>0 else ""
        _minutes = f"{_minutes:.0f} minutes" if _minutes>0 else ""
    else:
        _days,_hours,_minutes = "","","N/A"
    storage_overview=f"""
    <tr><th rowspan=4>Storage</th>
        <th>Power capacity</th>
        <td>{storage_power_ui.value:,.0f} MW</td>
        <td></td>
    </tr>
    <tr><th>Energy capacity</th>
        <td>{storage_energy_ui.value:,.0f} MWh</td>
        <td></td>
    </tr>
    <tr><th>Distributed resources</th>
        <td>{'Included' if distributed_storage_ui.value else 'None'}</td>
        <td></td>
    </tr>
    <tr><th>Maximum duration</th>
        <td>{_days} {_hours} {_minutes}</td>
        <td></td>
    </tr>
    <tr><td colspan=4><hr/></td></tr>
    """
    return storage_items, storage_overview


@app.cell
def __(mo):
    #
    # Storage states
    #
    distributed_storage_ui = mo.ui.switch(label="Distributed storage only")
    get_storage_power,set_storage_power = mo.state(0)
    get_storage_energy,set_storage_energy = mo.state(0)
    return (
        distributed_storage_ui,
        get_storage_energy,
        get_storage_power,
        set_storage_energy,
        set_storage_power,
    )


@app.cell
def __(
    distributed_storage_ui,
    get_storage_energy,
    get_storage_power,
    load,
    math,
    mo,
    set_storage_energy,
    set_storage_power,
    substation_ui,
):
    #
    # Storage UI
    #
    _value=max(10,sum([x*y*(int(x/100)+1) for x,y in substation_ui.value[['MAX_VOLT','LINES']].values])) if distributed_storage_ui.value else load["electric[kW]"].max()/1000
    _max=10**int(math.log10(_value)+1) 
    storage_power_ui=mo.ui.slider(
        label="Storage power capacity (MW)",
        start=0,
        stop=_max,
        step=_max/100,
        debounce=True,
        show_value=True,
        value=min(_max,get_storage_power()),
        on_change=set_storage_power,
    )
    storage_energy_ui=mo.ui.slider(
        label="Storage energy capacity (MWh)",
        start=0,
        stop=_max,
        step=_max/100,
        debounce=True,
        show_value=True,
        value=min(_max,get_storage_energy()),
        on_change=set_storage_energy,
    )
    return storage_energy_ui, storage_power_ui


@app.cell
def __(county_ui, loads, mo, plt, sb, state_ui):
    #
    # Weather data
    #
    weather_data = loads.get_weather(
        state_ui.value, county_ui.value.title() + " County"
    )

    plt.figure(figsize=(15,5))
    _temp = sb.heatmap((weather_data["drybulb[degC]"] * 1.8 + 32).to_numpy().reshape((365,24)).transpose(),
                       cmap="jet",cbar_kws={'label':'Temperature ($^\\mathrm{o}$F)'},
                       # xticklabels=_index,
                      )
    _temp.set_xlabel("Day")
    _temp.set_ylabel("Hour")
    _temp.set_title(f"{county_ui.value.title()} County, {state_ui.value}")

    plt.figure(figsize=(15,5))
    _solar = sb.heatmap((weather_data["ghr[W/m^2]"]).to_numpy().reshape((365,24)).transpose(),
                       cmap="jet",cbar_kws={'label':'Solar (W/m$^2$)'}
                      )
    _solar.set_xlabel("Day")
    _solar.set_ylabel("Hour")
    _solar.set_title(f"{county_ui.value.title()} County, {state_ui.value}")

    plt.figure(figsize=(15,5))
    _wind = sb.heatmap((weather_data["windvel[m/s]"]).to_numpy().reshape((365,24)).transpose(),
                       cmap="jet",cbar_kws={'label':'Wind (m/s)'}
                      )
    _wind.set_xlabel("Day")
    _wind.set_ylabel("Hour")
    _wind.set_title(f"{county_ui.value.title()} County, {state_ui.value}")

    weather_items = mo.ui.tabs(
        {
            "Temperature": _temp,
            "Solar": _solar,
            "Wind": _wind,
        },
        # lazy=True,
    )
    weather_overview = mo.md(f"""
    <tr><th rowspan=3>Weather</th>
        <th>Peak temperature</th>
        <td>{(weather_data["drybulb[degC]"]*1.8+32).max():.1f} &deg;F</td>
        <td></td>
    </tr>
    <tr><th>Peak solar</th>
        <td>{(weather_data["ghr[W/m^2]"]).max():.1f} W/m&sup2;</td>
        <td></td>
    </tr>
    <tr><th>Peak wind</th>
        <td>{(weather_data["windvel[m/s]"]).max():.1f} m/s</td>
        <td></td>
    </tr>
    """)
    return weather_data, weather_items, weather_overview


@app.cell
def __(speech):
    #
    # SPEECh model
    #
    ev_data = speech.DataSetConfigurations('Original16',ng=16)
    ev_model = speech.SPEECh(ev_data)
    return ev_data, ev_model


@app.cell
def __(ev_model, ev_timer_ui, json, number_evs_ui, pd, speech):
    #
    # SPEECh config
    ev_config = speech.SPEEChGeneralConfiguration(ev_model, remove_timers=not ev_timer_ui.value)
    ev_config.num_evs(number_evs_ui.value)
    ev_config.groups()
    # ev_config.change_pg(new_weights={0: 0.5, 4: 0.5}, dend=True)
    ev_config.run_all(weekday="weekday")
    ev_loadshape = {}
    _dt = {"weekend":pd.date_range("2017-12-31 00:00:00+08:00","2018-01-01 00:00:00+08:00",periods=1440),
           "weekday":pd.date_range("2018-01-01 00:00:00+08:00","2018-01-02 00:00:00+08:00",periods=1440),
           }

    # Note: mapping won't be necessary if we redesign the GMM
    _kw = json.load(open("ev_chargers.json","r")) # charger type kW loads
    _mt = json.load(open("ev_sectors.json","r")) # charging segment map to customer sectors
    for daytype in _dt:
        ev_config.run_all(weekday=daytype)
        _ls = pd.DataFrame(ev_config.total_load_dict,index=_dt[daytype])
        for _col in _ls.columns:
            _ct = _col.split()[-1]
            _ls[_col] *= _kw[_ct]
        for _cs in _mt.values():
            _ls[_cs] = 0.0
        for _col in _mt:
            _ls[_mt[_col]] += _ls[_col]        
            _ls.drop(_col,axis=1,inplace=True)
        ev_loadshape[daytype] = _ls.resample("1H").mean()[:-1]
    ev_load = pd.concat(([pd.concat([ev_loadshape['weekday']]*5 + [ev_loadshape['weekend']]*2)]*52)+[ev_loadshape['weekend']])
    return daytype, ev_config, ev_load, ev_loadshape


@app.cell
def __():
    import marimo as mo
    import os, sys
    import datetime as dt
    import pandas as pd
    import json
    import config
    import loads
    import math
    import matplotlib.pyplot as plt
    import seaborn as sb
    import speech
    return config, dt, json, loads, math, mo, os, pd, plt, sb, speech, sys


if __name__ == "__main__":
    app.run()
