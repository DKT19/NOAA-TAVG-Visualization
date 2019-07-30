import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import datetime
import pandas as pd
import numpy as np
import time
import sys
import os

# Concatenate to single dataframe
read_path = r'C:/Users/krist/cv/data/NOAA_data/'
list_files = os.listdir(read_path)

for file_num in range(0, len(list_files)):
    read_file = os.path.join(read_path, list_files[file_num])
    if file_num == 0:
        new_df = pd.read_csv(read_file)
    else:
        cur_df = pd.read_csv(read_file)
        new_df = pd.concat([new_df, cur_df], ignore_index = True)

# Find min, max, and unique years
years = list()
unique_years = list()

for row_counter in range(0, len(new_df)):
    years.append(time.strftime('%Y', time.strptime(new_df['Date'][row_counter], '%d %b %y')))
for year in years:
    if year not in unique_years:
        unique_years.append(year)
print('Min year: {}'.format(min(years)))
print('Max year: {}'.format(max(years)))
print('For years:', end = ' ')
for u_year in range(0, len(unique_years)):
    if u_year != len(unique_years) - 1:
        print(unique_years[u_year], end = ', ')
    else:
        print(unique_years[u_year])

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Dash app
external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.H1('Airport Average Temperatures',
        style = {'textAlign': 'center',
                 'color': colors['text']}
        )
    ]),
    html.Div([
        html.Div([
            html.H1(
                id = 'selected-year',
                style = {'fontSize': 60,
                         'color': colors['text']}
            ),
        ],
        style = {'width': '21%', 'display': 'inline-block', 'padding-left': '4%'}
        ),
        html.Div([
            html.H3(
                'Maximum Average Temperature',
                id = 'max-temp-year',
                style = {'fontSize': 12,
                         'color': colors['text']}
            ),
            html.H1(
                id = 'max-temp',
                style = {'fontSize': 30,
                         'color': colors['text'],
                         'padding-left': '10%'}
            )
        ],
        style = {'width': '21%', 'display': 'inline-block'}
        ),
        html.Div([
            html.H3(
                'Minimum Average Temperature',
                id = 'min-temp-year',
                style = {'fontSize': 12,
                         'color': colors['text']}
            ),
            html.H1(
                id = 'min-temp',
                style = {'fontSize': 30,
                         'color': colors['text'],
                         'padding-left': '10%'}
            )
        ],
        style = {'width': '21%', 'display': 'inline-block'}
        ),
        html.Div([
            dcc.Dropdown(
                id = 'airport-select',
                options = [
                    {'label': 'LaGuardia', 'value': 'LGA'},
                    {'label': 'Los Angeles', 'value': 'LAX'},
                    {'label': 'West Palm Beach', 'value': 'WPBA'}
                ],
                value = ['LAX'],
                multi = True
            )
        ],
        style = {'width': '30%', 'display': 'inline-block', 'backgroundColor': colors['background']}
        )
    ]),
    html.Div([
        dcc.Graph(
            id = 'temp-vs-time',
        )
    ],
    style = {'width': '96%', 'padding-left': '2%', 'padding-right': '2%'}
    ),
    html.Div([
        dcc.Slider(
            id = 'year-slider',
            min = 0,
            max = len(unique_years) - 1,
            value = 0,
            marks = {i : str(unique_year) for i, unique_year in enumerate(unique_years)}
        )
    ],
    style = {'width': '96%', 'padding-left': '2%', 'padding-right': '2%', 'backgroundColor': colors['background']}
    )
],
style = {'background': colors['background']}
)

@app.callback(
    Output('selected-year', 'children'),
    [Input('year-slider', 'value')],
    [State('year-slider', 'marks')]
)

def update_year(selected_year_key, marks):
    selected_year = marks[str(selected_year_key)]
    return selected_year

@app.callback(
    Output('max-temp', 'children'),
    [Input('year-slider', 'value'),
     Input('airport-select', 'value')],
    [State('year-slider', 'marks')]
)

def update_max_temp(selected_year_key, airport, marks):
    once = False
    selected_year = marks[str(selected_year_key)]
    for row_counter2 in range(0, len(new_df)):
        if time.strftime('%Y', time.strptime(new_df['Date'][row_counter2], '%d %b %y')) == str(selected_year):
            if once == False:
                filtered_df = new_df.iloc[[row_counter2]]
                once = True
            elif once == True:
                filtered_df = pd.concat([filtered_df, new_df.iloc[[row_counter2]]], ignore_index = True)

    max_temp_list = list()
    for u_location in airport:
        df_by_location = filtered_df[filtered_df['Location'] == u_location]
        max_temp_list.append(df_by_location['TAVG'].max())
    max_temp = max(max_temp_list)

    return '{}'.format(max_temp) + u"\u00b0" + 'F'

@app.callback(
    Output('min-temp', 'children'),
    [Input('year-slider', 'value'),
     Input('airport-select', 'value')],
    [State('year-slider', 'marks')]
)

def update_max_temp(selected_year_key, airport, marks):
    once = False
    selected_year = marks[str(selected_year_key)]
    for row_counter2 in range(0, len(new_df)):
        if time.strftime('%Y', time.strptime(new_df['Date'][row_counter2], '%d %b %y')) == str(selected_year):
            if once == False:
                filtered_df = new_df.iloc[[row_counter2]]
                once = True
            elif once == True:
                filtered_df = pd.concat([filtered_df, new_df.iloc[[row_counter2]]], ignore_index = True)

    min_temp_list = list()
    for u_location in airport:
        df_by_location = filtered_df[filtered_df['Location'] == u_location]
        min_temp_list.append(df_by_location['TAVG'].min())
    min_temp = min(min_temp_list)

    return '{}'.format(min_temp) + u"\u00b0" + 'F'

@app.callback(
    Output('temp-vs-time', 'figure'),
    [Input('year-slider', 'value'),
     Input('airport-select', 'value')],
    [State('year-slider', 'marks')])

def update_figure(selected_year_key, airport, marks):
    once = False
    selected_year = marks[str(selected_year_key)]
    for row_counter2 in range(0, len(new_df)):
        if time.strftime('%Y', time.strptime(new_df['Date'][row_counter2], '%d %b %y')) == str(selected_year):
            if once == False:
                filtered_df = new_df.iloc[[row_counter2]]
                once = True
            elif once == True:
                filtered_df = pd.concat([filtered_df, new_df.iloc[[row_counter2]]], ignore_index = True)

    traces = list()
    for u_location in airport:
        df_by_location = filtered_df[filtered_df['Location'] == u_location]
        traces.append(go.Scatter(
            x = df_by_location['Date'],
            y = df_by_location['TAVG'],
            text = df_by_location['Location'],
            mode = 'markers',
            opacity = 0.7,
            marker = {
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name = u_location
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis = {'title': 'Summer Dates'},
            yaxis = {'title': 'Average Temperature', 'range': [60, 92]},
            margin = {'l': 20, 'b': 80, 't': 40, 'r': 20},
            legend = {'x': 0, 'y': 1},
            hovermode = 'closest',
            plot_bgcolor = colors['background'],
            paper_bgcolor = colors['background'],
            font = {
                'color': colors['text']
            }
        )
    }

if __name__ == '__main__':
    app.run_server(debug = True)