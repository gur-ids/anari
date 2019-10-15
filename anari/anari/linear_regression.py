import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

NA_VALUES = ['#DIV/0!']

lm = LinearRegression()

COLUMNS_TO_INCLUDE = [
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

COLUMNS_TO_INCLUDE_2016 = [
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
        player_id = float('nan')
    elif found_players == 1:
        player_id = players_df['NHLid'].iloc[0]
    else:
        # TODO: Do something for the duplicates if necessary
        pass

    return player_id


def format_columns_2015(df, df_2016):
    df = df.rename(columns={'Pos': 'Position', 'TOI/G': 'TOI/GP', 'IPP': 'IPP%'})
    df['NHLid'] = df.apply(lambda x: fill_id(x['First Name'], x['Last Name'], df_2016), axis=1)

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


def pre_process_2016():
    path = '../data/NHL_2016-17.csv'

    df = pd.read_csv(
        path,
        header=2,
        usecols=COLUMNS_TO_INCLUDE_2016,
        na_values=NA_VALUES,
        converters={
            'Position': lambda x: parse_position(x, True),
            'IPP%': parse_ipp
        },
        # Run na_values first, then converters
        # https://github.com/pandas-dev/pandas/issues/13302
        engine='python',
    )

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
    avg_ipp = df['IPP%'].mean()
    df['IPP%'] = df['IPP%'].fillna(avg_ipp)
    return df


def remove_missing(df):
    return df.dropna(subset=['NHLid'])


def transform_categorical(df):
    df['Position'] = df['Position'].astype('category').cat.codes
    return df


def filter_columns(df):
    df = df.filter(items=COLUMNS_TO_INCLUDE)
    return df


def combine_data(left, right, latest):
    combined_df = pd.merge(
        left['df'],
        right['df'],
        on='NHLid',
        how='inner',
        suffixes=(left['suffix'], right['suffix']),
    )

    df = pd.DataFrame()
    df['2017_PTS'] = latest['PTS']
    df['NHLid'] = latest['NHLid']

    df = combined_df.merge(df, how='inner', on=['NHLid'])

    return df


def pre_process_linear():
    df_2017 = pre_process_2017()
    df_2016 = pre_process_2016()
    df_2015 = pre_process_2015(df_2016)

    df_2017 = filter_columns(df_2017)
    df_2016 = filter_columns(df_2016)
    df_2015 = filter_columns(df_2015)

    df_2017 = impute_columns(df_2017)
    df_2016 = impute_columns(df_2016)
    df_2015 = impute_columns(df_2015)

    df_2017 = remove_missing(df_2017)
    df_2016 = remove_missing(df_2016)
    df_2015 = remove_missing(df_2015)

    df_2017 = transform_categorical(df_2017)
    df_2016 = transform_categorical(df_2016)
    df_2015 = transform_categorical(df_2015)

    training_df = combine_data(
        {'df': df_2015, 'suffix': '_previous'},
        {'df': df_2016, 'suffix': '_next'},
        df_2017
    )

    # Finally drop NHLid
    training_df = training_df.drop(['NHLid'], axis=1)

    forecast_df = combine_data(
        {'df': df_2016, 'suffix': '_previous'},
        {'df': df_2017, 'suffix': '_next'},
        df_2017
    )
    forecast_df = forecast_df.drop(['2017_PTS'], axis=1)

    return training_df, forecast_df, df_2017


def do_linear(df):
    y = df['2017_PTS']
    X = df.drop(['2017_PTS'], axis=1)
    # X = X.drop(['G', 'A'], axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y)
    lm.fit(X_train, y_train)
    y_pred = lm.predict(X_test)
    coeff_df = pd.DataFrame(lm.coef_, X.columns, columns=['Coefficient'])
    print(coeff_df)
    errors = abs(y_pred - y_test)   # Print out the mean absolute error (mae)
    # print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')
    # Calculate mean absolute percentage error (MAPE)
    mape = 100 * (errors / y_test)  # Calculate and display accuracy
    accuracy = 100 - np.mean(mape)

    return X_train, X_test, y_train, y_test, y_pred

def forecast(df):
    return lm.predict(df.drop(['NHLid'], axis=1))

def get_forecast_visual_data(df_full, forecast_df):
    forecast_results = forecast(forecast_df)

    cap_hit_df = pd.DataFrame()
    cap_hit_df['Cap Hit'] = df_full['Cap Hit']
    cap_hit_df['H-Ref Name'] = df_full['H-Ref Name']
    cap_hit_df['NHLid'] = df_full['NHLid']
    cap_hit_df['Position'] = df_full['Position']

    forecast_df = forecast_df.merge(cap_hit_df, left_on='NHLid', right_on='NHLid', how='inner')
    forecast_df['forecast_PTS'] = forecast_results
    return forecast_df