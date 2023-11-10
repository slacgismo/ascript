import marimo

__generated_with = "0.1.47"
app = marimo.App(width="full")


@app.cell
def __(mo):
    mo.md("""# Mapping Example

    This example uses <a href="https://plotly.com/python/scattermapbox/" target="_blank">Mapbox</a> in `plotly.express` to build a scatter plot on a street map. The switch enables the satellite view.
    """)
    return


@app.cell
def __(mo, set_map):
    view_button = mo.ui.switch(value=False,on_change=set_map)
    mo.hstack([mo.md("Satellite view:"),view_button],justify='start')
    return view_button,


@app.cell
def __(get_view):
    get_view()
    return


@app.cell
def __(mo, nodes, px):
    def get_map(satellite):
        map = px.scatter_mapbox(nodes, 
                                lat="latitude", 
                                lon="longitude", 
                                hover_name="name", 
                                hover_data = {"latitude":False,"longitude":False,
                                              "class":True,"phases":True,"nominal_voltage":True,
                                              "voltage_A":True,"voltage_B":True,"voltage_C":True},
                                color_discrete_sequence=["fuchsia"], 
                                zoom=15)
        if satellite:
            map.update_layout(
                mapbox_style="white-bg",
                mapbox_layers=[
                    {
                        "below": 'traces',
                        "sourcetype": "raster",
                        "sourceattribution": "United States Geological Survey",
                        "source": [
                            "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                        ]
                    }
                  ])
            map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        else:    
            map.update_layout(mapbox_style="open-street-map")
            map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return map

    def set_map(satellite):
        set_view(get_map(satellite))

    get_view, set_view = mo.state(get_map(False))
    return get_map, get_view, set_map, set_view


@app.cell
def __(json, mo, os, pd):
    def get_nodes(filename):
        jsonfile = filename.replace(".glm", ".json")
        if not os.path.exists(jsonfile):
            os.system(f"gridlabd -I {filename} -o {jsonfile} || rm {jsonfile}")
        with open(jsonfile, "r") as fh:
            glm = json.load(fh)
            assert glm["application"] == "gridlabd"
            assert glm["version"] >= "4.3.3"
            data = pd.DataFrame(glm["objects"]).transpose()
            data.index.name = "name"
            data.reset_index(inplace=True)
            data['latitude'] = [float(x) for x in data['latitude']]
            data['longitude'] = [float(x) for x in data['longitude']]
            nodes = data.loc[~data["latitude"].isnull()]
            lines = None # pd.DataFrame(result["lines"])
            return data,nodes,lines
        raise Exception("file not found")

    data,nodes,lines = get_nodes("example.glm")
    mo.ui.table(data)
    return data, get_nodes, lines, nodes


@app.cell(disabled=True)
def __():
            # DRAW NODES
            # print(df,file=sys.stderr)
            # result = {"nodes" : [], "lines" : []}
            # for name, data in glm["objects"].items():
            #     if "latitude" in data and "longitude" in data \
            #             and "from" not in data and "to" not in data:
            #         result["nodes"].append(
            #             [
            #                 name,
            #                 float(data["latitude"]),
            #                 float(data["longitude"]),
            #                 data["class"],
            #             ]
            #         )
    return


@app.cell(disabled=True)
def __():
            # DRAW LINES
            # import plotly.graph_objects as go
            # fig = go.Figure()
            # for _,row in df.iterrows():
            #     fig.add_trace(go.Scattermapbox(mode='lines',
            #                                    lon=[row['source_lon'], row['sink_lon']],
            #                                    lat=[row['source_lat'], row['sink_lat']],
            #                                    line_color='green',
            #                                    name=row['source_name']
            #                                   ))
            # fig.update_layout(
            #     height=600,
            #     mapbox=dict(
            #         style='open-street-map',
            #         zoom=4,
            #         center=dict(lon=df['source_lon'].mean(), lat=df['source_lat'].mean())
            #     )
            # )
            # fig.show()

    return


@app.cell
def __():
    import os, sys, json
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    return json, mo, os, pd, px, sys


if __name__ == "__main__":
    app.run()
