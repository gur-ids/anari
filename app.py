# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
 
# df = pd.read_csv('./nhl_2017-2018.csv', header=[0, 1, 2])
df = pd.read_csv('./nhl_2017-2018.csv', header=2)

pts = df.loc[df['PTS'] >= 100]
 
asd = pts.head(10)
print(asd['Last Name'])

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
    generate_table(asd)
])

if __name__ == '__main__':
    app.run_server(debug=True, port=4200)
