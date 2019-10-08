from datetime import datetime

import pandas as pd

from columns_to_remove import columns_to_remove

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


def remove_columns(df):
    return df.drop(columns=columns_to_remove)


def format_columns(df):
    # TODO: Consider int
    df['Salary'] = df['Salary'].replace(r'[\$,]', '', regex=True).astype(float)
    df['Cap Hit'] = df['Cap Hit'].replace(r'[\$,]', '', regex=True).astype(float)
    df['IPP%'] = df['IPP%'].str.strip('%').astype(float)
    df['Team'] = df['Team'].str[-3:]
    df['Position'] = df['Position'].apply(lambda position: position.split('/')[-1])
    return df


def pre_process(path):
    # NOTE: Duplicate column names have suffixes. another way would be:
    # df = pd.read_csv(path, header=[0, 1, 2]
    df = pd.read_csv(path, header=2)
    df = remove_columns(df)
    df = format_columns(df)
    df.sort_values(by=['Team'], inplace=True)
    return df


def fill_seasons(x, df_2017):
    # Impute Season: 1 if player did not play following season
    seasons_2017 = df_2017.loc[df_2017['NHLid'] == x, 'Seasons']
    return seasons_2017.iloc[0] - 1 if not seasons_2017.empty else 1


def format_columns_2016(df, df_2017):
    df = df.rename(columns={'Born': 'Age'})
    df['PTS/GP'] = df['PTS'] / df['GP']
    df['Seasons'] = df['NHLid'].apply(fill_seasons, args=(df_2017,))
    return df


def born_to_age(yyy_mm_dd):
    born_year = datetime.strptime(yyy_mm_dd, '%Y-%m-%d').strftime('%Y')
    return 2016 - int(born_year)


def parse_position(position):
    if 'C' in position:
        position = 'C'
    elif 'D' in position:
        position = 'D'
    return position


def pre_process_2016(path, df_2017):
    df = pd.read_csv(
        path,
        header=2,
        usecols=COLUMNS_TO_INCLUDE_2016,
        converters={'Born': born_to_age, 'Position': parse_position}
    )
    df = format_columns_2016(df, df_2017)
    return df


def offenders(pre_processed_data):
    df = pre_processed_data
    pts_forward = df[(df['Position'] != 'D') & (df['GP'] >= 60)]
    return pts_forward


def write_to_csv(df):
    df.to_csv('../data/preprocessed.csv')
