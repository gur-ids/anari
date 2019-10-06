import dash
import dash_html_components as html
import hockey_player_model as hpm
import hockey_player_fun as hpf
import graphs as g
import view as v
import pandas as pd
import team_model as tm
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# initial pre-processing
df = hpm.pre_process('../data/nhl_2017-2018.csv')
teams = tm.pre_process('../data/team_stats_2017-2018.csv')

# handling pre-processed data
offenders = hpm.offenders(df)
defenders = hpm.defenders(df)
tm.is_beneficial_to_team(df)


top_players = hpf.filter_players_by_points(df, 50)

# produced view
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions']=True
'''
app.layout=html.Div(children=[
    html.H4(children='NHL meik mani'),
    html.P('Here is a table of the top scorers'),
    html.P(children=v.top_players_gp_mean_text(top_players)),
    g.box_plot_by_points(offenders),
    g.scatter_plot_teams('test_id2', teams),
    g.scatter_plot_players('test_id', top_players)
])
'''
test_df = pd.read_csv('../data/preprocessed2.csv')
print(test_df)
available_indicators = test_df['Indicator Name'].unique()
app.suppress_callback_exceptions=True
app.layout = html.Div([
    html.H1('Dash Tabs component demo'),
    dcc.Tabs(id="tabs-example", value='basic-info-tab', children=[
        dcc.Tab(label='Basic Info', value='basic-info-tab'),
        dcc.Tab(label='Make statistics great again', value='great-stat-tab'),
        dcc.Tab(label='test', value='test')
    ]),
    html.Div(id='tabs-content-example'),
    html.Div(id='tabs-content-example2')
])

@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'basic-info-tab':
        return html.Div(children=[
            html.H4(children='NHL meik mani'),
            html.P('Here is a table of the top scorers'),
            html.P(children=v.top_players_gp_mean_text(top_players)),
            g.box_plot_by_points(offenders),
            g.scatter_plot_teams('test_id2', teams),
            g.scatter_plot_players('test_id', top_players)
        ])
    elif tab == 'great-stat-tab':
        return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                id='graph-2-tabs',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [5, 10, 6],
                        'type': 'bar'
                    }]
                }
            )
        ])        

def is_test_tab_showing(tab):
        if tab != 'test':
            return 'none'
        return 'block'

@app.callback(Output('tabs-content-example2', 'children'),
              [Input('tabs-example', 'value')])
def render_content2(tab):
    return html.Div([
        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Fertility rate, total (births per woman)'
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Life expectancy at birth, total (years)'
            ),
            dcc.RadioItems(
                id='crossfilter-yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(
                id='crossfilter-indicator-scatter',
                hoverData={'points': [{'customdata': 'Japan'}]}
            )
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
        html.Div([
            dcc.Graph(id='x-time-series'),
            dcc.Graph(id='y-time-series'),
        ], style={'display': 'inline-block', 'width': '49%'}),

        html.Div(dcc.Slider(
            id='crossfilter-year--slider',
            min=test_df['Year'].min(),
            max=test_df['Year'].max(),
            value=test_df['Year'].max(),
            marks={str(year): str(year) for year in test_df['Year'].unique()}
        ), style={'width': '49%', 'padding': '0px 20px 20px 20px'})
        ],
        style={'display': is_test_tab_showing(tab)})

@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
    dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
    dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
    dash.dependencies.Input('crossfilter-yaxis-type', 'value'),
    dash.dependencies.Input('crossfilter-year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                xaxis_type, yaxis_type,
                year_value):
    dff = test_df[test_df['Year'] == year_value]

    return {
        'data': [go.Scatter(
            x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
            y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
            text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
        }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }

def create_time_series(dff, axis_type, title):
    return {
        'data': [go.Scatter(
            x=dff['Year'],
            y=dff['Value'],
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear'},
            'xaxis': {'showgrid': False}
        }
    }
@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
    dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
    dash.dependencies.Input('crossfilter-xaxis-type', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata']
    dff = test_df[test_df['Country Name'] == country_name]
    dff = dff[dff['Indicator Name'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)


@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
    dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
    dash.dependencies.Input('crossfilter-yaxis-type', 'value')])
def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
    dff = test_df[test_df['Country Name'] == hoverData['points'][0]['customdata']]
    dff = dff[dff['Indicator Name'] == yaxis_column_name]
    return create_time_series(dff, axis_type, yaxis_column_name)



# run webapp if main
if __name__ == '__main__':
    app.run_server(debug=True, port=4200)
