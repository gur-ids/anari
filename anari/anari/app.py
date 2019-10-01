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
forwards = hpm.forwards(df)
top_players = hpf.filter_players_by_points(df, 50)
team_df_first_in = tm.get_team(df, 'NSH')
team_df_last_in = tm.get_team(df, 'COL')
team_df_first_out = tm.get_team(df, 'STL')

top_three_df = hpf.top_paid_players(team_df_last_in)
team_cap_hit = tm.get_team_total_cap_hit(team_df_last_in)
top_three_cap_hit = hpf.cap_hit_share(top_three_df, team_cap_hit)
team_points = tm.get_team_total_points(team_df_last_in)
top_three_points = hpf.points_share(top_three_df, team_points)

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
            g.box_plot_by_points(forwards),
            g.scatter_plot_teams('test_id2', teams),
            g.scatter_plot_players('test_id', top_players)
        ])
    elif tab == 'great-stat-tab':

        team_trace_first_in = go.Histogram(
                x=team_df_first_in['Cap Hit'],
        )

        team_trace_first_out = go.Histogram(
                x=team_df_first_out['Cap Hit'],
        )

        return html.Div([
            dcc.Markdown(notes),
            html.H1(children='Western Conference'),

            # TODO: use functions
            html.H2(children='Nashville Predators'),
            dcc.Graph(
                figure={
                    'data': [team_trace_first_in],
                    'layout': {
                        'title': 'Cap Hit distribution',
                    },
                }
            ),
            # TODO: top players

            html.H2(children='Colorado Avalanche'),
            g.cap_hit_distribution(team_df_last_in),
            g.generate_table(top_three_df),
            html.Div([
                html.P(v.top_three_cap_hit_text(top_three_cap_hit, team_cap_hit)),
                html.P(v.top_three_points_text(top_three_points, team_points)),
            ]),

            # TODO: use functions
            html.H2(children='St. Louis Blues'),
            dcc.Graph(
                figure={
                    'data': [team_trace_first_out],
                    'layout': {
                        'title': 'Cap Hit distribution',
                    },
                }
            ),
            # TODO: top players
        ])


# run webapp if main
if __name__ == '__main__':
    app.run_server(debug=True, port=4200)
