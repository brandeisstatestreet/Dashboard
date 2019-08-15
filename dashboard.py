import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from datetime import datetime
import pandas as pd
import json

from plotly import graph_objs as go
from plotly.graph_objs import *
from dash.dependencies import Input, Output, State


mapbox_access_token = 'pk.eyJ1Ijoid2VpY2hlbmd6aGFuZyIsImEiOiJjanl0Mzd6OXUwMmo5M2RteDh4NHdvcjZ2In0.SaDXF8pboZXeVGx12M3CXg'
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


df = pd.read_csv('marketindicator.csv')
df['date'] = pd.to_datetime(df['date'].astype(str))
indicators = df.indicator.unique().tolist()
countries = df.country.unique().tolist()

def convert(date):
    date_l=list(str(date))
    del date_l[10:]
    return ''.join(date_l)
def listtostring(list):
    str1 = ' '
    return(str1.join(list))
def listtonum(numList):
    s = ''.join(map(str, numList))
    return int(s)

app = dash.Dash(__name__)
server = app.server
app.title = 'Dashboard'

#app layout
app.layout=html.Div(
    id='root',
    children=[
        html.Div(
            id='header',
            children=[
                html.H4(children='Market Indicator Dashboard'),
                html.P(
                    id='description',
                    children='Map+Table+Chart'
                ),
            ],
        ),
        html.Div(
            className='row',
            id='app-container',
            children=[
                        html.Div(
                            className='three columns',
                            id='left-column',
                            children=[
                                html.Div(
                                    id='date',
                                    children=[
                                        html.P(
                                            id='select-date-text',
                                            children='Filter by date:'
                                        ),
                                        dcc.DatePickerSingle(
                                            id='select-date',
                                            date=datetime(2019, 1, 1),
                                            style={'border':"0px solid black"},
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id='country',
                                    # className='three columns',
                                    children=[
                                        html.Label(
                                            id='select-country-text',
                                            children='Filter by country:',
                                        ),
                                        dcc.Dropdown(
                                            id='select-country',
                                            options=[{'label': str(c), 'value': str(c)} for c in countries],
                                            value=['Germany'],
                                            clearable=True,
                                            multi=True
                                        )
                                    ]
                                ),
                                html.Div(
                                    id='indicator',
                                    children=[
                                        html.Label(
                                            id='select-indicator-text',
                                            children='Select an indicator:',
                                        ),
                                        dcc.Dropdown(
                                            id='select-indicator',
                                            options=[{'label': str(i), 'value': str(i)} for i in indicators],
                                            value=['Index'],
                                            clearable=True,
                                            multi=True
                                            )
                                    ],
                                ),]),
                            html.Div(
                                id='map-container',
                                children=[
                                    dcc.Graph(
                                        id='world-choropleth',
                                        style={"height" : "100%", "width" : "100%"},

                                    ),
                                ],
                            )]),
        # html.Div(
        #     className='charts-container',
        #          children=[
                    html.Div(className='row',
                        id='bottom-row',
                        children=[
                            html.Div(className='six columns',
                            id='table-container',
                            children=[
                                html.P(['Table of market indicators for {}'.format(c) for c in countries],
                                       id='table-title',className='text-padding'),
                                dt.DataTable(
                                    id='table',
                                )
                            ]
                        ),

                            html.Div(className='six columns',
                                id='graph-container',
                                children=[
                                    html.P(['Timeseries plot of {} of {}'.format(k,c) for k in indicators
                                            for c in countries],id='timeseries-title', className='text-padding'),
                                    dcc.Graph(
                                        id='timeseries',
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                 )

@app.callback(
    Output(component_id='world-choropleth', component_property='figure'),
    [Input(component_id='select-date', component_property='date'),
     Input(component_id='select-indicator', component_property='value'),
     Input('select-country','value')],
)
def update_map(selected_date, selected_market_indicator,selected_country):
    # print(selected_market_indicator)
    print('country',selected_country,type(selected_country))
    print('indicator', selected_market_indicator, type(selected_market_indicator))
    if selected_country is None and selected_market_indicator is None:
        dff=df
    elif selected_market_indicator is None and selected_country is not None:
        dff = df[(df['date'] == selected_date)&(df['country']==listtostring(selected_country))]
    elif selected_country is None and selected_market_indicator is not None:
        dff = df[(df['date'] == selected_date) & (df['indicator'] == listtostring(selected_market_indicator))]
    elif selected_country == [] and selected_market_indicator == []:
        dff=df
    else:
        dff = df[(df['date'] == selected_date) & (df['indicator'] == listtostring(selected_market_indicator))
                 & (df['country'] == listtostring(selected_country))]
    data = [
        go.Scattermapbox(
            lat=dff["lat"],
            lon=dff["lon"],
            mode='markers',
            customdata=dff['country'],
            marker=go.scattermapbox.Marker(size=14),
            text=dff['value']
        )
    ]

    layout = dict(
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style=mapbox_style,
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0, pad=0)
        ),

        clickmode= 'select',
        margin=dict(l=0, r=0, t=0, b=0, pad=0)
    )
    fig = dict(data=data,layout=layout)

    return fig

@app.callback(
    Output('timeseries','figure'),
    [Input('table','derived_virtual_data'),
     Input('table', 'derived_virtual_selected_rows'),
     Input('select-indicator', 'value'),
     Input('select-country', 'value')]
)
def update_graph(rows,derived_virtual_selected_rows,selected_market_indicator,selected_country):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    # print('-------',derived_virtual_selected_rows)
    dff = df if rows is None else pd.DataFrame(rows)

    if len(derived_virtual_selected_rows) == 0:
        if selected_country is None and selected_market_indicator is None:
            dff = pd.DataFrame(columns=['date','indicator','country','value'])
        elif selected_market_indicator is None and selected_country is not None:
            dff = pd.DataFrame(columns=['date','indicator','country','value'])
        elif selected_country is None and selected_market_indicator is not None:
            dff = pd.DataFrame(columns=['date', 'indicator', 'country','value'])
        else:
            dff = df[(df['indicator'] == listtostring(selected_market_indicator))
                     & (df['country'] == listtostring(selected_country))]
        return {'data' :
            [go.Scatter(
                 x=dff.date,
                 y=dff.value,
                 mode='lines+markers'
                )],
                'layout' :
                go.Layout(
                    xaxis={'title': 'Time'},
                    yaxis={'title': listtostring(selected_market_indicator)},
                    width=700)
            }

    else:
        return {'data': [
            go.Scatter(
                x=df[(df['indicator']==dff.iloc[i]['indicator'])&(df['country']==dff.iloc[i]['country'])]['date'],
                y=df[(df['indicator']==dff.iloc[i]['indicator'])&(df['country']==dff.iloc[i]['country'])]['value'],
                # text=df2[df2['continent'] == i]['country'],
                mode='lines + markers'
            )for i in derived_virtual_selected_rows
        ],
            'layout': go.Layout(
                xaxis={'title': 'Time'},
                yaxis={'title': listtostring(selected_market_indicator)},
                width=700
            )
        }





@app.callback(Output("table-title", "children"),
              [Input("select-country", "value")])
def update_table_title(selected_country):

    return "Table of market indicators for {}".format(
        listtostring(selected_country)
    )

@app.callback(Output("timeseries-title", "children"),
              [Input("select-country", "value"),
              Input('select-indicator','value')]
              )
def update_plot_title(selected_country,selected_market_indicator):
    return 'Timeseries plot of {} of {}'.format(
        listtostring(selected_market_indicator),listtostring(selected_country)
    )

@app.callback(
    Output('table-container','children'),
    [Input(component_id='select-date', component_property='date'),
     Input(component_id='select-country', component_property='value')])
def update_table(selected_date, selected_country):
    if selected_country is None:
        dff = df[df['country']=='Germany']
    else: dff = df[(df['country'] == listtostring(selected_country))&(df['date']==selected_date)]


    return[
        html.P(['Table of market indicators for {}'.format(c) for c in countries], id='table-title'),
        dt.DataTable(
        id='table',
        columns=[{'name':i,"id":i}for i in dff.iloc[:,[2,3]]],
        data=dff.to_dict('rows'),
        sort_action='native',
        filter_action='native',
        row_selectable='single',
        selected_rows=[])
    ]



if __name__ == '__main__':
    app.run_server(debug=True)