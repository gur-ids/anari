import pandas as pd
from columns_to_remove import columns_to_remove


def remove_columns(df):
    return df.drop(columns=columns_to_remove)


def format_columns(df):
    # TODO: Consider int
    df['Salary'] = df['Salary'].replace(r'[\$,]', '', regex=True).astype(float)
    df['Cap Hit'] = df['Cap Hit'].replace(r'[\$,]', '', regex=True).astype(float)
    df['IPP%'] = df['IPP%'].str.strip('%').astype(float)
    df['Team'] = df['Team'].str[-3:]
    df['Position'] = df['Position'].apply(lambda x: 'C' if 'C' in x else x)
    return df


def pre_process(path):
    # NOTE: Duplicate column names have suffixes. another way would be:
    # df = pd.read_csv(path, header=[0, 1, 2]
    df = pd.read_csv(path, header=2)
    df = remove_columns(df)
    df = format_columns(df)
    df.sort_values(by=['Team'], inplace=True)
    return df


def write_to_csv(df):
    df.to_csv('../data/preprocessed.csv')
