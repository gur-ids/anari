import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


def box_plot_by_points(df):
    trace = go.Box(
        y=df['PTS'],
        name='Forwards',
    )

    return dcc.Graph(
        figure={
            'data': [trace],
            'layout': {
                'title': 'Points distribution of forwards with >= 60 games played',
            }
        }
    )


def scatter_plot_toi_pts(plot_id, df):
    traces = []

    for i in df.Position.unique():
        # Marker size
        # https://plot.ly/python/bubble-charts/#scaling-the-size-of-bubble-charts
        df_by_position = df[df['Position'] == i]
        size = df_by_position['Cap Hit']
        sizeref = 2.*max(size)/(20.**2)

        text = df[df['Position'] == i]['H-Ref Name']

        traces.append(go.Scatter(
            x=df[df['Position'] == i]['TOI/GP'],
            y=df[df['Position'] == i]['PTS'],
            text=text,
            mode='markers',
            opacity=0.7,
            marker={
                'size': size,
                'sizeref': sizeref,
                'sizemode': 'area',
                'sizemin': 4,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))

    return dcc.Graph(
        id=plot_id,
        figure={
            'data': traces,
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Time on ice per game'},
                yaxis={'title': 'Points scored'},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                title='Ice time and points (>= 50)',
            )
        }
    )


def cap_hit_distribution(df):
    trace = go.Histogram(
        x=df['Cap Hit'],
    )

    return (
        dcc.Graph(
            figure={
                'data': [trace],
                'layout': {
                    'title': 'Cap Hit distribution',
                },
            }
        )
    )


def scatter_plot_teams(plot_id, teams):
    return dcc.Graph(
        id=plot_id,
        figure={
            'data': [
                go.Scatter(
                    x=teams[teams['Team'] == i]['Rank'],
                    y=teams[teams['Team'] == i]['Team'],
                    text=teams[teams['Team'] == i]['Team'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in teams.Team.unique()
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'avg pts'},
                yaxis={'title': 'team name'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
