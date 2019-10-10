from datetime import datetime

import pandas as pd

# TODO For data scheisse part in linear regression:
#
#  - filter 2017-2018 columns: df.filter(items=COLUMNS_TO_INCLUDE_2016)
#  - fillna(?)
#  - remove NHLid
#  - perhaps add 2015-2016 season

COLUMNS_TO_INCLUDE_2017 = [
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
    'Position',
    'GP',
    'G',
    'A',
    'PTS',
    '+/-',
    'TOI/GP',
    'IPP%',
]

NA_VALUES_2016 = ['#DIV/0!']


def parse_born(yyy_mm_dd):
    born_year = datetime.strptime(yyy_mm_dd, '%Y-%m-%d').strftime('%Y')
    return 2016 - int(born_year)


def parse_position(position):
    if 'C' in position:
        position = 'C'
    elif 'D' in position:
        position = 'D'
    return position


def parse_ipp(ipp):
    return float(ipp.strip('%'))


def fill_seasons(x, df_2017):
    # FIXME: use mean
    # Impute Season: 1 if player did not play following season
    seasons_2017 = df_2017.loc[df_2017['NHLid'] == x, 'Seasons']
    return seasons_2017.iloc[0] - 1 if not seasons_2017.empty else 1


def format_columns_2016(df, df_2017):
    df = df.rename(columns={'Born': 'Age'})
    df['PTS/GP'] = df['PTS'] / df['GP']
    df['Seasons'] = df['NHLid'].apply(fill_seasons, args=(df_2017,))
    return df


def pre_process_linear():
    df_2017 = pre_process_2017()
    df_2016 = pre_process_linear_2016(df_2017)


def pre_process_2017():
    path = '../data/nhl_2017-2018.csv'

    df = pd.read_csv(
        path,
        header=2,
        usecols=COLUMNS_TO_INCLUDE_2017,
        converters={'Position': parse_position, 'IPP%': parse_ipp},
    )

    return df


def pre_process_linear_2016(df_2017):
    path = '../data/NHL_2016-17.csv'

    df = pd.read_csv(
        path,
        header=2,
        usecols=COLUMNS_TO_INCLUDE_2016,
        na_values=NA_VALUES_2016,
        converters={'Born': parse_born, 'Position': parse_position, 'IPP%': parse_ipp},
        # Run na_values first, then converters
        # https://github.com/pandas-dev/pandas/issues/13302
        engine='python',
    )

    df = format_columns_2016(df, df_2017)

    return df
