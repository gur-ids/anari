# -*- coding: utf-8 -*-
import dash
# import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_core_components as dcc
import pandas as pd

# df = pd.read_csv('./nhl_2017-2018.csv', header=[0, 1, 2])
df = pd.read_csv('./nhl_2017-2018.csv', header=2)

# Format Salary
df['Salary'] = df['Salary'].replace(r'[\$,]', '', regex=True).astype(float)

# Format Individual Points Percentage
df['IPP%'] = df['IPP%'].str.strip('%').astype(float)

pts = df.loc[df['PTS'] >= 50]

pts_forward = df[(df['Position'] != 'D') & (df['GP'] >= 60)]

ipp = pts.loc[df['IPP%'] > 80]
top_ipp_str = 'IPP% over 80: {0}'.format(', '.join(ipp['Last Name'].values))

gp_mean = pts['GP'].mean()
gp_mean_str = 'Average games played by top scorers: {0} games'.format(gp_mean)

pts = pts.sort_values(by=['PTS'], ascending=False)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


app.layout = html.Div(children=[
    html.H4(children='NHL meik mani'),
    html.P('Here is a table of the top scorers'),
    html.P(top_ipp_str),
    html.P(children=gp_mean_str),
    generate_table(pts),
    dcc.Graph(figure={'data': [go.Box(y=pts_forward['PTS'])]}),
    dcc.Graph(
        id='test',
        figure={
            'data': [
                go.Scatter(
                    x=pts[pts['Position'] == i]['GP'],
                    y=pts[pts['Position'] == i]['PTS'],
                    text=pts[pts['Position'] == i]['Last Name'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in pts.Position.unique()
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Games played'},
                yaxis={'title': 'Points scored'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True, port=4200)
