import marimo

__generated_with = "0.7.19"
app = marimo.App(width="medium")


@app.cell
def __(mo):
    mo.md(
        """
        # Charger placement

        This notebook adds charger to a network based on the distance from the feeder header.
        """
    )
    return


@app.cell
def __(feeder_ui, file_ui, mo):
    mo.hstack([file_ui,feeder_ui])
    return


@app.cell
def __(mo):
    #
    # Upload model data file
    #
    file_ui = mo.ui.file(label="GridLAB-D model",filetypes=[".json"]);
    return file_ui,


@app.cell
def __(file_ui, json):
    #
    # Load model
    #
    _model = (
        json.loads(file_ui.contents().decode("utf-8"))
        if file_ui.value
        else {"application": "gridlabd", "objects": {}}
    )
    assert(_model["application"]=="gridlabd")
    assert("objects" in _model)
    classes = _model["classes"]
    objects = _model["objects"]
    return classes, objects


@app.cell
def __(mo, objects):
    #
    # Select feeder head object
    #
    _swingbus = {f"{x.title().replace('_',' ')} ({y['nominal_voltage']})":x for x,y in objects.items() \
                 if "bustype" in y and y["bustype"] in ["SWING","PQSWING"]}
    _default = (list(_swingbus.keys())[0] if _swingbus else None)
    feeder_ui = mo.ui.dropdown(
        label="Feeder head object:",
        options=_swingbus,
        value=_default,
        allow_select_none=not _swingbus,
    );
    return feeder_ui,


@app.cell
def __(objects):
    #
    # Extract network topology data
    #
    links = {x:y for x,y in objects.items() if "from" in y or "to" in y}
    nodes = {x:objects[x] for x in set([x["from"] for x in links.values()] + 
                                       [x["to"] for x in links.values()])}
    loads = {x:y for x,y in nodes.items() if y["class"] in ["load","triple_load"]}
    nodelinks = {x:[] for x in nodes}
    nodenodes = {x:[] for x in nodes}
    for _link,_data in links.items():
        nodelinks[_data["from"]].append(_link)
        nodenodes[_data["from"]].append(_data["to"])
        nodelinks[_data["to"]].append(_link)
        nodenodes[_data["to"]].append(_data["from"])
    return links, loads, nodelinks, nodenodes, nodes


@app.cell
def __(feeder_ui, links, nodelinks, nodenodes, nodes):
    #
    # Calculate distances to feeder
    #
    def calculate(a, b):
        for link in nodelinks[b]:
            if {a, b} == {links[link]["from"], links[link]["to"]}:
                if not "distance" in nodes[b]:
                    nodes[b]["distance"] = nodes[a]["distance"]
                if "length" in links[link]:
                    nodes[b]["distance"] += float(
                        links[link]["length"].split(" ")[0]
                    )
                for node in nodenodes[b]:
                    if not "distance" in nodes[node]:
                        calculate(b, node)

    for _node in nodes:
        del nodes[_node]["distance"]
    nodes[feeder_ui.value]["distance"] = 0.0
    for _node in nodenodes[feeder_ui.value]:
        calculate(feeder_ui.value, _node)
    maxdist = max([x["distance"] for x in nodes.values()])
    for _node in nodes:
        nodes[_node]["distance"] /= maxdist
    # node distances are normalized (0,1)
    # {x: y["distance"] for x, y in nodes.items()}
    return calculate, maxdist


@app.cell
def __():
    #
    # Place EV chargers according to placement rule
    #
    def probability(x,N):
        return 1.0/N


    return probability,


@app.cell
def __():
    import marimo as mo
    import json
    return json, mo


if __name__ == "__main__":
    app.run()
