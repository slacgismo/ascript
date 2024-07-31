import marimo

__generated_with = "0.7.12"
app = marimo.App(width="medium", app_title="Button state bug example")


@app.cell
def __(page1, page2):
    pages = {
        "Page 1" : dict(show=page1,prev=None,next="Page 2"),
        "Page 2" : dict(show=page2,prev="Page 1",next=None),
    }
    return pages,


@app.cell
def __(mo):
    get_page,set_page = mo.state("Page 1",allow_self_loops=True)
    return get_page, set_page


@app.cell
def __(get_page, mo, pages):
    mo.md(pages[get_page()]["show"])
    return


@app.cell
def __(get_page, mo, pages, set_page):
    #
    # App Navigation
    #
    prev_ui = next_ui = None

    def prev(_):
        if pages[get_page()]["prev"]:
            set_page(pages[get_page()]["prev"])
            global prev_ui
            prev_ui = mo.ui.button(label="Back",on_click=prev,disabled=pages[get_page()]["prev"] is None)

    def next(_):
        if pages[get_page()]["next"]:
            set_page(pages[get_page()]["next"])
            global next_ui
            next_ui = mo.ui.button(label="Next",on_click=next,disabled=pages[get_page()]["next"] is None)

    prev_ui = mo.ui.button(label="Back",on_click=prev,disabled=pages[get_page()]["prev"] is None)
    next_ui = mo.ui.button(label="Next",on_click=next,disabled=pages[get_page()]["next"] is None)

    mo.hstack([prev_ui,next_ui],justify='end')
    return next, next_ui, prev, prev_ui


@app.cell
def __():
    import marimo as mo
    page1 = "This is page 1. Click [Next] to go to page 2."
    page2 = "This is page 2. Click [Back] to return to page 1."
    return mo, page1, page2


if __name__ == "__main__":
    app.run()
