import geopandas as gpd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd


gdf = gpd.read_file('gis/states.geojson')
df = pd.read_csv(
    'report.csv',
)

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)


@app.callback(
    Output("dropdown-column", "options"),
    [Input("dropdown-tab", "value")]
)
def update_options(tab=df.table.unique()[0]):
    sel = df[df['table'] == tab]
    return list(sel.col.unique())


@app.callback(Output('map', 'figure'),
              [
                  Input('dropdown-tab', 'value'),
                  Input('dropdown-column', 'value'),
                  Input('selected-val', 'value'),
              ]
              )
def draw_map(table, column, val):
    dfs = df[(df.table == table) & (df.col == column)]
    cols = ['state', 'table', 'col', val]
    dfe = dfs.loc[:, cols].copy()
    dfe = dfe.fillna(0)

    gdfs = gdf.merge(dfe, on='state', how='left')
    gdfs.set_index('state', inplace=True)
    fig = px.choropleth_mapbox(
        gdfs,
        geojson=gdfs.geometry,
        locations=gdfs.index,
        color=val,
        center={"lat": 40, "lon": -135},
        mapbox_style="open-street-map",
        zoom=2.5,
        opacity=0.5,
        height=800
    )
    return fig


@app.callback(
    Output("table-info", "data"),
    [Input("dropdown-tab", "value")]
)
def update_table(tab='mapuint'):
    dfs = df[df['table'] == tab].drop_duplicates(subset=['col'])
    dfs = dfs.loc[:, ['col', 'type']]
    return dfs.to_dict('records')


app.layout = html.Div([
    html.H1('Ssurgo stats'),

    dbc.Row([
        dbc.Col([
            html.H5('Table'),
            dcc.Dropdown(
                options=df.table.unique(),
                value=df.table.unique()[0],
                id='dropdown-tab'
            ),
            html.Br(),

            html.H5('Column'),
            dcc.Dropdown(id="dropdown-column"),
            html.Br(),

            dcc.RadioItems(
                ['type', 'empty', 'rows', 'val_cnt', 'minv', 'maxv',
                 'unique_vals', 'duplicates', 'type_ok', ],
                'type_ok', id='selected-val',
                labelStyle={'display': 'block', 'padding': '6px'},
            ),
            html.Br(),
        ], width=2),

        dbc.Col([
            dash.dash_table.DataTable(
                columns=[
                    {'name': nm, 'id': nm} for nm in ['col', 'type']
                ],
                id='table-info',
                style_table={'overflowX': 'scroll', 'maxHeight': '500px'},
                style_header={'backgroundColor': 'gray'},
            )
        ], width=2),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='map'), width=10),
    ]),
], style={'padding': '20px'})


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
