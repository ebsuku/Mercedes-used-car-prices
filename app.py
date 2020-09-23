import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import humanize


# external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app = dash.Dash(__name__)

df = pd.read_csv("data/final.csv")
df["webpage"] = df["site"] + df["url"]
df = df[["title", "price", "year", "km", "model", "webpage"]]
df = df[(df["year"] > 1980) & (df["km"] < 500000) & (df["price"] > 1000)]

total_cars = df["title"].count()
total_price = df["price"].sum()
total_km = df["km"].sum()
total_model = len(df["model"].unique())

car_models = df["model"].unique()
model_options = [{"label": i, "value": i} for i in car_models]
model_options += [{"label": "All", "value": ""}]
model_options.sort(key=lambda x: x["value"])

year = df["year"].unique()
year.sort()

app.layout = html.Div(
    children=[
        html.H1(children="Mercedes Benz Used Car Prices", className="title"),
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Total Cars", className="title"),
                        html.H4(humanize.intcomma(total_cars), className="subtitle"),
                    ],
                    className="column",
                ),
                html.Div(
                    [
                        html.H3("Car Classes", className="title"),
                        html.H4(total_model, className="subtitle"),
                    ],
                    className="column",
                ),
                html.Div(
                    [
                        html.H3("Total Kms", className="title"),
                        html.H4(humanize.intcomma(total_km), className="subtitle"),
                    ],
                    className="column",
                ),
                html.Div(
                    [
                        html.H3("Total Cost", className="title"),
                        html.H4(
                            f"R {humanize.intcomma(total_price)}", className="subtitle"
                        ),
                    ],
                    className="column",
                ),
            ],
            className="columns",
        ),
        html.H2(children="Car Class Summary", className="title"),
        html.Div(
            children=[
                "Select Year",
                dcc.Slider(
                    id="year-slider",
                    min=df["year"].min(),
                    max=df["year"].max(),
                    value=df["year"].min(),
                    marks={str(year): str(year) for year in df["year"].unique()},
                    step=None,
                ),
            ]
        ),
        html.Div(
            className="columns",
            children=[
                html.Div(
                    className="column is-half", children=[dcc.Graph(id="avg-price")]
                ),
                html.Div(className="column is-half", children=[dcc.Graph(id="avg-km")]),
            ],
        ),
        html.Div(
            className="columns",
            children=[
                html.Div(className="column", children=[dcc.Graph(id="class-price")]),
                html.Div(className="column", children=[dcc.Graph(id="class-km")]),
            ],
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
    [
        Output("class-price", "figure"),
        Output("class-km", "figure"),
        Output("avg-price", "figure"),
        Output("avg-km", "figure"),
    ],
    [Input("year-slider", "value")],
)
def update_class_graphs(year_value):
    """
    update the class values based on the year.
    """
    year_df = df[df["year"] == year_value]

    price_df = year_df.groupby(["model"])["price"].sum()
    price_fig = px.bar(price_df, x=price_df.index, y="price", title="Total Cost")

    km_df = year_df.groupby(["model"])["km"].sum()
    km_df = px.bar(km_df, x=km_df.index, y="km", title="Total KM")

    avg_price = year_df.groupby(["model"])["price"].mean()
    avg_price_fig = px.bar(
        avg_price, x=avg_price.index, y="price", title="Average Price"
    )

    avg_km = year_df.groupby(["model"])["km"].mean()
    avg_km_fig = px.bar(avg_km, x=avg_km.index, y="km", title="Average KM")

    return price_fig, km_df, avg_price_fig, avg_km_fig


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

    sort_df = filter_df.sort_values(by=["year"])
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
        x="year",
        y="km",
        hover_data=["title", "year"],
        title="Kilometers Vs Year",
        color="price",
    )

    return price_year, price_km, table, km_year


if __name__ == "__main__":
    app.run_server(debug=True)
