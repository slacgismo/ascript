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
    city_ui,
    county_ui,
    mo,
    number_chargers_ui,
    number_evs_ui,
    state_ui,
    substation_ui,
    year_ui,
):
    substations = substation_ui.value.ZIP.to_dict()
    substation_names = ", ".join(substations.keys()) if substations else None
    overview_items = mo.md(f"""<table>
    <caption>Current scenario data<hr/><hr/></caption>

    <tr><th><i>Location</i><hr/></th><td>&nbsp;<hr/></td></tr>
    <tr><td>City, County, State</td><td>{city_ui.value.title()}, {county_ui.value.title()}, {state_ui.value}</td></tr>
    <tr><td>Substations</td><td>{"<br/>".join([x[0]+" ("+x[1]+")" for x in substations.items()])}</td></tr>

    <tr><th><i>Demand</i><hr/></th><td>&nbsp;<hr/></td></tr>
    <tr><td>Study year</td><td>{year_ui.value}</td></tr>
    <tr><td>Number of EVs</td><td>{number_evs_ui.value:,.0f}</td></tr>
    <tr><td>Number of chargers</td><td>{number_chargers_ui.value:,.0f}</td></tr>

    <tr><th><i>Supply</i><hr/></th><td>&nbsp;<hr/></td></tr>

    <tr><th><i>Feeders</i><hr/></th><td>&nbsp;<hr/></td></tr>

    <tr><th><i>Loads</i><hr/></th><td>&nbsp;<hr/></td></tr>
    </table>""")
    return overview_items, substation_names, substations


@app.cell
def __(
    charger_items,
    feeder_items,
    loadshape_items,
    location_items,
    mo,
    overview_items,
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
            "**Loads**": loadshape_items,
        },
        multiple=True,
        lazy=True,
    )
    return


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
def __(defaults, mo, substation_data):
    #
    # State selection
    #
    _values = (
        substation_data[substation_data["COUNTYFIPS"] != "NOT AVAILABLE"]
        .index.get_level_values(0)
        .unique()
        .tolist()
    )
    state_ui = mo.ui.dropdown(
        label="State:",
        options=_values,
        value=(defaults['STATE'] if 'STATE' in defaults else _values[0]),
        # on_change=set_state,
        allow_select_none=False,
    )
    return state_ui,


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
def __(dt, mo):
    year_ui = mo.ui.dropdown(
        label="Study year:",
        value=str(dt.datetime.now().year+10),
        options=[str(x) for x in range(dt.datetime.now().year, dt.datetime.now().year+21)],
    )
    number_evs_ui = mo.ui.slider(
        label="Number of EVs: ",
        value=0,
        start=0,
        stop=100000,
        step=1000,
        debounce=True,
        show_value=True,
    )
    number_chargers_ui = mo.ui.slider(
        label="Number of chargers: ",
        value=0,
        start=0,
        stop=100000,
        step=1000,
        debounce=True,
        show_value=True,
    )
    return number_chargers_ui, number_evs_ui, year_ui


@app.cell
def __(mo, number_chargers_ui, number_evs_ui, year_ui):
    charger_items = mo.vstack([
        mo.md("""Specify your scenario by selecting the region, targeted year, percentage or number of EV chargers, and rate structures."""),
        # mo.hstack([full_adoption_year_ui,peak_adoption_year_ui,adoption_rate_ui],justify='space-between'),
        mo.hstack([year_ui,number_evs_ui,number_chargers_ui],justify='space-between'),
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
    tariff_data = pd.read_csv(
        "https://openei.org/apps/USURDB/download/usurdb.csv.gz",
        low_memory=False,
        index_col=["utility","sector","name"],
    ).sort_index()
    return tariff_data,


@app.cell
def __(defaults, mo, state_ui, tariff_data):
    _utilities = {"CA":[
        "City of Alameda, California (Utility Company)",
        "City of Anaheim, California (Utility Company)",
        "City of Azusa, California (Utility Company)",
        "City of Banning, California (Utility Company)",
        "City of Biggs, California (Utility Company)",
        "City of Burbank Water and Power, California (Utility Company)",
        "City of Colton, California (Utility Company)",
        "City of Corona, California (Utility Company)",
        "Direct Energy Services",
        "East Bay Municipal Util Dist",
        "East Bay Community Energy",
        "City of Escondido, California (Utility Company)",
        "City of Glendale, California (Utility Company)",
        "City of Gridley, California (Utility Company)",
        "City of Healdsburg, California (Utility Company)",
        "Imperial Irrigation District",
        "Island Energy",
        "Modesto Irrigation District",
        "City of Lodi, California (Utility Company)",
        "City of Lompoc, California (Utility Company)",
        "Los Angeles Department of Water and Power",
        "City of Moreno, California (Utility Company)",
        "City of Needles, California (Utility Company)",
        "Nevada Irrigation District",
        "O'Brien Cogeneration",
        "City of Palo Alto, California (Utility Company)",
        "Pacific Gas & Electric Co",
        "City of Pasadena, California (Utility Company)",
        "Pacific Power (California)",
        "City of Riverside, California (Utility Company)",
        "Sacramento Municipal Utility District",
        "San Diego Gas & Electric Co",
        "City & County of San Francisco (Utility Company)",
        "City of Santa Clara, California (Utility Company)",
        "Sierra Pacific Power Co",
        "Southern California Edison Co",
        "Southern California P P A",
        "Turlock Irrigation District",
    ]}
    _utilities = [x for x in _utilities[state_ui.value] if x in tariff_data.index.get_level_values(0).unique()]
    utility_ui = mo.ui.dropdown(
        label="Utility name:",
        options=_utilities,
        value=defaults['UTILITY'] if 'UTILITY' in defaults else _utilities[0],
        allow_select_none=False,
    )
    return utility_ui,


@app.cell
def __(mo, tariff_data, utility_ui):
    _tariffs = tariff_data.loc[utility_ui.value,"Residential"]
    residential_rate_ui = mo.ui.dropdown(
        options=_tariffs.index,
        value=_tariffs.index[0],
    )
    _tariffs = tariff_data.loc[utility_ui.value,"Commercial"]
    commercial_rate_ui = mo.ui.dropdown(
        options=_tariffs.index,
        value=_tariffs.index[0],
    )
    _tariffs = tariff_data.loc[utility_ui.value,"Commercial"]
    public_rate_ui = mo.ui.dropdown(
        options=_tariffs.index,
        value=_tariffs.index[0],
    )

    return commercial_rate_ui, public_rate_ui, residential_rate_ui


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
    commercial_rate_ui,
    mo,
    number_chargers_ui,
    public_fraction_ui,
    public_rate_ui,
    residential_fraction_ui,
    residential_rate_ui,
    utility_ui,
    workplace_fraction_ui,
):
    tariff_items = mo.vstack([
        mo.md(f"""Specify the charger types and tariffs for {utility_ui}
        <table>
        <tr><th>Location</th><th>Fraction</th><th>Count</th><th>Tariff</th></tr>
        <tr><td>Public</td><td>{public_fraction_ui}%</td><td>{public_fraction_ui.value*number_chargers_ui.value/100:,.0f}</td><td>{public_rate_ui}</td></tr>
        <tr><td>Workplace</td><td>{workplace_fraction_ui}%</td><td>{workplace_fraction_ui.value*number_chargers_ui.value/100:,.0f}</td><td>{commercial_rate_ui}</td></tr>
        <tr><td>Residential</td><td>{residential_fraction_ui}%</td><td>{residential_fraction_ui.value*number_chargers_ui.value/100:,.0f}</td><td>{residential_rate_ui}</td></tr>
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
def __(mo):
    feeder_items = mo.vstack([
        mo.md("""Set constraints on your feeders and select the network assets to include in the hotspot analysis."""),
        mo.md("TODO")
    ])
    return feeder_items,


@app.cell
def __():
    #
    # Loadshape
    #
    return


@app.cell
def __(mo):
    loadshape_items = mo.vstack([
        mo.md("""Fine-tune the future end-use load shapes based on region, year, and technology adoption rates."""),
        mo.md("TODO")    
    ])
    return loadshape_items,


@app.cell
def __():
    import marimo as mo
    import datetime as dt
    import pandas as pd
    import config
    return config, dt, mo, pd


if __name__ == "__main__":
    app.run()
