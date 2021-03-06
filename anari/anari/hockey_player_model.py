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


def offenders(pre_processed_data):
    df = pre_processed_data
    pts_forward = df[(df['Position'] != 'D') & (df['GP'] >= 60)]
    return pts_forward


def write_to_csv(df, name, has_index=False):
    df.to_csv('../data/{0}'.format(name), index=has_index)
