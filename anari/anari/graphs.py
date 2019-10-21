import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from scipy import stats
import textual_view as tv
from math import log10, floor


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
                'title': 'Points distribution of players with Cap Hit >= $4M',
                'width': 400,
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
        sizeref = 4.*max(size)/(25.**2)
        text = df_by_position.apply(lambda x: tv.name_salary(x['H-Ref Name'], x['Cap Hit']), axis=1)

        traces.append(go.Scatter(
            x=df_by_position['TOI/GP'],
            y=df_by_position['PTS'],
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
                title='Ice time and points (Cap Hit >= $4M)',
            )
        }
    )


def update_overview_team_graphs(df, y_value, agg_method):
    traces = []

    for i in df.Playoffs.unique():
        traces.append(go.Scatter(
            x=df[df['Playoffs'] == i]['Points'],
            y=df[df['Playoffs'] == i][y_value],
            text=df[df['Playoffs'] == i]['Team Name'],
            customdata=df[df['Playoffs'] == i]['Team'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name='Made the playoffs' if i else 'Did not make the playoffs'
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={
                'title': 'Team points',
                'type': 'linear',
            },
            yaxis={
                'title': '{0} ({1})'.format(y_value, agg_method),
                'type': 'linear',
            },
            legend={'x': 0, 'y': 1},
            hovermode='closest',
        )
    }


def update_detailed_team_graphs(df, x_value, y_value, title):
    traces = []
    for i in df.Position.unique():
        traces.append(go.Scatter(
            x=df[df['Position'] == i][x_value],
            y=df[df['Position'] == i][y_value],
            text=df[df['Position'] == i]['Last Name'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=next((d.get("label") for d in tv.position_label_values if d.get('value') == i), 'Label not found')
        ))

    return dcc.Graph(
        figure={
            'data': traces,
            'layout': go.Layout(
                xaxis={
                    'title': x_value,
                    'type': 'linear'
                },
                yaxis={
                    'title': y_value,
                    'type': 'linear'
                },
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                title=title
            )
        }
    )


def cap_hit_distribution(df, team_name):
    trace = go.Histogram(
        x=df['Cap Hit'],
    )

    return (
        dcc.Graph(
            figure={
                'data': [trace],
                'layout': {
                    'title': 'Cap Hit distribution: {0}'.format(team_name),
                },
            }
        )
    )


def scatter_matrix(df):
    index_vals = df['Position'].astype('category').cat.codes
    df = df.drop(['NHLid', 'Position'], axis=1)
    dimensions = [dict(label=column, values=df[column]) for column in df.columns]

    trace = go.Splom(
        dimensions=dimensions,
        diagonal_visible=False,
        marker=dict(
            color=index_vals,
            showscale=False,    # colors encode categorical variables
            line_color='white',
            line_width=0.5
        )
    )

    return (
        dcc.Graph(
            figure={
                'data': [trace],
                'layout': go.Layout(
                    dragmode='select',
                    width=1200,
                    height=1200,
                    title='Correlation of different recorded statistics.'
                )
            }
        )
    )


def regression_scatter(lr_data, category):

    trace0 = go.Scatter(
        x=lr_data['y_test'],
        y=lr_data['y_pred'].round(0),
        name=category,
        mode='markers',
    )

    slope, intercept, r_value, p_value, std_err = stats.linregress(lr_data['y_test'], lr_data['y_pred'])

    trace1 = go.Scatter(
        x=lr_data['y_test'],
        y=intercept + slope*lr_data['y_test'],
        mode='lines',
    )

    data = [trace0, trace1]

    width = 600
    height = 600
    max_value = max(lr_data['y_pred'].max(), lr_data['y_test'].max())
    dtick = round(max_value, -int(floor(log10(abs(max_value))))) / 10
    layout = go.Layout(
        showlegend=False,
        title='Regression scatter performance on ' + category,
        width=width,
        height=height,
        xaxis = go.layout.XAxis(
            tickmode = 'linear',
            dtick = dtick,
            title='Actual value'
        ),
        yaxis = go.layout.YAxis(
            tickmode = 'linear',
            dtick = dtick,
            title='Predicted value'
        )
    )

    return (
        dcc.Graph(
            figure={
                'data': data,
                'layout': layout,
            }
        )
    )


def forecast_regression_scatter(df):
    traces = []
    for i in df.Position.unique():
        df_by_position = df[df['Position'] == i]
        traces.append(go.Scatter(
            #text = df_by_position.apply(lambda x: tv.name_salary(x['H-Ref Name'], x['Cap Hit']), axis=1),
            x=df[df['Position'] == i]['forecast_PTS'],
            y=df[df['Position'] == i]['Cap Hit'],
            text=(df_by_position.apply(lambda x: tv.name_salary(x['H-Ref Name'], x['Cap Hit']), axis=1) + ', ' + df_by_position.apply(lambda x: str(int(x['forecast_PTS'])), axis=1) + 'PTS'),
            mode='markers',
            opacity=0.7,
            marker={
                'size': 10,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=next((d.get("label") for d in tv.position_label_values if d.get('value') == i), 'Label not found')
        ))
    layout = go.Layout(
        title='Expected points in next season and current salary',
        hovermode='closest',
        width=1200,
        height=500,
        xaxis={'title': 'Estimated points'},
        yaxis={'title': 'Current Cap Hit'}
    )

    return (
        dcc.Graph(
            figure={
                'data': traces,
                'layout': layout,
            }
        )
    )
