import marimo

__generated_with = "0.7.12"
app = marimo.App(width="full", app_title="")


@app.cell
def __(mo):
    mo.md(
        """
        # Introduction

        Welcome to ASCRIPT, the Advanced Smart Charging Infrastructure Planning Tool.

        ASCRIPT will help you anticipate and manage the growing demand for electric vehicle (EV) charging. With controlled charging gaining traction, accurately estimating future charging loads across utilities, distribution, and transmission becomes crucial. Our tool allows you to input EV load estimates and other assumptions to compare and adjust control settings across different scenarios.

        To use ASCRIPT you must provide input through a series of pages that provide data for the scenario, the analysis, the tariffs, and the electrical network. Then you can view the impacts of the scenario on the network and generate a report documenting the results.

        The first step is provide data about the scenario you wish to study.
        """
    )
    return


@app.cell
def __():
    # mo.md("""Click the [Next] button to begin.""")
    return


@app.cell
def __():
    import marimo as mo
    return mo,


if __name__ == "__main__":
    app.run()
