import dash, pandas as pd, dash_bootstrap_components as dbc, uuid
from dash import html, dcc, Input, Output
from frontend import main_page
from flask import request, session

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server
server.secret_key = "BUYILDIZLIGOKLERNEZAMANBASLADIDONMEYE"

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(
        id="app-layout",
        children=[])])

def create_session_id():
    return str(uuid.uuid4())

@app.callback(
    Output("app-layout", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/":
        sid = create_session_id()
        session["session_id"] = sid
        return main_page.layout()

    return html.H1("404: Page not found")

