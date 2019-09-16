import pandas as pd

def pre_process(path): 
    df = pd.read_csv(path, header=2)
    df['IPP%'] = df['IPP%'].str.strip('%').astype(float)
    return df

def offenders(pre_processed_data):
    df = pre_processed_data
    pts_forward = df[(df['Position'] != 'D') & (df['GP'] >= 60)]
    return pts_forward

