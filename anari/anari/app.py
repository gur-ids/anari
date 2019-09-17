import dash
import dash_html_components as html
import hockey_player_model as hpm
import hockey_player_fun as hpf
import graphs as g
import view as v

# initial pre-processing
df = hpm.pre_process('../data/nhl_2017-2018.csv')

# handling pre-processed data
offenders = hpm.offenders(df)
top_players = hpf.filter_players_by_points(df, 50)

# produced view
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H4(children='NHL meik mani'),
    html.P('Here is a table of the top scorers'),
    html.P(children=v.top_players_gp_mean_text(top_players)),
    g.box_plot_by_points(offenders),
    g.scatter_plot_players('test_id', top_players)
])

# run webapp if main
if __name__ == '__main__':
    app.run_server(debug=True, port=4200)
