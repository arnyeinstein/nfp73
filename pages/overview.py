import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from utils import Header, make_dash_table

import pandas as pd
import pathlib

import gams
import workdirectory as swd
import os
import gdxtools as gdxt
import plotly_express as px

## Set the dictionaries
work_dir, project_dir, temp_dir, data_dir = swd.workdirectory()

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()

## Get the data
ws = gams.GamsWorkspace()
gdx_file = os.path.join(temp_dir, 'cgecars.gdx')
db = ws.add_database_from_gdx(gdx_file)
year_CGE = int(gdxt.get_parameter(db, 'actyearv').iloc[0, 0])
cars = gdxt.get_parameter(db, 'carsupd')

## Reshape data

cars.rename(columns={'dim1': 'year',
                     'dim2': 'ryr',
                     'dim3': 'trst',
                     'dim4': 'lstkw',
                     'dim5': 'level'},
            inplace=True)
years = cars['year'].unique()

cars = cars.set_index(['ryr', 'trst', 'lstkw', 'year'])
#cars = cars.unstack(level='year')

cars_sum = cars.groupby(['trst', 'year']).sum().reset_index()
fig = px.line(cars_sum, x="year", y="level", color="trst", log_y=True)
fig2 = px.bar(cars_sum, x="year", y="level", color="trst")
fig3 = px.area(cars_sum, x="year", y="level", color="trst")

## Macro economic indicators
## Aggregated results
gdx_file = os.path.join(temp_dir, 'results.gdx')
db = ws.add_database_from_gdx(gdx_file)
results_agg = gdxt.get_parameter(db, 'results_agg')
results_agg.rename(columns={'dim1': 'year',
                            'dim2': 'scenario',
                            'dim3': 'indicator',
                            'dim4': 'level'},
                   inplace=True)
indicators = results_agg['indicator'].unique()

## Static tables
df_fund_facts = pd.read_csv(DATA_PATH.joinpath("df_scenarios.csv"), sep=';')
df_price_perf = pd.read_csv(DATA_PATH.joinpath("df_price_perf.csv"))


def create_layout(app):
    # Page layouts
    return html.Div(
        [
            html.Div([Header(app)]),
            # page 1
            html.Div([
                # Row 3
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5("Project summary"),
                                html.Br([]),
                                html.P(
                                    "\
                                    Using a mix of quantitative and qualitative methods we are examining the ways \
                                    in which the transport sector can drastically reduce its greenhouse gas \
                                    emissions by 2050. Initially, we will collect data from previous research \
                                    and from discussions with various experts during workshops to look for options \
                                    and measures for reducing greenhouse gases in the transport sector. We will \
                                    then develop a range of scenarios for successfully reducing emissions in the \
                                    transport sector by 2050, and calculate the economic effects for Switzerland \
                                    (change in employment, GDP) with an economic equilibrium model. From these \
                                    results and in dialogue with experts and based on an optimisation concept \
                                    we will create a path that will show over time how a new approach to \
                                    mobility can be economically viable.",
                                    style={"color": "#ffffff"},
                                    className="row",
                                ),
                            ],
                            className="product",
                        )
                    ],
                    className="row",
                ),
                # Row 4
                html.Div([
                    html.Div([
                        html.H6(
                            ["Macroeconomic and energy indicators"],
                            className="subtitle padded",
                        ),
                        dcc.Graph(
                            id="graph-2",
                            figure=fig2
                        ),
                        dcc.Dropdown(
                            id='yaxis-column',
                            options=[{'label': ind, 'value': ind} for ind in indicators],
                            value='Consumption (nv)'
                        )
                    ], style={"width": "50%",
                              "float": "left"},
                        className="six columns",
                    ),
                    html.Div(
                        [
                            html.H6(
                                "Private car stock",
                                className="subtitle padded",
                            ),
                            dcc.Graph(
                                id="graph-1",
                                figure=fig
                            ),
                        ], style={"width": "50%",
                                  "float": "left"},
                        className="six columns",  # px
                    ),
                ],
                    className="row",
                    style={"margin-bottom": "35px"},
                ),
                # Row 5
                html.Div([
                    html.Div([
                        html.H6(
                            ["Scenarios analyzed"], className="subtitle padded"
                        ),
                        html.Table(make_dash_table(df_fund_facts)),
                    ],
                        className="six columns",
                    ),
                ], className="row ",
                ),
            ],
                className="sub_page",
            ),
        ], className="page",
    )
