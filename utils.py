import dash_html_components as html
import dash_core_components as dcc


def Header(app):
    return html.Div([get_header(app), html.Br([]), get_menu()])


def get_header(app):
    header = html.Div(
        [
            html.Div(
                [
                    html.Img(
                        src=app.get_asset_url("modelworks.png"),
                        className="logo",
                    ),
                ],
                className="row",
            ),
            html.Div(
                [
                    html.Div(
                        [html.H5("NFP 73: Decarbonisation of the transport sector")],
                        className="seven columns main-title",
                    ),
                ],
                className="twelve columns",
                style={"padding-left": "0"},
            ),
        ],
        className="row",
    )
    return header


def get_menu():
    menu = html.Div(
        [
            dcc.Link(
                "Overview",
                href="/nfp73/overview",
                className="tab first",
            ),
            dcc.Link(
                "Macroeconomic Results",
                href="/nfp73/macro",
                className="tab",
            ),
            dcc.Link(
                "Private Cars",
                href="/nfp73/cohort",
                className="tab",
            ),
            dcc.Link(
                "Sectoral Results",
                href="/nfp73/sector",
                className="tab"
            ),
            dcc.Link(
                "Distributional Results",
                href="/nfp73/distribution",
                className="tab",
            ),
        ],
        className="row all-tabs",
    )
    return menu


def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table