import pandas as pd


def remove_columns(df):
    # TODO
    return df


def format_columns(df):
    df['Salary'] = df['Salary'].replace(r'[\$,]', '', regex=True).astype(float)
    df['IPP%'] = df['IPP%'].str.strip('%').astype(float)
    return df


def pre_process(path):
    # NOTE: Duplicate column names have suffixes. another way would be:
    # df = pd.read_csv(path, header=[0, 1, 2]
    df = pd.read_csv(path, header=2)
    df = remove_columns(df)
    df = format_columns(df)
    return df


def offenders(pre_processed_data):
    df = pre_processed_data
    pts_forward = df[(df['Position'] != 'D') & (df['GP'] >= 60)]
    return pts_forward
