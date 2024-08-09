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
    tariff_items,
):
    mo.accordion(
        items={
            "**Location**": location_items,
            "**Chargers**": charger_items,
            "**Rates**": tariff_items,
            "**Feeders**": feeder_items,
            "**Loads**": loadshape_items,
        },
        multiple=True,
        lazy=True,
    )
    return


@app.cell
def __(config, pd):
    county_data = pd.read_csv(f"counties/{config.DEFAULT_STATE}.csv")
    cities = pd.read_csv(
            "CA_cities.csv",
            usecols=[0,2,3],
            index_col=[1,0]
        ).sort_index()
    city_data = {x:[] for x in cities.index.get_level_values(0).unique()}
    for _county in list(city_data):
        city_data[f"{_county} County"] = {}
        for _city in cities.loc[_county].index:
            city_data[f"{_county} County"][_city] = float(cities.loc[_county,_city]["Population(2020)"])
    return cities, city_data, county_data


@app.cell
def __(config, mo):
    #
    # Aggregation level and location
    #

    get_aggregation_level,set_aggregation_level = mo.state(config.DEFAULT_AGGREGATION_LEVEL)
    get_state,set_state = mo.state(config.DEFAULT_STATE)
    get_location, set_location = mo.state(config.DEFAULT_LOCATION)
    return (
        get_aggregation_level,
        get_location,
        get_state,
        set_aggregation_level,
        set_location,
        set_state,
    )


@app.cell
def __(get_aggregation_level, mo, set_aggregation_level):
    aggregation_level_ui = mo.ui.radio(
        label="Aggregation level:",
        options=["State", "County", "City"],
        inline=True,
        value=get_aggregation_level(),
        on_change=set_aggregation_level,
    )
    return aggregation_level_ui,


@app.cell
def __(config, get_state, mo, set_state):
    state_ui = mo.ui.dropdown(
        label="State:",
        options=config.STATES,
        value=get_state(),
        on_change=set_state,
        allow_select_none=False,
    )
    return state_ui,


@app.cell
def __(config, county_data, mo, set_location):
    county_ui = mo.ui.dropdown(
        label="County:",
        options=county_data.NAME.to_list(), 
        value=config.DEFAULT_LOCATION,
        on_change=set_location,
    )
    return county_ui,


@app.cell
def __(city_data, get_location, mo):
    city_ui = mo.ui.dropdown(
        label="City:",
        options=city_data[get_location()].keys(),
        value = list(city_data[get_location()])[0],
    )
    return city_ui,


@app.cell
def __(
    aggregation_level_ui,
    cities,
    city_ui,
    county_ui,
    get_aggregation_level,
    get_location,
    mo,
    state_ui,
):
    if get_aggregation_level() == "state":
        population = cities["Population(2020)"].sum()
    elif get_aggregation_level() == "county":
        population = cities.loc[get_location().replace(" County","")]["Population(2020)"].sum()
    else:
        population = cities.loc[get_location().replace(" County",""),city_ui.value]["Population(2020)"].sum()
        
    location_items = mo.vstack([
        mo.md("""Set the aggregation level to be an entire state, a specific county, or a city."""),
        mo.hstack([aggregation_level_ui,state_ui,county_ui,city_ui],justify="space-between"),
        mo.md(f"""Population: {population:,.0f}""")
    ])
    return location_items, population


@app.cell
def __(config, mo):
    #
    # Year, EVs, and Chargers
    #

    get_year,set_year = mo.state(config.DEFAULT_YEAR)
    get_number_evs,set_number_evs = mo.state(0.0)
    get_number_chargers,set_number_chargers = mo.state(0.0)
    return (
        get_number_chargers,
        get_number_evs,
        get_year,
        set_number_chargers,
        set_number_evs,
        set_year,
    )


@app.cell
def __(
    config,
    dt,
    get_number_chargers,
    get_number_evs,
    get_year,
    mo,
    set_number_chargers,
    set_number_evs,
    set_year,
):
    full_adoption_year_ui = mo.ui.slider(
        label="Full EV adoption year:",
        start=dt.datetime.now().year,
        stop=dt.datetime.now().year + 50,
        value=dt.datetime.now().year + 20,
        show_value=True,
        debounce=True,
    )
    peak_adoption_year_ui = mo.ui.slider(
        label="Peak EV adoption year:",
        start=dt.datetime.now().year,
        stop=dt.datetime.now().year + 50,
        value=dt.datetime.now().year + 10,
        show_value=True,
        debounce=True,
    )
    adoption_rate_ui = mo.ui.slider(
        label="Peak adoption rate:",
        start=0.0,
        stop=1.0,
        step=0.01,
        value=0.10,
        show_value=True,
        debounce=True,
    )
    year_ui = mo.ui.dropdown(
        label="Study year:",
        value=str(get_year()),
        options=[str(x) for x in range(config.START_YEAR, config.STOP_YEAR + 1)],
        on_change=set_year,
    )
    number_evs_ui = mo.ui.slider(
        label="Number of EVs per capita: ",
        value=get_number_evs(),
        start=0.0,
        stop=2.0,
        step=0.1,
        on_change=set_number_evs,
        debounce=True,
        show_value=True,
    )
    number_chargers_ui = mo.ui.slider(
        label="Number of chargers per capita: ",
        value=get_number_chargers(),
        start=0.0,
        stop=2.0,
        step=0.1,
        on_change=set_number_chargers,
        debounce=True,
        show_value=True,
    )
    return (
        adoption_rate_ui,
        full_adoption_year_ui,
        number_chargers_ui,
        number_evs_ui,
        peak_adoption_year_ui,
        year_ui,
    )


@app.cell
def __(
    adoption_rate_ui,
    full_adoption_year_ui,
    mo,
    number_chargers_ui,
    number_evs_ui,
    peak_adoption_year_ui,
    year_ui,
):
    charger_items = mo.vstack([
        mo.md("""Specify your scenario by selecting the region, targeted year, percentage or number of EV chargers, and rate structures."""),
        mo.hstack([full_adoption_year_ui,peak_adoption_year_ui,adoption_rate_ui],justify='space-between'),
        mo.hstack([year_ui,number_evs_ui,number_chargers_ui],justify='space-between'),
    ])
    return charger_items,


@app.cell
def __(config, get_number_chargers, mo):
    #
    # Tariff
    #

    get_public_fraction, set_public_fraction = mo.state(
        round(config.DEFAULT_PUBLIC), 
        allow_self_loops=True
    )
    get_public_count, set_public_count = mo.state(
        round(config.DEFAULT_PUBLIC * get_number_chargers()), 
        allow_self_loops=True
    )
    get_workplace_fraction, set_workplace_fraction = mo.state(
        round(config.DEFAULT_WORKPLACE), 
        allow_self_loops=True
    )
    get_workplace_count, set_workplace_count = mo.state(
        round(config.DEFAULT_WORKPLACE * get_number_chargers()),
        allow_self_loops=True,
    )
    get_residential_fraction, set_residential_fraction = mo.state(
        round(100 - config.DEFAULT_WORKPLACE - config.DEFAULT_PUBLIC),
        allow_self_loops=True,
    )
    get_residential_count, set_residential_count = mo.state(
        round(
            (100 - config.DEFAULT_WORKPLACE - config.DEFAULT_PUBLIC)
            * get_number_chargers()
        ),
        allow_self_loops=True,
    )
    return (
        get_public_count,
        get_public_fraction,
        get_residential_count,
        get_residential_fraction,
        get_workplace_count,
        get_workplace_fraction,
        set_public_count,
        set_public_fraction,
        set_residential_count,
        set_residential_fraction,
        set_workplace_count,
        set_workplace_fraction,
    )


@app.cell
def __(
    config,
    get_public_count,
    get_public_fraction,
    get_residential_count,
    get_residential_fraction,
    get_workplace_count,
    get_workplace_fraction,
    mo,
    set_public_count,
    set_public_fraction,
    set_residential_count,
    set_residential_fraction,
    set_workplace_count,
    set_workplace_fraction,
):
    def _set_public_fraction(x):
        other = get_workplace_count() + get_residential_count()
        ratio = get_workplace_count()/other
        total = get_public_count() + get_workplace_count() + get_residential_count()
        set_public_fraction(x)
        set_public_count(round(x*total/100))
        set_workplace_fraction(round(ratio*100))
        set_workplace_count(round(other*ratio))
        set_residential_fraction(round(100-ratio*100))
        set_residential_count(round(other*(1-ratio)))

    def _set_workplace_fraction(x):
        set_workplace_fraction(x)

    def _set_residential_fraction(x):
        set_residential_fraction(x)

    def _set_public_count(x):
        total = get_workplace_count() + get_residential_count() + x
        set_public_fraction(round(x/total*100))
        set_workplace_fraction(round(get_workplace_count()/total*100))
        set_residential_fraction(round(get_residential_count()/total*100))
        set_public_count(x)

    def _set_workplace_count(x):
        total = get_public_count() + get_residential_count() + x
        set_public_fraction(round(get_public_count()/total*100))
        set_workplace_fraction(round(x/total*100))
        set_residential_fraction(round(get_residential_count()/total*100))
        set_workplace_count(x)

    def _set_residential_count(x):
        total = get_workplace_count() + get_public_count() + x
        set_public_fraction(round(get_public_count()/total*100))
        set_workplace_fraction(round(get_workplace_count()/total*100))
        set_residential_fraction(round(x/total*100))
        set_residential_count(x)

    public_fraction_ui = mo.ui.slider(
        start=0,
        stop=100,
        value=min(100,max(0,get_public_fraction())),
        on_change=_set_public_fraction,
        debounce=True,
        show_value=True,
    )
    public_count_ui = mo.ui.slider(
        start=0,
        stop=config.MAX_CHARGERS,
        step=1000,
        value=min(config.MAX_CHARGERS,max(0,get_public_count())),
        on_change=_set_public_count,
        debounce=True,
        show_value=True,
    )
    workplace_fraction_ui = mo.ui.slider(
        start=0,
        stop=100,
        value=min(100,max(0,get_workplace_fraction())),
        on_change=_set_workplace_fraction,
        debounce=True,
        show_value=True,
    )
    workplace_count_ui = mo.ui.slider(
        start=0,
        stop=config.MAX_CHARGERS,
        step=1000,
        value=min(config.MAX_CHARGERS,max(0,get_workplace_count())),
        on_change=_set_workplace_count,
        debounce=True,
        show_value=True,
    )
    residential_fraction_ui = mo.ui.slider(
        start=0,
        stop=100,
        value=min(100,max(0,get_residential_fraction())),
        on_change=_set_residential_fraction,
        debounce=True,
        show_value=True,    
    )
    residential_count_ui = mo.ui.slider(
        start=0,
        stop=config.MAX_CHARGERS,
        step=1000,
        value=min(config.MAX_CHARGERS,max(0,get_residential_count())),
        on_change=_set_residential_count,
        debounce=True,
        show_value=True,
    )
    return (
        public_count_ui,
        public_fraction_ui,
        residential_count_ui,
        residential_fraction_ui,
        workplace_count_ui,
        workplace_fraction_ui,
    )


@app.cell
def __(
    mo,
    public_count_ui,
    public_fraction_ui,
    residential_count_ui,
    residential_fraction_ui,
    workplace_count_ui,
    workplace_fraction_ui,
):
    tariff_items = mo.vstack([
        mo.md(f"""Specify the electricity rate schedules for the charging segments.
        <table>
        <tr><th>Location</th><th>Fraction</th><th>Count</th></tr>
        <tr><td>Public</td><td>{public_fraction_ui}%</td><td>{public_count_ui}</td></tr>
        <tr><td>Workplace</td><td>{workplace_fraction_ui}%</td><td>{workplace_count_ui}</td></tr>
        <tr><td>Residential</td><td>{residential_fraction_ui}%</td><td>{residential_count_ui}</td></tr>
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
