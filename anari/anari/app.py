import dash
import dash_html_components as html
import plotly.graph_objs as go
import hockey_player_model as hpm
import hockey_player_fun as hpf
import graphs as g
import view as v
import team_model as tm
import dash_core_components as dcc
from dash.dependencies import Input, Output
from notes import notes

# initial pre-processing
df = hpm.pre_process('../data/nhl_2017-2018.csv')
teams = tm.pre_process('../data/team_stats_2017-2018.csv')

# handling pre-processed data
offenders = hpm.offenders(df)
top_players = hpf.filter_players_by_points(df, 50)
team_df = tm.get_team(df, 'NSH')

# produced view
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='NHL meik mani'),
    dcc.Tabs(id="tabs", value='basic-info-tab', children=[
        dcc.Tab(label='Basic Info', value='basic-info-tab'),
        dcc.Tab(label='Make statistics great again', value='great-stat-tab'),
    ]),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'basic-info-tab':
        return html.Div(children=[
            html.P(children=v.top_players_gp_mean_text(top_players)),
            g.box_plot_by_points(offenders),
            g.scatter_plot_teams('test_id2', teams),
            g.scatter_plot_players('test_id', top_players)
        ])
    elif tab == 'great-stat-tab':

        team_trace = go.Histogram(
                x=team_df['Cap Hit'],
        )

        return html.Div([
            dcc.Markdown(notes),
            dcc.Graph(
                figure={
                    'data': [team_trace],
                }
            )
        ])


# run webapp if main
if __name__ == '__main__':
    app.run_server(debug=True, port=4200)
