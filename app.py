import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv("data/final.csv")
df["webpage"] = df["site"] + df["url"]
df = df[["title", "price", "year", "km", "model", "webpage"]]


car_models = df["model"].unique()
model_options = [{"label": i, "value": i} for i in car_models]
model_options += [{"label": "All", "value": ""}]
model_options.sort(key=lambda x: x["value"])


def generate_table(dataframe, max_rows=50):
    """
    Sort table from lowest to highest
    """
    sort_df = dataframe.sort(["price"], axis=1)
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(col) for col in sort_df.columns])),
            html.Tbody(
                [
                    html.Tr(
                        [html.Td(dataframe.iloc[i][col]) for col in sort_df.columns]
                    )
                    for i in range(min(len(sort_df), max_rows))
                ]
            ),
        ]
    )


app.layout = html.Div(
    children=[
        html.H1(
            children="Mercedes Benz Used Car Prices", style={"textAlign": "center"}
        ),
        html.Div(
            [
                html.Div(
                    ["Search Title: ", dcc.Input(id="title", value="", type="text")],
                    style={"width": "48%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        "Car Class",
                        dcc.Dropdown(
                            id="model-choice", options=model_options, value=""
                        ),
                    ],
                    style={"width": "48%", "display": "inline-block"},
                ),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="price-year")],
                    style={"width": "48%", "display": "inline-block"},
                ),
                html.Div(
                    [dcc.Graph(id="price-km")],
                    style={"width": "48%", "float": "right", "display": "inline-block"},
                ),
            ]
        ),
        html.Div([dcc.Graph(id="km-year")]),
        html.Table(id="table"),
    ]
)


@app.callback(
    Output("price-year", "figure"),
    Output("price-km", "figure"),
    Output("table", "children"),
    Output("km-year", "figure"),
    [Input("title", "value"), Input("model-choice", "value")],
)
def update_regions(text_value, choice_value):
    filter_df = df[(df["year"] > 1980) & (df["km"] < 500000) & (df["price"] > 1000)]

    if choice_value != "":
        filter_df = filter_df[filter_df["model"] == choice_value]

    if text_value != "":
        filter_df = filter_df[filter_df["title"].str.contains(text_value)]

    sort_df = filter_df.sort_values(by=["price"])
    table = [
        html.Thead(html.Tr([html.Th(col) for col in sort_df.columns])),
        html.Tbody(
            [
                html.Tr([html.Td(sort_df.iloc[i][col]) for col in sort_df.columns])
                for i in range(min(len(sort_df), 50))
            ]
        ),
    ]
    price_year = px.scatter(
        filter_df,
        x="year",
        y="price",
        hover_data=["title"],
        title="Price Vs Year",
        color="km",
    )
    price_km = px.scatter(
        filter_df,
        x="km",
        y="price",
        hover_data=["title", "year"],
        title="Price Vs Kilometers",
        color="year",
    )
    km_year = px.scatter(
        filter_df,
        x="km",
        y="year",
        hover_data=["title", "year"],
        title="Kilometers Vs Year",
        color="price",
    )

    return price_year, price_km, table, km_year


if __name__ == "__main__":
    app.run_server(debug=True)
