from datetime import datetime

import pandas as pd

from columns_to_remove import columns_to_remove

COLUMNS_TO_INCLUDE_2016 = [
    'Born',
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


def format_columns_2016(df):
    # TODO: Seasons, PAX
    df = df.rename(columns={'Born': 'Age'})
    df['PTS/GP'] = df['PTS'] / df['GP']
    return df


def born_to_age(yyy_mm_dd):
    born_year = datetime.strptime(yyy_mm_dd, '%Y-%m-%d').strftime('%Y')
    return 2016 - int(born_year)


def pre_process_2016(path):
    df = pd.read_csv(path, header=2, usecols=COLUMNS_TO_INCLUDE_2016, converters={'Born': born_to_age})
    df = format_columns_2016(df)
    return df


def offenders(pre_processed_data):
    df = pre_processed_data
    pts_forward = df[(df['Position'] != 'D') & (df['GP'] >= 60)]
    return pts_forward


def write_to_csv(df):
    df.to_csv('../data/preprocessed.csv')
