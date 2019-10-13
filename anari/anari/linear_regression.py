import uuid
from datetime import datetime

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

NA_VALUES = ['#DIV/0!']

COLUMNS_TO_INCLUDE = [
    'Age',
    'Seasons',
    'NHLid',
    'Position',
    'GP',
    'G',
    'A',
    'PTS',
    'PTS/GP',
    '+/-',
    'TOI/GP',
    'IPP%',
]

COLUMNS_TO_INCLUDE_2016 = [
    'Born',
    'NHLid',
    'Last Name',
    'First Name',
    'Position',
    'GP',
    'G',
    'A',
    'PTS',
    '+/-',
    'TOI/GP',
    'IPP%',
]

COLUMNS_TO_INCLUDE_2015 = [
    'Age',
    'First Name',
    'Last Name',
    'Pos',
    'GP',
    'G',
    'A',
    'PTS',
    '+/-',
    'TOI/G',
    'IPP',
]


def parse_born(yyy_mm_dd, year_then):
    born_year = datetime.strptime(yyy_mm_dd, '%Y-%m-%d').strftime('%Y')
    return year_then - int(born_year)


def parse_position(position, keep_first=False):
    # "NHL source listed first, followed by those listed by any other source."
    return position.split('/')[0 if keep_first else -1]


def parse_ipp(ipp):
    return float(ipp.strip('%'))


def fill_id(first_name, last_name, df_next_year):
    # NOTE: The function could find id data from all the following seasons
    players_df = df_next_year.loc[lambda x: (x['First Name'] == first_name) & (x['Last Name'] == last_name)]
    found_players = len(players_df.index)

    if found_players == 0:
        # Assign dummy id
        player_id = uuid.uuid4()
    elif found_players == 1:
        player_id = players_df['NHLid'].iloc[0]
    else:
        # TODO: Do something for the duplicates if necessary
        pass

    return player_id


def fill_seasons(x, df_next_year):
    # NOTE: The function could find season data from all the following seasons
    # NaN if player does not have data available
    seasons_next_year = df_next_year.loc[df_next_year['NHLid'] == x, 'Seasons']
    return seasons_next_year.iloc[0] - 1 if not seasons_next_year.empty else float('nan')


def format_columns_2016(df, df_2017):
    df = df.rename(columns={'Born': 'Age'})
    df['PTS/GP'] = df['PTS'] / df['GP']
    df['Seasons'] = df['NHLid'].apply(fill_seasons, args=(df_2017,))

    return df


def format_columns_2015(df, df_2016):
    df = df.rename(columns={'Pos': 'Position', 'TOI/G': 'TOI/GP', 'IPP': 'IPP%'})
    df['PTS/GP'] = df['PTS'] / df['GP']
    df['NHLid'] = df.apply(lambda x: fill_id(x['First Name'], x['Last Name'], df_2016), axis=1)
    df['Seasons'] = df['NHLid'].apply(fill_seasons, args=(df_2016,))

    return df


def pre_process_2017():
    path = '../data/nhl_2017-2018.csv'

    df = pd.read_csv(
        path,
        header=2,
        usecols=COLUMNS_TO_INCLUDE,
        converters={'Position': parse_position, 'IPP%': parse_ipp},
    )

    return df


def pre_process_2016(df_2017):
    path = '../data/NHL_2016-17.csv'

    df = pd.read_csv(
        path,
        header=2,
        usecols=COLUMNS_TO_INCLUDE_2016,
        na_values=NA_VALUES,
        converters={
            'Born': lambda x: parse_born(x, 2016),
            'Position': lambda x: parse_position(x, True),
            'IPP%': parse_ipp
        },
        # Run na_values first, then converters
        # https://github.com/pandas-dev/pandas/issues/13302
        engine='python',
    )

    df = format_columns_2016(df, df_2017)

    return df


def pre_process_2015(df_2016):
    path = '../data/NHL 2015-16.csv'

    df = pd.read_csv(
        path,
        usecols=COLUMNS_TO_INCLUDE_2015,
        na_values=NA_VALUES,
        converters={
            'Pos': lambda x: parse_position(x, True),
            'IPP': parse_ipp
        },
        # Run na_values first, then converters
        # https://github.com/pandas-dev/pandas/issues/13302
        engine='python',
    )

    df = format_columns_2015(df, df_2016)

    return df


def impute_columns(df):
    avg_seasons = df['Seasons'].mean()
    df['Seasons'] = df['Seasons'].fillna(avg_seasons)
    avg_ipp = df['IPP%'].mean()
    df['IPP%'] = df['IPP%'].fillna(avg_ipp)
    return df


def transform_categorical(df):
    df['Position'] = df['Position'].astype('category').cat.codes
    return df


def filter_columns(df):
    df = df.filter(items=COLUMNS_TO_INCLUDE)
    df = df.drop(['NHLid'], axis=1)
    return df


def pre_process_linear():
    df_2017 = pre_process_2017()
    df_2016 = pre_process_2016(df_2017)
    df_2015 = pre_process_2015(df_2016)

    df_2017 = filter_columns(df_2017)
    df_2016 = filter_columns(df_2016)
    df_2015 = filter_columns(df_2015)

    linear_df = pd.concat([df_2017, df_2016, df_2015], sort=True)
    linear_df = impute_columns(linear_df)
    linear_df = transform_categorical(linear_df)

    return linear_df


def do_linear(df):
    y = df['PTS']
    X = df.drop(['PTS'], axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y)
    lm = LinearRegression()
    lm.fit(X_train, y_train)
    y_pred = lm.predict(X_test)

    return X_train, X_test, y_train, y_test, y_pred
