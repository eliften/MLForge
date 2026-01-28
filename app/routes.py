import uuid
from dash import Input, Output
from flask import session
from app.pages import main_page

def create_session_id():
    return str(uuid.uuid4())


def register_routes(app):

    @app.callback(
        Output("app-layout", "children"),
        Input("url", "pathname")
    )
    def display_page(pathname):

        if "session_id" not in session:
            session["session_id"] = create_session_id()

        if pathname == "/":
            return main_page.layout()

        return "404"
