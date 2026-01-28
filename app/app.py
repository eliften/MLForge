from dotenv import load_dotenv
from pathlib import Path
import os
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from app.routes import register_routes

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def create_app():

    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )

    server = app.server

    server.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.layout = html.Div([
        dcc.Location(id="url"),
        html.Div(id="app-layout")
    ])

    register_routes(app)
    return app






# import dash, pandas as pd, dash_bootstrap_components as dbc, uuid
# from dash import html, dcc, Input, Output
# from app.pages import main_page
# from flask import request, session
# import dotenv, os

# dotenv.load_dotenv()

# app = dash.Dash(
#     __name__,
#     external_stylesheets=[dbc.themes.BOOTSTRAP],
#     suppress_callback_exceptions=True
# )
# server = app.server
# server.secret_key = os.getenv("SECRET_KEY")

# app.layout = html.Div([
#     dcc.Location(id="url", refresh=False),
#     html.Div(
#         id="app-layout",
#         children=[])])

# def create_session_id():
#     return str(uuid.uuid4())

# @app.callback(
#     Output("app-layout", "children"),
#     Input("url", "pathname")
# )
# def display_page(pathname):
#     if pathname == "/":
#         sid = create_session_id()
#         session["session_id"] = sid
#         return main_page.layout()

#     return html.H1("404: Page not found")

