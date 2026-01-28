import dash_bootstrap_components as dbc,pandas as pd, dash, io, base64
from dash import html, dcc, Input, Output, callback, State
from core.redis_client import get_redis, load_model_from_redis, load_problem_type_from_redis, save_df_to_redis, load_df_from_redis, save_model_to_redis, save_problem_type_to_redis
from flask import session

def get_session_id():
    return session.get("session_id")

r = get_redis()

models = {"regression": [
            {"label": "Lineer Regresyon", "value": "linear"},
            {"label": "Ridge", "value": "ridge"},
            {"label": "Lasso", "value": "lasso"},
            {"label": "ElasticNet", "value": "elasticnet"},
            {"label": "Decision Tree", "value": "decision_tree"},
            {"label": "Random Forest", "value": "random_forest"},
            {"label": "XGBoost", "value": "xgboost"},
            {"label": "LightGBM", "value": "lightgbm"},
            {"label": "SVR", "value": "svr"}
        ],
          "classification": [
            {"label": "Logistic Regression", "value": "logistic"},
            {"label": "Decision Tree", "value": "decision_tree"},
            {"label": "Random Forest", "value": "random_forest"},
            {"label": "XGBoost", "value": "xgboost"},
            {"label": "LightGBM", "value": "lightgbm"},
            {"label": "SVM", "value": "svm"},
            {"label": "KNN", "value": "knn"},
            {"label": "Naive Bayes", "value": "naive_bayes"}
        ],
          "clustering": [
            {"label": "KMeans", "value": "kmeans"},
            {"label": "DBSCAN", "value": "dbscan"},
            {"label": "Agglomerative", "value": "hierarchical"},
            {"label": "Gaussian Mixture", "value": "gmm"}
        ],
          "timeseries": [
            {"label": "ARIMA", "value": "arima"},
            {"label": "SARIMA", "value": "sarima"},
            {"label": "Prophet", "value": "prophet"},
            {"label": "LSTM", "value": "lstm"}
        ]}

def layout():
    return html.Div(
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
            dcc.Input(id="project_name", type="text", placeholder="Proje Adı Giriniz"),
            html.Br(),
            html.Br(),
            dbc.RadioItems(
                id="problem-type",
                options=[
                    {"label": "Regresyon", "value": "regression"},
                    {"label": "Sınıflandırma", "value": "classification"},
                    {"label": "Kümeleme", "value": "clustering"},
                    {"label": "Zaman Serisi", "value": "timeseries"},
                ],
                inline=True
            ),
            html.Div(id="output-place")
            ]),
        className="ma-card")),
        dbc.Col(dbc.Card(dbc.CardBody(html.Div(id='output-start')), className="ma-card"))]))

def create_data(df):
    columns = list(df.columns)

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H6("Öznitelikler"),
                dcc.Checklist(
                    id="feature-columns",
                    options=[{"label": col, "value": col} for col in columns],
                    value=[]
                )
            ], width=6),

            dbc.Col([
                html.H6("Hedef Özellik"),
                dbc.RadioItems(
                    id="target-column",
                    options=[{"label": col, "value": col} for col in columns],
                    value=None
                )
            ], width=6)
        ])
    ])

def parse_contents(contents, filename, dType):
    _, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode('ISO-8859-1')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            df = pd.DataFrame()
            return html.Div([
                'Desteklenmeyen dosya türü.'
            ])
    except Exception as e:
        return html.Div([
            'There was an error processing this file.'])

    session_id = get_session_id()
    save_df_to_redis(r, session_id, df, dType)

    return html.Div([
        html.H5(f'{filename} yüklendi')])

@callback(
    Output("output-place", "children"),
    Input("problem-type", "value"),
    prevent_initial_call=True,
)
def update_project_name(type):
    if type is not None:
        if type == "regression" or type == "classification":
            upData = html.Div([dcc.Upload(
                id='upload-data',
                children=html.Div(
                    html.A('Eğitim Verisi Yükle')
                    ),
                style={
                    'width': '80%',
                    'height': '40px',
                    'lineHeight': '30px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center'
                },
                multiple=False
            ),
            html.Div(id='output-data-upload'),
            html.Br(),
            dcc.Upload(
                id='upload-test-data',
                children=html.Div(
                    html.A('Test Verisi Yükle')),
                style={
                    'width': '80%',
                    'height': '40px',
                    'lineHeight': '30px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center'
                },
                multiple=False
            ),
            html.Div(id='output-test-data-upload')])
        else:
            upData = html.Div([dcc.Upload(
                id='upload-data',
                children=html.Div(
                    html.A('Dosya Yükleyin')
                    ),
                style={
                    'width': '80%',
                    'height': '40px',
                    'lineHeight': '30px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center'
                },
                multiple=False
            ),
            html.Div(id='output-data-upload')])
        return html.Div([
                upData,
                dbc.Checklist(
                id="model-type",
                options=models[type],
                inline=True
            ),
            html.Br(),
            html.Button(id="submit-button", n_clicks=0, children="Kaydet")
            ])
    else:
        return dash.no_update

@callback(Output('output-data-upload', 'children'),
          Input('upload-data', 'contents'),
          State('upload-data', 'filename'),
          State('upload-data', 'last_modified'),
          prevent_initial_call=True,
    running=[(Output("submit-button", "disabled"), True, False)])
def update_output(content, name, date):
    if content is not None:
        output = parse_contents(content, name, "train")
        children = [output]
        return children
    else:
        return dash.no_update
    
@callback(Output('output-test-data-upload', 'children'),
          Input('upload-test-data', 'contents'),
          State('upload-test-data', 'filename'),
          State('upload-test-data', 'last_modified'),
          prevent_initial_call=True,
    running=[(Output("submit-button", "disabled"), True, False)])
def update_test_output(content, name, date):
    if content is not None:
        output = parse_contents(content, name, "test")
        children = [output]
        return children
    else:
        return dash.no_update

@callback(Output('output-start', 'children'),
          Input("submit-button", 'n_clicks'),
          State("problem-type", 'value'),
          State("model-type", 'value'),
          prevent_initial_call=True)
def on_submit(n_clicks, problem_type, model_type):
    if n_clicks > 0:
        session_id = get_session_id()
        save_problem_type_to_redis(r, session_id, problem_type)
        save_model_to_redis(r, session_id, model_type)
        problem  = load_problem_type_from_redis(r, session_id)
        model = load_model_from_redis(r, session_id) 
        df_train = load_df_from_redis(r, session_id, "train")
        df_test = load_df_from_redis(r, session_id, "test")
        if problem_type in ["regression", "classification"] and df_train is not None and df_test is not None:
            return html.Div([problem, str(model),
                create_data(df_train)
            ])
        elif problem_type in ["clustering", "timeseries"] and df_train is not None:
            return html.Div([problem, str(model).replace('["',"").replace('"]',"").replace('", "',' '),
                create_data(df_train)]
            )
        else:
            return html.Div([
                'Lütfen önce bir dosya yükleyin.'
            ])
    else:
        return dash.no_update