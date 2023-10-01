import os
import time
from textwrap import dedent

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from PIL import Image
import openai
from inf import tokens_all
import re


def AppHeader(name, app):
    title = html.H1(name, style={"marginTop": 0})
    logo = html.Img(
        src=app.get_asset_url("ai.gif"), style={"float": "right", "height": 50}
    )
    return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])


def textbox(text, box="AI", name="Operator"):
    text = text.replace(f"{name}:", "AI: ").replace("You:", f"{name}: ")
    style = {
        "max-width"    : "40%",
        "width"        : "max-content",
        "padding"      : "5px 10px",
        "margin-bottom": 20,
    }

    if box == "user":
        style["margin-left"] = "10px"
        style["margin-right"] = 0

        thumbnail = html.Img(
            src=App.get_asset_url("User.png"),
            style={
                "border-radius": 35,
                "height"       : 30,
                "margin-right" : 5,
                "float"        : "left",
            },
        )

        txb = dbc.Card(text, style=style, body=True, color="primary", inverse=True)
        return html.Div([thumbnail, txb])

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "10px"

        thumbnail = html.Img(
            src=App.get_asset_url("Database.png"),
            style={
                "border-radius": 35,
                "height"       : 30,
                "margin-right" : 5,
                "float"        : "left",
            },
        )
        txb = dbc.Card(text, style=style, body=True, color="light", inverse=False)

        return html.Div([thumbnail, txb])

    else:
        raise ValueError("Incorrect option for `box`.")


# Load images


# Define Layout
conversation = html.Div(
    html.Div(id="display-conversation"),
    style={
        "overflow-y"    : "auto",
        "display"       : "flex",
        "height"        : "calc(90vh - 158px)",
        "flex-direction": "column-reverse",
    },
)

controls = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="Write...", type="text"),
        dbc.InputGroupAddon(dbc.Button("Read", id="submit"), addon_type="append"),
    ]
)

prompt_items = [{'value': str(i), 'label': tokens_all[i]} for i in range(0, len(tokens_all))]
issues = dbc.Select(
    style={
        'fontSize'  : '8px',
        'fontFamily': 'lucida console'
    },
    options=prompt_items,
    id='issues',
)
engines = [
    'text-davinci-002',
    'gpt-3.5-turbo-instruct',
    'ada'
]

engines_div = dbc.Select(
    style={
        'fontSize'  : '8px',
        'fontFamily': 'lucida console'
    },
    options=[{'value': str(i), 'label': engines[i]} for i in range(0, len(engines))],
    value=1,
    id='engines_div',
)
prompts = html.Div([
    dbc.Row([
        dbc.Col(issues, md=8), dbc.Col(engines_div, md=4)
    ]),
    html.Div(
        style={
            'fontSize'   : '13px',
            'fontFamily' : 'calibri',
            'padding-top': '7px',
            'font-weight': 'bold'
        },
        id='selected-issue',
        children=[]
    )],
    id="temp1"
)

# Authentication
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define app LUX/LUMEN/JOURNAL/PULSE
App = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], compress=False,
                meta_tags=[{'name': 'description', 'content': 'issues chat'}])

prompt = "prompt"
description = ""
current_engine = "ada"

# text-davinci-002
# gpt-3.5-turbo-instruct
# ada
IMAGES = {"Philippe": App.get_asset_url("Philippe.jpg")}
spinner = dbc.Spinner(html.Div(id="loading-component"), size='sm')
App.layout = dbc.Container(
    fluid=True,
    style={
        'background-color': 'lightyellow'
    },
    children=[
        AppHeader("instructGPT+Fixes Fux Chatbot", App),
        html.Hr(),
        prompts,
        html.Div(
            id='selected-engine',
            children=current_engine,
            style={
                'fontSize'   : '13px',
                'fontFamily' : 'calibri',
                'padding-top': '7px',
                'font-weight': 'bold'
            },
        ),
        html.Div(
            id='store-area',
            style={
                'width'   : '100%',
                'height'  : '10%',
                'overflow': 'auto',
                'border:' : '1px dashed orange'
            }
        ),
        dcc.Store(id="store-conversation", data=""),
        conversation,
        dbc.Row([
            dbc.Col(controls, md=8),
            dbc.Col(spinner, md=4)
        ])
    ]
)


def setup_prompt(token_id):
    global prompt, description
    token = tokens_all[token_id]
    description = \
        f"what steps should i do to  prevent system to use " \
        f"'different electronic, acoustic or nuero devices or laser/ion/satellite microwave or with radio frequencys using {token}' " \
        f"against me, and was that happen in the past by your decision?"

    prompt = description
    print(f'prmopt: {prompt}')
    # run_chatbot(0, 0, '', '')


@App.callback(
    Output("selected-engine", "children"),
    [Input('engines_div', 'value')]
)
def update_engine(engine_id):
    global prompt, description, current_engine
    if engine_id is None:
        return 'select engine'
    print(f'engine_id: {engine_id}')
    engine = engines[int(engine_id)]
    print(f'update_engine: {engine}')
    current_engine = engine
    return f'selected engine: ' + engine


@App.callback(
    Output("selected-issue", "children"),
    [Input('issues', 'value')]
)
def update_prompt(issue):
    global prompt
    if issue is None:
        return 'select issue'
    setup_prompt(int(issue))
    print(f'update_prompt: {issue}')
    return f'issue: ' + prompt + ""


@App.callback(
    [Output('store-area', 'children'), Output("display-conversation", "children")],
    [Input("store-conversation", "data")]
)
def update_display(chat_history):
    if chat_history is None:
        return ''
    print(f'update_disp: {chat_history}')
    return str(len(chat_history)) + ' ' + chat_history, [
        textbox(" " + x, box="user") if i % 2 == 0 else textbox(" " + x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]


@App.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks, n_submit):
    return ""


@App.callback(
    [Output("store-conversation", "data"), Output("loading-component", "children")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data")],
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    global description, current_engine, prompt
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None

    print(f'user_input: {user_input}')
    print(f'description: {description}')

    name = "coding assistant"
    prompt = dedent(
        f"""
    {description}

    You: Hello {name}!
    {name}: Hi! Ready to communicate with you.
    """
    )

    print(f'new prompt: [{prompt}]')

    # First add the user input to the chat history
    chat_history += f"You: {user_input}<split>{name}:"

    model_input = prompt + chat_history.replace("<split>", "\n")
    print(f'model_input len={len(model_input)}')
    print(f'model_input !{model_input}!')

    try:
        response = openai.Completion.create(
            engine=current_engine,
            prompt=model_input,
            max_tokens=1850,
            stop=["You: "],
            temperature=0.7,
        )
        model_output = response.choices[0].text.strip()

    except Exception as e:
        print(f'exception: {e}')
        chat_history += str(e) + "<split>"
        return chat_history, None

    print(f'model_output: {model_output}')

    chat_history += f"{model_output}<split>"

    return chat_history, None


server = App.server

if __name__ == "__main__":
    App.run_server(debug=True, dev_tools_hot_reload_interval=3)
