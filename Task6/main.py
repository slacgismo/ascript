import marimo

__generated_with = "0.5.2"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    import plotly.express as px
    import pandas as pd
    import leafmap
    import seaborn
    from matplotlib import pyplot

    # May not need the following two lines after marimo releases a new version
    import plotly.io as pio

    pio.renderers.default = "notebook"
    return leafmap, mo, pd, pio, px, pyplot, seaborn


@app.cell
def __(mo):
    mo.md("#Advanced Smart Charging Infrastructure Planning Tool (ASCRIPT)")
    return


@app.cell
def __(mo):
    # Inputs for Charging Segments
    # Aggregation level
    dropdown_agg = mo.ui.dropdown(
        options=["State", "County", "City"], value="County"
    )

    # List of county can get through SG2T
    # May be relevant: https://github.com/slacgismo/SCRIPT/blob/master/UploadToCounty/UploadToPostgresCountiesZips.py
    # Region
    dropdown_region = mo.ui.dropdown(
        options=[
            "Alameda",
            "Contra Costa",
            "Marin",
            "Napa",
            "San Francisco",
            "San Mateo",
            "Santa Clara",
            "Solano",
            "Sonoma",
        ],
        value="Santa Clara",
    )

    # Target year of analysis
    dropdown_year = mo.ui.dropdown(
        options=["2030", "2031", "2032", "2033", "2034", "2035"], value="2034"
    )

    # Initial guess of the number of EVs and chargers based on the region and year
    # If we don't have the data, we can ask the user to input the numbers
    num_number_ev = mo.ui.number(start=0, stop=3000000, step=100, value=500000)
    num_number_charger = mo.ui.number(start=0, stop=3000000, step=10, value=30500)
    return (
        dropdown_agg,
        dropdown_region,
        dropdown_year,
        num_number_charger,
        num_number_ev,
    )


@app.cell
def __(mo, num_number_charger):
    # Variables: number of chargers; pub: public, work: workplace, res: residential
    num_pub_l1 = mo.ui.number(
        start=0, step=1, stop=num_number_charger.value, value=0
    )
    num_pub_l2 = mo.ui.number(
        start=0, step=1, stop=num_number_charger.value, value=9028
    )
    num_pub_l3 = mo.ui.number(
        start=0, step=1, stop=num_number_charger.value, value=2257
    )
    num_work_l1 = mo.ui.number(
        start=0, step=1, stop=num_number_charger.value, value=0
    )
    num_work_l2 = mo.ui.number(
        start=0, step=1, stop=num_number_charger.value, value=9150
    )
    num_work_l3 = mo.ui.number(
        start=0, step=1, stop=num_number_charger.value, value=0
    )
    num_res_l1 = mo.ui.number(
        start=0, step=1, stop=num_number_charger.value, value=2013
    )
    num_res_l2 = mo.ui.number(
        start=0, step=1, stop=num_number_charger.value, value=8052
    )
    num_res_l3 = mo.ui.number(
        start=0, step=1, stop=num_number_charger.value, value=0
    )

    # Radio button to let the user select from (1) setting a ratio to the total number of chargers at each location or (2) specifying the exact number along with their types. The table for charger number setting updates based on this selection.
    radio_charger = mo.ui.radio(
        options=[
            "setting a ratio to the total number of chargers at each location",
            "specifying the exact number along with their types",
        ],
        value="setting a ratio to the total number of chargers at each location",
    )
    return (
        num_pub_l1,
        num_pub_l2,
        num_pub_l3,
        num_res_l1,
        num_res_l2,
        num_res_l3,
        num_work_l1,
        num_work_l2,
        num_work_l3,
        radio_charger,
    )


@app.cell
def __(mo):
    # Tariff can be retrieved from OpenEI
    # Either create a module here or through SG2T
    dropdown_rate_pub = mo.ui.dropdown(options=["TOU-R"], value="TOU-R")

    dropdown_rate_work = mo.ui.dropdown(
        options=["A6 Poly Phase"], value="A6 Poly Phase"
    )

    dropdown_rate_res = mo.ui.dropdown(
        options=["E-TOU-C", "E-TOU-D", "E-TOU-B", "EV2-A", "EV-B"], value="E-TOU-C"
    )
    return dropdown_rate_pub, dropdown_rate_res, dropdown_rate_work


@app.cell
def __(mo):
    # UI elements for setting the number of chargers by ratio
    ratio_charger_pub = mo.ui.number(start=0, stop=100, step=1, value=37)
    ratio_charger_pub_l1 = mo.ui.number(start=0, stop=100, step=1, value=0)
    ratio_charger_pub_l2 = mo.ui.number(start=0, stop=100, step=1, value=80)
    ratio_charger_pub_l3 = mo.ui.number(start=0, stop=100, step=1, value=20)

    ratio_charger_work = mo.ui.number(start=0, stop=100, step=1, value=30)
    ratio_charger_work_l1 = mo.ui.number(start=0, stop=100, step=1, value=0)
    ratio_charger_work_l2 = mo.ui.number(start=0, stop=100, step=1, value=100)
    ratio_charger_work_l3 = mo.ui.number(start=0, stop=100, step=1, value=0)

    ratio_charger_res = mo.ui.number(start=0, stop=100, step=1, value=33)
    ratio_charger_res_l1 = mo.ui.number(start=0, stop=100, step=1, value=20)
    ratio_charger_res_l2 = mo.ui.number(start=0, stop=100, step=1, value=80)
    ratio_charger_res_l3 = mo.ui.number(start=0, stop=100, step=1, value=0)
    return (
        ratio_charger_pub,
        ratio_charger_pub_l1,
        ratio_charger_pub_l2,
        ratio_charger_pub_l3,
        ratio_charger_res,
        ratio_charger_res_l1,
        ratio_charger_res_l2,
        ratio_charger_res_l3,
        ratio_charger_work,
        ratio_charger_work_l1,
        ratio_charger_work_l2,
        ratio_charger_work_l3,
    )


@app.cell
def __(
    num_number_charger,
    num_pub_l1,
    num_pub_l2,
    num_pub_l3,
    num_res_l1,
    num_res_l2,
    num_res_l3,
    num_work_l1,
    num_work_l2,
    num_work_l3,
    ratio_charger_pub,
    ratio_charger_pub_l1,
    ratio_charger_pub_l2,
    ratio_charger_pub_l3,
    ratio_charger_res,
    ratio_charger_res_l1,
    ratio_charger_res_l2,
    ratio_charger_res_l3,
    ratio_charger_work,
    ratio_charger_work_l1,
    ratio_charger_work_l2,
    ratio_charger_work_l3,
):
    # Caculate the number of chargers based on the total number of chargers and the ratio specified by the user
    ratio_to_num_pub = int(
        ratio_charger_pub.value * 0.01 * num_number_charger.value
    )
    ratio_to_num_pub_l1 = int(ratio_charger_pub_l1.value * 0.01 * ratio_to_num_pub)
    ratio_to_num_pub_l2 = int(ratio_charger_pub_l2.value * 0.01 * ratio_to_num_pub)
    ratio_to_num_pub_l3 = int(ratio_charger_pub_l3.value * 0.01 * ratio_to_num_pub)
    ratio_to_num_work = int(
        ratio_charger_work.value * 0.01 * num_number_charger.value
    )
    ratio_to_num_work_l1 = int(
        ratio_charger_work_l1.value * 0.01 * ratio_to_num_work
    )
    ratio_to_num_work_l2 = int(
        ratio_charger_work_l2.value * 0.01 * ratio_to_num_work
    )
    ratio_to_num_work_l3 = int(
        ratio_charger_work_l3.value * 0.01 * ratio_to_num_work
    )
    ratio_to_num_res = int(
        ratio_charger_res.value * 0.01 * num_number_charger.value
    )
    ratio_to_num_res_l1 = int(ratio_charger_res_l1.value * 0.01 * ratio_to_num_res)
    ratio_to_num_res_l2 = int(ratio_charger_res_l2.value * 0.01 * ratio_to_num_res)
    ratio_to_num_res_l3 = int(ratio_charger_res_l3.value * 0.01 * ratio_to_num_res)

    # Total number of chargers from number inputs
    sum_pub_total = num_pub_l1.value + num_pub_l2.value + num_pub_l3.value
    sum_work_total = num_work_l1.value + num_work_l2.value + num_work_l3.value
    sum_res_total = num_res_l1.value + num_res_l2.value + num_res_l3.value
    return (
        ratio_to_num_pub,
        ratio_to_num_pub_l1,
        ratio_to_num_pub_l2,
        ratio_to_num_pub_l3,
        ratio_to_num_res,
        ratio_to_num_res_l1,
        ratio_to_num_res_l2,
        ratio_to_num_res_l3,
        ratio_to_num_work,
        ratio_to_num_work_l1,
        ratio_to_num_work_l2,
        ratio_to_num_work_l3,
        sum_pub_total,
        sum_res_total,
        sum_work_total,
    )


@app.cell
def __(
    dropdown_rate_pub,
    dropdown_rate_res,
    dropdown_rate_work,
    mo,
    num_pub_l1,
    num_pub_l2,
    num_pub_l3,
    num_res_l1,
    num_res_l2,
    num_res_l3,
    num_work_l1,
    num_work_l2,
    num_work_l3,
    radio_charger,
    ratio_charger_pub,
    ratio_charger_pub_l1,
    ratio_charger_pub_l2,
    ratio_charger_pub_l3,
    ratio_charger_res,
    ratio_charger_res_l1,
    ratio_charger_res_l2,
    ratio_charger_res_l3,
    ratio_charger_work,
    ratio_charger_work_l1,
    ratio_charger_work_l2,
    ratio_charger_work_l3,
    ratio_to_num_pub,
    ratio_to_num_res,
    ratio_to_num_work,
    sum_pub_total,
    sum_res_total,
    sum_work_total,
):
    # The table to include the above UI elements to enable the setting of tariff and number of chagers at three different locations: public, workplace, and residential
    table_charger = mo.ui.table(
        data=[
            {
                "Rate": dropdown_rate_pub,
                "Location": "Public",
                "Ratio": mo.md(f"{ratio_charger_pub} %")
                if radio_charger.value
                == "setting a ratio to the total number of chargers at each location"
                else None,
                "Total": sum_pub_total
                if radio_charger.value
                == "specifying the exact number along with their types"
                else ratio_to_num_pub,
                "Level 1": num_pub_l1
                if radio_charger.value
                == "specifying the exact number along with their types"
                else mo.md(f"{ratio_charger_pub_l1} %"),
                "Level 2": num_pub_l2
                if radio_charger.value
                == "specifying the exact number along with their types"
                else mo.md(f"{ratio_charger_pub_l2} %"),
                "Level 3": num_pub_l3
                if radio_charger.value
                == "specifying the exact number along with their types"
                else mo.md(f"{ratio_charger_pub_l3} %"),
            },
            {
                "Rate": dropdown_rate_work,
                "Location": "Workplace",
                "Ratio": mo.md(f"{ratio_charger_work} %")
                if radio_charger.value
                == "setting a ratio to the total number of chargers at each location"
                else " ",
                "Total": sum_work_total
                if radio_charger.value
                == "specifying the exact number along with their types"
                else ratio_to_num_work,
                "Level 1": num_work_l1
                if radio_charger.value
                == "specifying the exact number along with their types"
                else mo.md(f"{ratio_charger_work_l1} %"),
                "Level 2": num_work_l2
                if radio_charger.value
                == "specifying the exact number along with their types"
                else mo.md(f"{ratio_charger_work_l2} %"),
                "Level 3": num_work_l3
                if radio_charger.value
                == "specifying the exact number along with their types"
                else mo.md(f"{ratio_charger_work_l3} %"),
            },
            {
                "Rate": dropdown_rate_res,
                "Location": "Residential",
                "Ratio": mo.md(f"{ratio_charger_res} %")
                if radio_charger.value
                == "setting a ratio to the total number of chargers at each location"
                else " ",
                "Total": sum_res_total
                if radio_charger.value
                == "specifying the exact number along with their types"
                else ratio_to_num_res,
                "Level 1": num_res_l1
                if radio_charger.value
                == "specifying the exact number along with their types"
                else mo.md(f"{ratio_charger_res_l1} %"),
                "Level 2": num_res_l2
                if radio_charger.value
                == "specifying the exact number along with their types"
                else mo.md(f"{ratio_charger_res_l2} %"),
                "Level 3": num_res_l3
                if radio_charger.value
                == "specifying the exact number along with their types"
                else mo.md(f"{ratio_charger_res_l3} %"),
            },
        ],
        selection=None,
    )
    return table_charger,


@app.cell
def __(
    mo,
    num_pub_l1,
    num_pub_l2,
    num_pub_l3,
    num_res_l1,
    num_res_l2,
    num_res_l3,
    num_work_l1,
    num_work_l2,
    num_work_l3,
    pd,
    px,
):
    # Panda DataFrame of location, charger type, and number of chargers
    # This will be used to plot the sunburst chart
    df_charger_details = pd.DataFrame(
        {
            "Location": [
                "Public",
                "Public",
                "Public",
                "Workplace",
                "Workplace",
                "Workplace",
                "Residential",
                "Residential",
                "Residential",
            ],
            "Charger_type": [
                "Public L1",
                "Public L2",
                "Public L3",
                "Workplace L1",
                "Workplace L2",
                "Workplace L3",
                "Residential L1",
                "Residential L2",
                "Residential L3",
            ],
            "Number_of_chargers": [
                num_pub_l1.value,
                num_pub_l2.value,
                num_pub_l3.value,
                num_work_l1.value,
                num_work_l2.value,
                num_work_l3.value,
                num_res_l1.value,
                num_res_l2.value,
                num_res_l3.value,
            ],
        }
    )

    # sunburst chart
    _plot_charger_details = px.sunburst(
        df_charger_details,
        path=["Location", "Charger_type"],
        values="Number_of_chargers",
        title="Number of Chargers by Locations and Types",
    )

    # Customized color mapping; public: blue, workplace: orange, residential: green
    color_mapping = {
        "Public": "#1d6bab",
        "Public L1": "#6fd1f5",
        "Public L2": "#0fafea",
        "Public L3": "#0b7da7",
        "Workplace": "#ff730f",
        "Workplace L1": "#f7ce76",
        "Workplace L2": "#f9a600",
        "Workplace L3": "#b27700",
        "Residential": "#289627",
        "Residential L1": "#77ed9f",
        "Residential L2": "#1cdd5d",
        "Residential L3": "#149e42",
    }
    _plot_charger_details.update_traces(
        marker_colors=[
            color_mapping[cat] for cat in _plot_charger_details.data[-1].labels
        ]
    )

    plot_cd = mo.ui.plotly(_plot_charger_details).style({"width": "40vw"})
    return color_mapping, df_charger_details, plot_cd


@app.cell
def __(
    color_mapping,
    mo,
    pd,
    px,
    ratio_to_num_pub_l1,
    ratio_to_num_pub_l2,
    ratio_to_num_pub_l3,
    ratio_to_num_res_l1,
    ratio_to_num_res_l2,
    ratio_to_num_res_l3,
    ratio_to_num_work_l1,
    ratio_to_num_work_l2,
    ratio_to_num_work_l3,
):
    # Similar to the cell above, but with the numbers calculated from the ratios
    df_charger = pd.DataFrame(
        {
            "Location": [
                "Public",
                "Public",
                "Public",
                "Workplace",
                "Workplace",
                "Workplace",
                "Residential",
                "Residential",
                "Residential",
            ],
            "Charger_type": [
                "Public L1",
                "Public L2",
                "Public L3",
                "Workplace L1",
                "Workplace L2",
                "Workplace L3",
                "Residential L1",
                "Residential L2",
                "Residential L3",
            ],
            "Number_of_chargers": [
                ratio_to_num_pub_l1,
                ratio_to_num_pub_l2,
                ratio_to_num_pub_l3,
                ratio_to_num_work_l1,
                ratio_to_num_work_l2,
                ratio_to_num_work_l3,
                ratio_to_num_res_l1,
                ratio_to_num_res_l2,
                ratio_to_num_res_l3,
            ],
        }
    )

    _plot_charger_loc = px.sunburst(
        df_charger,
        path=["Location", "Charger_type"],
        # color="Charger_type",
        values="Number_of_chargers",
        title="Number of Chargers by Locations and Types",
    )

    _plot_charger_loc.update_traces(
        marker_colors=[
            color_mapping[cat] for cat in _plot_charger_loc.data[-1].labels
        ]
    )

    plot_cl = mo.ui.plotly(_plot_charger_loc).style({"width": "40vw"})
    return df_charger, plot_cl


@app.cell
def __(mo, pd):
    # Ask Alyona
    # Inputs for Feeder Capacity
    dropdown_feeder_id = mo.ui.dropdown(options=[""], value="")
    num_feeder_power = mo.ui.number(start=1, stop=50, step=1, value=20)
    num_feeder_peak = mo.ui.number(start=1, stop=150, step=1, value=110)

    # Inputs for Data Import
    button_network_ini = mo.ui.button(label="Reset")
    button_network_upload = mo.ui.file(
        kind="button", label="Upload Data (CSV/JSON)", filetypes=[".csv", ".json"]
    )

    # Table to include data for network analysis
    df_network = pd.DataFrame(
        {
            "Feeder": [" "],
            "Substation": [" "],
            "Service transformer": [" "],
            "Meter ID": [" "],
            "Building ID": [" "],
            "Building type": [" "],
            "Charging infrastructure": [" "],
            "Coordinates": [" "],
        }
    )
    table_network = mo.ui.table(data=df_network, selection=None)

    df_meter = pd.DataFrame(
        {
            "Meter ID": [" "],
            "Customer Account #": [" "],
            "Tariff": [" "],
        }
    )
    table_meter = mo.ui.table(data=df_meter, selection=None)

    tabs_feeder = mo.tabs(
        {"Distribution System": table_network, "Meter": table_meter}
    )
    return (
        button_network_ini,
        button_network_upload,
        df_meter,
        df_network,
        dropdown_feeder_id,
        num_feeder_peak,
        num_feeder_power,
        table_meter,
        table_network,
        tabs_feeder,
    )


@app.cell
def __(mo, pd, px):
    # Inputs for Load Shape
    # Potentially through SG2T
    switch_advance_loadshape = mo.ui.switch(label="Enable", value=True)

    # from SPEECh model
    # through SG2T
    # need a list of inputs @Sara
    df_loadshape = pd.DataFrame({"Time (hour)": [], "Ratio (%)": []})

    _plot_loadshape = px.line(
        df_loadshape,
        x="Time (hour)",
        y="Ratio (%)",  # ratio of the EVs been charging
        height=450,
        title="Load Shape of the Identified Charging Segment",
    )
    plot_ls = mo.ui.plotly(_plot_loadshape).style({"width": "35vw"})
    slider_shape_x = mo.ui.slider(start=-23, stop=23, step=1, value=0)
    slider_shape_y = mo.ui.slider(start=0, stop=1, step=0.1)

    button_loadshape_upload = mo.ui.file(
        kind="button", label="Upload (CSV)", filetypes=[".csv"]
    )
    return (
        button_loadshape_upload,
        df_loadshape,
        plot_ls,
        slider_shape_x,
        slider_shape_y,
        switch_advance_loadshape,
    )


@app.cell
def __(
    button_loadshape_upload,
    button_network_ini,
    button_network_upload,
    dropdown_agg,
    dropdown_feeder_id,
    dropdown_region,
    dropdown_year,
    mo,
    num_feeder_peak,
    num_feeder_power,
    num_number_charger,
    num_number_ev,
    plot_cd,
    plot_cl,
    plot_ls,
    radio_charger,
    slider_shape_x,
    slider_shape_y,
    switch_advance_loadshape,
    table_charger,
    tabs_feeder,
):
    # Tab for Scenario
    tab1 = mo.vstack(
        [
            mo.md("## Introduction"),
            mo.hstack(
                [
                    mo.md(f"&emsp;&emsp;"),
                    mo.md(
                        "Our web-based app is designed to help you anticipate and manage the growing demand for electric vehicle (EV) charging. With controlled charging gaining traction, accurately estimating future charging loads across utilities, distribution, and transmission becomes crucial. Our tool allows you to input EV load estimates and other assumptions to compare and adjust control settings across different scenarios."
                    ),
                ]
            ),
            mo.md("### Creating a Scenario"),
            mo.hstack(
                [
                    mo.md(f"&emsp;&emsp;"),
                    mo.md(
                        f"Start by navigating to the <b>Charging Segments</b> section. Here, you can set the aggregation level to be the entire state or a specific county or city, and then tailor your scenario by selecting the region, targeted year, percentage or number of EV chargers, and rate structures. Additionally, you have the option to set constraints on <b>Feeder Capacity</b> and upload a list of assets for hotspot analysis within the network. For more detailed analysis, you can enable <b>Advanced Settings</b> to fine-tune the predicted <b>load shape</b> based on factors such as region, year, EV numbers, and rate schedules specified in Charging Segments."
                    ),
                ]
            ),
            mo.Html("<hr>"),
            mo.vstack(
                [
                    mo.vstack(
                        [
                            mo.md("## Charging Segments"),
                            mo.md(
                                f"&emsp;&emsp;Aggregation level: {dropdown_agg}"
                            ),
                            mo.md(f"&emsp;&emsp;Region: {dropdown_region}"),
                            mo.md(f"&emsp;&emsp;Year: {dropdown_year}"),
                            # mo.md(f"&emsp;&emsp;Rate schedule: {dropdown_rate}"),
                            mo.md(f"&emsp;&emsp;Number of EVs: {num_number_ev}"),
                            mo.md(
                                f"&emsp;&emsp;Number of EV chargers: {num_number_charger}"
                            ),
                            mo.hstack(
                                [
                                    mo.md(
                                        f"&emsp;&emsp;Specify the number of EV chargers either by: "
                                    ),
                                    radio_charger,
                                ],
                                justify="start",
                            ),
                            # mo.md(f"&emsp;&emsp;&emsp;&emsp;{radio_charger}"),
                            mo.vstack(
                                [
                                    table_charger,
                                    plot_cd
                                    if radio_charger.value
                                    == "specifying the exact number along with their types"
                                    else plot_cl,
                                ]
                            ),
                        ]
                    ),
                    mo.Html("<hr>"),
                    mo.md("## Feeder Capacity"),
                    mo.md(f"&emsp;&emsp;Names (IDs): {dropdown_feeder_id}"),
                    mo.md(f"&emsp;&emsp;Power constraint: {num_feeder_power} MW"),
                    mo.md(f"&emsp;&emsp;Peak load: {num_feeder_peak} %"),
                    mo.hstack(
                        [
                            mo.md(f"&emsp;&emsp;Data Import: "),
                            button_network_upload,
                            button_network_ini,
                        ],
                        justify="start",
                    ),
                    tabs_feeder,
                    mo.Html("<hr>"),
                    mo.vstack(
                        [
                            mo.md("## Advanced Setting: Load Shape"),
                            plot_ls,
                            mo.hstack(
                                [
                                    mo.md("&emsp;&emsp;Load shape fine tune"),
                                    switch_advance_loadshape,
                                ],
                                justify="start",
                            ),
                            #                        if switch_advance_loadshape.value
                            #                        else mo.md(""),
                            mo.hstack(
                                [
                                    mo.vstack(
                                        [
                                            mo.md(
                                                "&emsp;&emsp;&emsp;&emsp;Shift the peak hour:"
                                            ),
                                            mo.md(
                                                "&emsp;&emsp;&emsp;&emsp;Scale the percentage of active EV drivers:"
                                            ),
                                        ]
                                    ),
                                    mo.vstack(
                                        [
                                            mo.md(
                                                f"{slider_shape_x} {slider_shape_x.value}h"
                                            ),
                                            mo.md(
                                                f"{slider_shape_y} {slider_shape_y.value:.0%}"
                                            ),
                                        ]
                                    ),
                                ],
                                justify="start",
                            )
                            if switch_advance_loadshape.value
                            else mo.md(""),
                            mo.hstack(
                                [
                                    mo.md(
                                        "&emsp;&emsp;_OR_ Upload a load shape profile:"
                                    )
                                    if switch_advance_loadshape.value
                                    else mo.md(""),
                                    button_loadshape_upload
                                    if switch_advance_loadshape.value
                                    else mo.md(""),
                                ],
                                justify="start",
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )
    return tab1,


@app.cell
def __(mo):
    # TODO: control options
    # @Gustavo: These are based on the screenshots of SCRIPT. Will need to include necessary control options
    # contraints for optimization
    dropdown_control_r_timer = mo.ui.dropdown(options=["None"], value="None")
    dropdown_control_w = mo.ui.dropdown(options=["Minpeak"], value="Minpeak")
    dropdown_control_r_smooth = mo.ui.dropdown(
        options=["True", "False"], value="True"
    )
    dropdown_control_day = mo.ui.dropdown(
        options=["Weekday", "Weekend"], value="Weekday"
    )

    # Uploading weather data is optional. If the user doesn't upload one, we'll use the data from GridLAB-D
    button_weather_upload = mo.ui.file(
        kind="button", label="Upload (CSV/TMY3)", filetypes=[".csv", ".tmy3"]
    )
    return (
        button_weather_upload,
        dropdown_control_day,
        dropdown_control_r_smooth,
        dropdown_control_r_timer,
        dropdown_control_w,
    )


@app.cell
def __(mo, pd, px):
    # Simulation outputs
    # All these are only placeholders for now
    button_run_sim = mo.ui.button(label="Run")

    # Energy Demand
    df_energy_demand = pd.DataFrame(
        {
            "Month": [
                "Jan",
                "Jan",
                "Feb",
                "Feb",
                "Mar",
                "Mar",
                "Apr",
                "Apr",
                "May",
                "May",
                "Jun",
                "Jun",
                "Jul",
                "Jul",
                "Aug",
                "Aug",
                "Sep",
                "Sep",
                "Oct",
                "Oct",
                "Nov",
                "Nov",
                "Dec",
                "Dec",
            ],
            "Type": [
                "EV",
                "non-EV",
                "EV",
                "non-EV",
                "EV",
                "non-EV",
                "EV",
                "non-EV",
                "EV",
                "non-EV",
                "EV",
                "non-EV",
                "EV",
                "non-EV",
                "EV",
                "non-EV",
                "EV",
                "non-EV",
                "EV",
                "non-EV",
                "EV",
                "non-EV",
                "EV",
                "non-EV",
            ],
            "GWh/Month": [
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
            ],
        }
    )

    _plot_energy_demand = px.bar(
        df_energy_demand,
        x="Month",
        y="GWh/Month",
        color="Type",
        height=450,
        title="Monthly Energy Consumption Forecast",
    )

    # Grid load
    df_grid_load = pd.DataFrame(
        {
            "Month": [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ],
            "MW (gen)": [
                2000,
                2000,
                2000,
                2000,
                2000,
                2000,
                2000,
                2000,
                2000,
                2000,
                2000,
                2000,
            ],
            "MW (load)": [
                3000,
                3000,
                3000,
                3000,
                3000,
                3000,
                3000,
                3000,
                3000,
                3000,
                3000,
                3000,
            ],
        }
    )
    yaxis_max = df_grid_load["MW (load)"].max() + 1000

    _plot_grid_load = px.line(
        df_grid_load,
        x="Month",
        y=["MW (load)", "MW (gen)"],
        range_y=(0, yaxis_max),
        height=450,
        labels={},
        title="Grid Load & Generation Forecast",
    )

    # EV load
    # df_ev_charging_demand = pd.DataFrame({'Year': [], # target_year±5
    #                                'kWh': []})

    # _plot_ev_charging_demand = px.line(
    #    df_ev_charging_demand,
    #    x="Year",
    #    y="kWh",
    #    height=450,
    #    title="EV Charging Demand Forecast"
    # )

    # Peak demand
    df_peak_demand = pd.DataFrame(
        {"Time of Day": [], "kW_controlled": [], "kW_uncontrolled": []}
    )

    _plot_peak_demand = px.line(
        df_peak_demand,
        x="Time of Day",
        y=["kW_controlled", "kW_uncontrolled"],
        height=450,
        title="Peak Demand Forecast",
    )

    # Stree Test
    text_stress_testing = mo.ui.text_area(
        value="STRESS TESTING RESULTS", disabled=True
    )

    # Hot spot
    radio_hotspot = mo.ui.radio(
        options=["map", "list"],
        value="map",
        label="Choose the representation for hot spot analysis",
    )

    # Placeholder for hot spot analysis
    image_hotspot = mo.image(
        src="https://lh3.googleusercontent.com/proxy/CaVLw6jliKiV3vCbVx4s7-tZpFVWAidZUEMXgLGw9BesybUv2OJG4am78kPgk1hp7vCowvR67r4qaddekudfHIlcx5hl4jTsJpdNRgM3l5c2yZxKSgQzMgGuqsOs3nmE7pswB69eenMxQCZHSrXuRM0OaUU3wBBsMHR1sHHHmN8SNWAnieim05rMi6BFXEFeJDbv",
        alt="placeholder",
        height=425,
        rounded=True,
    ).style({"width": "25vw"})

    plot_ed = mo.ui.plotly(_plot_energy_demand).style({"width": "29vw"})
    plot_gl = mo.ui.plotly(_plot_grid_load).style({"width": "29vw"})
    # plot_ecd = mo.ui.plotly(_plot_ev_charging_demand)
    plot_pd = mo.ui.plotly(_plot_peak_demand).style({"width": "29vw"})
    return (
        button_run_sim,
        df_energy_demand,
        df_grid_load,
        df_peak_demand,
        image_hotspot,
        plot_ed,
        plot_gl,
        plot_pd,
        radio_hotspot,
        text_stress_testing,
        yaxis_max,
    )


@app.cell
def __(
    button_run_sim,
    button_weather_upload,
    dropdown_control_day,
    dropdown_control_r_smooth,
    dropdown_control_r_timer,
    dropdown_control_w,
    image_hotspot,
    mo,
    plot_ed,
    plot_gl,
    plot_pd,
    radio_hotspot,
    text_stress_testing,
):
    # Tab for Analysis
    # @Gustavo: Please check the descriptions below. Because of not suring what are the control options (e.g., what is minpeak for workplace?), the descriptions is incomplete and can be incorrect.
    tab2 = mo.vstack(
        [
            mo.md("## Setting Control Parameters"),
            mo.hstack(
                [
                    mo.md(f"&emsp;&emsp;"),
                    mo.md(
                        f"ASCRIPT allows you to forecast grid load based on various control settings. To get started, go to the <b>Control</b> section. Here, you can (1) Choose whether to enable timers to delay charging sessions until off-peak hours; (2) Decide whether to use a 'smooth' residential profile to estimate load from Level 1 single-family home charging; (3) ......; and (4) Specify if your analysis is focused on weekdays or weekends. <br> You can also customize the future <b>weather</b> data by uploading a file to replace the default forecast. (This step is optional.) <br> After setting your preferences, click the 'run' button to start the <b>Simulation</b>. The results will show the Monthly Energy Consumption Forecast, the Grid Load and Generation Forecast, the Peak Demand Forecast, the Hot Spot Analysis, and the Stress Testing results."
                    ),
                ]
            ),
            mo.Html("<hr>"),
            mo.vstack(
                [
                    #    mo.hstack([mo.md(f"Region: {dropdown_region.value}"), mo.md(f"Year: {dropdown_year.value}"), mo.md(f"Number of EVs: {text_number_ev.value}")], justify='center', gap=30),
                    mo.md("## Control"),
                    mo.hstack(
                        [
                            mo.vstack(
                                [
                                    mo.md(
                                        f"&emsp;&emsp;Residential timer: {dropdown_control_r_timer}"
                                    ),
                                    mo.md(
                                        f"&emsp;&emsp;Workplace: {dropdown_control_w}"
                                    ),
                                ]
                            ),
                            mo.vstack(
                                [
                                    mo.md(
                                        f"Residential smooth: {dropdown_control_r_smooth}"
                                    ),
                                    mo.md(f"Day type: {dropdown_control_day}"),
                                ]
                            ),
                        ],
                        justify="start",
                        gap=10,
                    ),
                ]
            ),
            mo.Html("<hr>"),
            mo.md("## Customize Weather"),
            mo.hstack(
                [
                    mo.md(
                        f"&emsp;&emsp;Upload weather data to override the default forecast:"
                    ),
                    button_weather_upload,
                ],
                justify="start",
            ),
            mo.Html("<hr>"),
            mo.vstack(
                [
                    mo.md("## Simulation"),
                    mo.md(f"&emsp;&emsp;Run simulation: {button_run_sim}"),
                    mo.hstack(
                        [
                            mo.vstack(
                                [
                                    mo.style(
                                        plot_ed,
                                        styles={
                                            "border-width": "1px",
                                            "padding": "0.5rem",
                                        },
                                    ),
                                    mo.style(
                                        mo.vstack(
                                            [
                                                mo.md("Hot spot analysis"),
                                                radio_hotspot,
                                                image_hotspot,
                                            ]
                                        ),
                                        styles={
                                            "border-width": "1px",
                                            "padding": "0.5rem",
                                        },
                                    ),
                                ]
                            ),
                            mo.vstack(
                                [
                                    mo.style(
                                        plot_gl,
                                        styles={
                                            "border-width": "1px",
                                            "padding": "0.5rem",
                                        },
                                    ),
                                    mo.style(
                                        mo.vstack(
                                            [
                                                mo.md("Stress testing results"),
                                                text_stress_testing,
                                            ]
                                        ),
                                        styles={
                                            "border-width": "1px",
                                            "padding": "0.5rem",
                                        },
                                    ),
                                ]
                            ),
                            mo.vstack(
                                [
                                    mo.style(
                                        plot_pd,
                                        styles={
                                            "border-width": "1px",
                                            "padding": "0.5rem",
                                        },
                                    )
                                ]
                            )
                            #            mo.vstack([mo.style(plot_ecd, styles={'border-width': '1px', 'padding': '0.5rem'}), mo.style(mo.vstack([mo.md("Stress testing results"), text_stress_testing]), styles={'border-width': '1px', 'padding': '0.5rem'})])
                            #            mo.style(plot_gl, styles={'border-width': '1px', 'padding': '0.5rem'}), mo.style(mo.vstack([mo.md("Hot spot analysis"), image_hotspot]), styles={'border-width': '1px', 'padding': '0.5rem'}), mo.style(mo.vstack([mo.md("Stress testing results"), text_stress_testing]), styles={'border-width': '1px', 'padding': '0.5rem'})
                        ],
                        widths="equal",
                        gap="1",
                    ),
                ]
            ),
        ],
        gap="2",
    )
    return tab2,


@app.cell
def __(leafmap):
    # Map
    # Had permission issue when it tries to write to /usr/src/app/saq.html (can be other file name). Myles updated the permissions so it works now.
    m = leafmap.Map(center=(40, -100), zoom=6)
    m.add_basemap("HYBRID")
    m.add_basemap("Esri.NatGeoWorldMap")
    m.add_tile_layer(
        url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        name="Google Satellite",
        attribution="Google",
    )

    # Good-to-have function: marker on the map triggers a pop-up that shows the name, type and status
    return m,


@app.cell
def __(mo):
    # Toggle buttons for the visualization of network topology, asset and hot spot on the map
    switch_topo = mo.ui.switch(label="Network Topology")
    switch_asset = mo.ui.switch(label="Asset")
    switch_hotspot = mo.ui.switch(label="Hot Spot")
    return switch_asset, switch_hotspot, switch_topo


@app.cell
def __(m, mo, switch_asset, switch_hotspot, switch_topo):
    # Tab for Map
    tab3 = mo.vstack(
        [
            mo.ui.text(placeholder="address"),
            mo.vstack(
                [
                    m,
                    mo.hstack(
                        [switch_topo, switch_asset, switch_hotspot],
                        justify="center",
                        gap=20,
                    ),
                ]
            ),
        ]
    )
    return tab3,


@app.cell
def __(mo, pd):
    # Tiered charge
    # Need to be linked to the rate selected on the Scenario tab
    # Residential
    df_tiered_charge_res = pd.DataFrame(
        {
            "Period": [1, 1, 2, 2, 3, 3, 4, 4],
            "Tier": [1, 2, 1, 2, 1, 2, 1, 2],
            "Max Usage Units": [
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
            ],
            "Rate $/kWh": [
                0.45082,
                0.53933,
                0.36738,
                0.45589,
                0.34811,
                0.43622,
                0.31976,
                0.40827,
            ],
        }
    )

    # Showing the tiered charge in a table
    table_tiered_charge_res = mo.ui.table(
        df_tiered_charge_res, pagination=None, selection=None
    )

    # Workplace
    df_tiered_charge_work = pd.DataFrame(
        {
            "Period": [1, 1, 2, 2, 3, 3, 4, 4],
            "Tier": [1, 2, 1, 2, 1, 2, 1, 2],
            "Max Usage Units": [
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
            ],
            "Rate $/kWh": [
                0.45082,
                0.53933,
                0.36738,
                0.45589,
                0.34811,
                0.43622,
                0.31976,
                0.40827,
            ],
        }
    )

    table_tiered_charge_work = mo.ui.table(
        df_tiered_charge_work, pagination=None, selection=None
    )

    # Public
    df_tiered_charge_pub = pd.DataFrame(
        {
            "Period": [1, 1, 2, 2, 3, 3, 4, 4],
            "Tier": [1, 2, 1, 2, 1, 2, 1, 2],
            "Max Usage Units": [
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
                "kWh daily",
            ],
            "Rate $/kWh": [
                0.45082,
                0.53933,
                0.36738,
                0.45589,
                0.34811,
                0.43622,
                0.31976,
                0.40827,
            ],
        }
    )

    table_tiered_charge_pub = mo.ui.table(
        df_tiered_charge_pub, pagination=None, selection=None
    )
    return (
        df_tiered_charge_pub,
        df_tiered_charge_res,
        df_tiered_charge_work,
        table_tiered_charge_pub,
        table_tiered_charge_res,
        table_tiered_charge_work,
    )


@app.cell
def __(pd):
    # Weekday schedule
    # Need to be linked to the rate selected on the Scenario tab
    # Residential
    df_weekday_schedule_res = pd.DataFrame(
        {
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "5 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "6 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "7 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "8 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "9 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "5 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "6 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "7 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "8 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "9 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
        },
        index=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
    )

    # Workplace
    df_weekday_schedule_work = pd.DataFrame(
        {
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "5 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "6 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "7 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "8 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "9 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "5 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "6 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "7 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "8 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "9 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
        },
        index=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
    )

    # Public
    df_weekday_schedule_pub = pd.DataFrame(
        {
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "5 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "6 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "7 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "8 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "9 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "5 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "6 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "7 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "8 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "9 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
        },
        index=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
    )
    return (
        df_weekday_schedule_pub,
        df_weekday_schedule_res,
        df_weekday_schedule_work,
    )


@app.cell
def __(pd):
    # Weekend schedule
    # Need to be linked to the rate selected on the Scenario tab
    # Residential
    df_weekend_schedule_res = pd.DataFrame(
        {
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "5 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "6 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "7 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "8 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "9 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "5 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "6 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "7 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "8 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "9 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
        },
        index=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
    )

    # Workplace
    df_weekend_schedule_work = pd.DataFrame(
        {
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "5 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "6 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "7 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "8 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "9 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "5 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "6 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "7 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "8 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "9 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
        },
        index=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
    )

    # Public
    df_weekend_schedule_pub = pd.DataFrame(
        {
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "5 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "6 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "7 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "8 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "9 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "12 am": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "1 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "2 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "3 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "4 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "5 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "6 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "7 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "8 pm": [3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3],
            "9 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "10 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
            "11 pm": [4, 4, 4, 4, 4, 2, 2, 2, 2, 4, 4, 4],
        },
        index=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
    )
    return (
        df_weekend_schedule_pub,
        df_weekend_schedule_res,
        df_weekend_schedule_work,
    )


@app.cell
def __(
    df_weekday_schedule_pub,
    df_weekday_schedule_res,
    df_weekday_schedule_work,
    pyplot,
    seaborn,
):
    # Showing the weekday schedule with a seaborn heatmap
    # Residential
    hm_weekday_res = seaborn.heatmap(
        df_weekday_schedule_res,
        annot=True,
        cmap="viridis",
        linewidths=0.5,
        cbar_kws={"ticks": [0, 1, 2, 3, 4]},
    )
    hm_weekday_res.set_yticklabels(hm_weekday_res.get_yticklabels(), rotation=0)
    pyplot.close(hm_weekday_res.figure)

    # Workplace
    hm_weekday_work = seaborn.heatmap(
        df_weekday_schedule_work,
        annot=True,
        cmap="viridis",
        linewidths=0.5,
        cbar_kws={"ticks": [0, 1, 2, 3, 4]},
    )
    hm_weekday_work.set_yticklabels(hm_weekday_work.get_yticklabels(), rotation=0)
    pyplot.close(hm_weekday_work.figure)

    # Public
    hm_weekday_pub = seaborn.heatmap(
        df_weekday_schedule_pub,
        annot=True,
        cmap="viridis",
        linewidths=0.5,
        cbar_kws={"ticks": [0, 1, 2, 3, 4]},
    )
    hm_weekday_pub.set_yticklabels(hm_weekday_pub.get_yticklabels(), rotation=0)
    pyplot.close(hm_weekday_pub.figure)
    return hm_weekday_pub, hm_weekday_res, hm_weekday_work


@app.cell
def __(
    df_weekend_schedule_pub,
    df_weekend_schedule_res,
    df_weekend_schedule_work,
    pyplot,
    seaborn,
):
    # Showing the weekend schedule with a seaborn heatmap
    # Residential
    hm_weekend_res = seaborn.heatmap(
        df_weekend_schedule_res,
        annot=True,
        cmap="viridis",
        linewidths=0.5,
        cbar_kws={"ticks": [0, 1, 2, 3, 4]},
    )
    hm_weekend_res.set_yticklabels(hm_weekend_res.get_yticklabels(), rotation=0)
    pyplot.close(hm_weekend_res.figure)

    # Workplace
    hm_weekend_work = seaborn.heatmap(
        df_weekend_schedule_work,
        annot=True,
        cmap="viridis",
        linewidths=0.5,
        cbar_kws={"ticks": [0, 1, 2, 3, 4]},
    )
    hm_weekend_work.set_yticklabels(hm_weekend_work.get_yticklabels(), rotation=0)
    pyplot.close(hm_weekend_work.figure)

    # Public
    hm_weekend_pub = seaborn.heatmap(
        df_weekend_schedule_pub,
        annot=True,
        cmap="viridis",
        linewidths=0.5,
        cbar_kws={"ticks": [0, 1, 2, 3, 4]},
    )
    hm_weekend_pub.set_yticklabels(hm_weekend_pub.get_yticklabels(), rotation=0)
    pyplot.close(hm_weekend_pub.figure)
    return hm_weekend_pub, hm_weekend_res, hm_weekend_work


@app.cell
def __(
    dropdown_rate_res,
    hm_weekday_res,
    hm_weekend_res,
    mo,
    table_tiered_charge_res,
):
    # Sub tab of Tariff: Residential
    tab_tariff_res = mo.vstack(
        [
            mo.md(
                f"This page shows the detailed charge structure and schedule of <i>{dropdown_rate_res.value}</i>, based on the <b>scenario</b> you created"
            ),
            mo.md("## Tiered Energy Usage Charge Structure"),
            table_tiered_charge_res,
            mo.Html("<hr>"),
            mo.hstack(
                [
                    mo.vstack([mo.md("## Weekday Schedule"), hm_weekday_res]),
                    mo.vstack([mo.md("## Weekend Schedule"), hm_weekend_res]),
                ]
            ),
        ]
    )
    return tab_tariff_res,


@app.cell
def __(
    dropdown_rate_work,
    hm_weekday_work,
    hm_weekend_work,
    mo,
    table_tiered_charge_work,
):
    # Sub tab of Tariff: Workplace
    tab_tariff_work = mo.vstack(
        [
            mo.md(
                f"This page shows the detailed charge structure and schedule of <i>{dropdown_rate_work.value}</i>, based on the <b>scenario</b> you created"
            ),
            mo.md("## Tiered Energy Usage Charge Structure"),
            table_tiered_charge_work,
            mo.Html("<hr>"),
            mo.hstack(
                [
                    mo.vstack([mo.md("## Weekday Schedule"), hm_weekday_work]),
                    mo.vstack([mo.md("## Weekend Schedule"), hm_weekend_work]),
                ]
            ),
        ]
    )
    return tab_tariff_work,


@app.cell
def __(
    dropdown_rate_pub,
    hm_weekday_pub,
    hm_weekend_pub,
    mo,
    table_tiered_charge_pub,
):
    # Sub tab of Tariff: Public
    tab_tariff_pub = mo.vstack(
        [
            mo.md(
                f"This page shows the detailed charge structure and schedule of {dropdown_rate_pub.value}, based on the <b>scenario</b> you created"
            ),
            mo.md("## Tiered Energy Usage Charge Structure"),
            table_tiered_charge_pub,
            mo.Html("<hr>"),
            mo.hstack(
                [
                    mo.vstack([mo.md("## Weekday Schedule"), hm_weekday_pub]),
                    mo.vstack([mo.md("## Weekend Schedule"), hm_weekend_pub]),
                ]
            ),
        ]
    )
    return tab_tariff_pub,


@app.cell
def __(mo, tab_tariff_pub, tab_tariff_res, tab_tariff_work):
    # Tab for Tariff
    tab_tariff = mo.tabs(
        {
            "Public": tab_tariff_pub,
            "Workplace": tab_tariff_work,
            "Residential": tab_tariff_res,
        }
    )
    return tab_tariff,


@app.cell
def __(mo):
    # Plan to let the user choose what they want to show on the report
    checkbox_plot_energy = mo.ui.checkbox()
    checkbox_plot_load = mo.ui.checkbox()
    checkbox_plot_peak = mo.ui.checkbox()
    return checkbox_plot_energy, checkbox_plot_load, checkbox_plot_peak


@app.cell
def __(
    dropdown_region,
    dropdown_year,
    mo,
    num_feeder_peak,
    num_feeder_power,
    num_number_ev,
    radio_charger,
    ratio_to_num_pub,
    ratio_to_num_res,
    ratio_to_num_work,
    sum_pub_total,
    sum_res_total,
    sum_work_total,
):
    # Description to be included in the report
    if radio_charger.value == "specifying the exact number along with their types":
        summary = mo.md(
            f"The simulated results in this report are generated based on the following assumptions:<br> &emsp;&emsp;1. There will be {num_number_ev.value} EVs in {dropdown_region.value} in {dropdown_year.value}.<br> &emsp;&emsp;2. There will be {sum_pub_total} public chargers, {sum_work_total} chargers at the workplace, and {sum_res_total} chargers at residential homes.<br> &emsp;&emsp;3. The maximum power flowing in the feeders is limited to {num_feeder_power.value}kW, with allowing {num_feeder_peak.value}% peak load.<br>If you need to simulate different scenarios, you can adjust the parameters through the ASCRIPT App and rerun the simulation."
        )
    else:
        summary = mo.md(
            f"The simulated results in this report are generated based on the following assumptions:<br> &emsp;&emsp;1. There will be {num_number_ev.value} EVs in {dropdown_region.value} in {dropdown_year.value}.<br> &emsp;&emsp;2. There will be {ratio_to_num_pub} public chargers, {ratio_to_num_work} chargers at the workplace, and {ratio_to_num_res} chargers at residential homes.<br> &emsp;&emsp;3. The maximum power flowing in the feeders is limited to {num_feeder_power.value}kW, with allowing {num_feeder_peak.value}% peak load.<br>If you need to simulate different scenarios, you can adjust the parameters through the ASCRIPT App and rerun the simulation."
        )
    return summary,


@app.cell
def __(
    image_hotspot,
    mo,
    plot_ed,
    plot_gl,
    plot_pd,
    summary,
    text_stress_testing,
):
    # Tab for Report
    tab4 = mo.vstack(
        [
            mo.callout(summary),
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.style(
                                plot_ed,
                                styles={
                                    "border-width": "1px",
                                    "padding": "0.5rem",
                                },
                            ),
                            mo.style(
                                plot_pd,
                                styles={
                                    "border-width": "1px",
                                    "padding": "0.5rem",
                                },
                            ),
                            mo.style(
                                mo.vstack(
                                    [mo.md("Hot spot analysis"), image_hotspot]
                                ),
                                styles={
                                    "border-width": "1px",
                                    "padding": "0.5rem",
                                },
                            ),
                        ]
                    ),
                    mo.vstack(
                        [
                            mo.style(
                                plot_gl,
                                styles={
                                    "border-width": "1px",
                                    "padding": "0.5rem",
                                },
                            ),
                            mo.style(
                                mo.vstack(
                                    [
                                        mo.md("Stress testing results"),
                                        text_stress_testing,
                                    ]
                                ),
                                styles={
                                    "border-width": "1px",
                                    "padding": "0.5rem",
                                },
                            ),
                        ]
                    ),
                ],
                widths="equal",
                gap="1",
            ),
        ]
    ).style({"width": "816px"})
    # 1-inch=96px
    return tab4,


@app.cell
def __(mo, tab1, tab2, tab3, tab4, tab_tariff):
    mo.tabs(
        {
            "Scenario": tab1,
            "Analysis": tab2,
            "Tariff": tab_tariff,
            "Map": tab3,
            "Report": tab4,
        }
    )
    return


if __name__ == "__main__":
    app.run()

