import marimo

__generated_with = "0.7.12"
app = marimo.App(
    width="full",
    app_title="ASCRIPT -- Advanced Smart Charging Infrastructure Planning Tool",
)


@app.cell
def __(intro, scenario):
    pages = {
        "Introduction" : dict(show=intro,prev=None,next="Scenario",data=None),
        "Scenario" : dict(show=scenario,prev="Introduction",next=None,data=None),
    }
    return pages,


@app.cell
def __():
    # get_page,set_page = mo.state("Introduction",allow_self_loops=True)
    return


@app.cell
def __():
    # mo.hstack([prev_ui,next_ui],justify='end')
    return


@app.cell
def __():
    # page = await pages[get_page()]["show"].app.embed()
    # pages[get_page()]["data"] = page.defs
    # page.output
    return


@app.cell
def __():
    #
    # App Navigation
    #

    # prev_ui = next_ui = None

    # def prev(_):
    #     if pages[get_page()]["prev"]:
    #         set_page(pages[get_page()]["prev"])
    #         global prev_ui
    #         prev_ui = mo.ui.button(label="Back",on_click=prev,disabled=pages[get_page()]["prev"] is None)

    # def next(_):
    #     if pages[get_page()]["next"]:
    #         set_page(pages[get_page()]["next"])
    #         global next_ui
    #         next_ui = mo.ui.button(label="Next",on_click=next,disabled=pages[get_page()]["next"] is None)

    # prev_ui = mo.ui.button(label="Back",on_click=prev,disabled=pages[get_page()]["prev"] is None)
    # next_ui = mo.ui.button(label="Next",on_click=next,disabled=pages[get_page()]["next"] is None)
    return


@app.cell
def __():
    # mo.hstack([prev_ui,next_ui],justify='end')
    return


@app.cell
async def __(mo, pages):
    mo.carousel([(await x["show"].app.embed()).output for x in pages.values()])
    return


@app.cell
def __():
    import marimo as mo
    import intro
    import scenario
    return intro, mo, scenario


if __name__ == "__main__":
    app.run()
