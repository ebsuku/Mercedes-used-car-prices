import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv("data/final.csv")
df = df[["title", "price", "year", "km", "model", "url", "site"]]


filter_df = df[(df["year"] > 1980) & (df["km"] < 500000)]
fig = px.scatter(filter_df, x="year", y="price", hover_data=["title"])


def generate_table(dataframe, max_rows=50):
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(col) for col in dataframe.columns])),
            html.Tbody(
                [
                    html.Tr(
                        [html.Td(dataframe.iloc[i][col]) for col in dataframe.columns]
                    )
                    for i in range(min(len(dataframe), max_rows))
                ]
            ),
        ]
    )


app.layout = html.Div(
    children=[
        html.H1(
            children="Mercedes Benz Used Car Prices", style={"textAlign": "center"}
        ),
        html.Div(["Input: ", dcc.Input(id="title", value="", type="text")]),
        dcc.Graph(id="all-cars", figure=fig),
        generate_table(filter_df),
    ]
)


@app.callback(
    Output(component_id="all-cars", component_property="children"),
    [Input(component_id="title", component_property="value")],
)
def update_graph(text_value):
    return []


if __name__ == "__main__":
    app.run_server(debug=True)
