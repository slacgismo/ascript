import marimo

__generated_with = "0.1.47"
app = marimo.App(width="full")


@app.cell
def __(load_glm, mo, set_file):
    filename = mo.ui.file(
        filetypes = [".glm",".json"],
        kind = "area",
        multiple = True,
        label = "GridLAB-D model file",
        on_change = lambda x:set_file(load_glm(x[0].name)))
    filename
    return filename,


@app.cell
def __(json, mo, os, pd):
    def load_glm(filename):
        if filename is None:
            return pd.DataFrame({})
        if filename.endswith(".json"):
            jsonfile = filename
        else:
            jsonfile = filename.replace(".glm",".json")
            os.system(f"gridlabd -I {filename} -o {jsonfile}")
        with open(jsonfile, "r") as fh:
            glm = json.load(fh)
            assert glm["application"] == "gridlabd"
            assert glm["version"] >= "4.3.3"
            data = pd.DataFrame(glm["objects"]).transpose()
            data.index.name = "name"
            return data

    get_file, set_file = mo.state(load_glm(None))
    return get_file, load_glm, set_file


@app.cell
def __(get_file):
    data = get_file()
    classes = sorted(data['class'].unique())
    return classes, data


@app.cell
def __(classes, mo, sys):
    get_filter, set_filter = mo.state(dict([[x,True] for x in classes]))
    def set_check(x,y):
        filter = get_filter()
        filter[x] = y
        set_filter(filter)
        print(filter,file=sys.stderr)
    class_checks = [mo.ui.checkbox(value = get_filter()[x],
                              label = x.replace("_"," ").title(),
                              on_change = lambda y:set_check(x,y)
                             ) for x in classes]
    filter = mo.vstack([
        mo.md("""**Filter&nbsp;class**

    ---
    """),
        mo.vstack(class_checks),
        ])
    return class_checks, filter, get_filter, set_check, set_filter


@app.cell
def __(data, get_filter, mo):
    classes_included = [x for x,y in get_filter().items() if y]
    view = data[data['class'].isin(classes_included)]
    table_view = mo.ui.table(view,pagination=True)
    # get_filter().items(),filter
    return classes_included, table_view, view


@app.cell
def __(filter, mo, table_view):
    mo.hstack([filter,table_view])
    return


@app.cell
def __():
    import os, sys, json
    import marimo as mo
    import pandas as pd
    return json, mo, os, pd, sys


if __name__ == "__main__":
    app.run()
