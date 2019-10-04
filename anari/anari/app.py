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
teams_df = tm.pre_process('../data/team_stats_2017-2018.csv')

# handling pre-processed data
forwards_df = hpf.forwards_by_gp(df, 60)
top_players_df = hpf.filter_players_by_points(df, 50)

w_top_df = tm.get_team(df, 'NSH')
w_bottom_df = tm.get_team(df, 'COL')
w_out_df = tm.get_team(df, 'STL')

w_top_name = tm.get_team_full_name(teams_df, 'NSH')
w_bottom_name = tm.get_team_full_name(teams_df, 'COL')
w_out_name = tm.get_team_full_name(teams_df, 'STL')

max_cap_hit = tm.get_max_cap_hit()

w_bottom_top_paid_df = hpf.top_paid_players(w_bottom_df)
w_bottom_cap_hit = tm.get_team_total_cap_hit(w_bottom_df)
w_bottom_top_paid_cap_hit = hpf.cap_hit_share(w_bottom_top_paid_df, w_bottom_cap_hit)
w_bottom_top_paid_cap_hit_total = hpf.cap_hit_share(w_bottom_top_paid_df, max_cap_hit)
w_bottom_points = tm.get_team_total_points(w_bottom_df)
w_bottom_top_paid_points = hpf.points_share(w_bottom_top_paid_df, w_bottom_points)

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
            g.box_plot_by_points(forwards_df),
            g.scatter_plot_teams('test_id2', teams_df),
            g.scatter_plot_toi_pts('toi_pts', top_players_df)
        ])
    elif tab == 'great-stat-tab':

        team_trace_w_top = go.Histogram(
                x=w_top_df['Cap Hit'],
        )

        team_trace_out = go.Histogram(
                x=w_out_df['Cap Hit'],
        )

        return html.Div([
            dcc.Markdown(notes),
            html.H1(children='Western Conference'),

            # TODO: use functions
            html.H2(children=w_top_name),
            dcc.Graph(
                figure={
                    'data': [team_trace_w_top],
                    'layout': {
                        'title': 'Cap Hit distribution',
                    },
                }
            ),
            # TODO: top players

            html.H2(children=w_bottom_name),
            g.cap_hit_distribution(w_bottom_df),
            g.generate_table(w_bottom_top_paid_df),
            html.Div([
                html.P(v.top_paid_cap_hit_text(w_bottom_top_paid_cap_hit, w_bottom_cap_hit)),
                html.P(v.top_paid_max_cap_hit_text(w_bottom_top_paid_cap_hit_total, max_cap_hit)),
                html.P(v.top_paid_points_text(w_bottom_top_paid_points, w_bottom_points)),
            ]),

            # TODO: use functions
            html.H2(children=w_out_name),
            dcc.Graph(
                figure={
                    'data': [team_trace_out],
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
