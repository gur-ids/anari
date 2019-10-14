import numpy as np
import pandas as pd
# randomforest
from sklearn.ensemble import \
    RandomForestRegressor  # Instantiate model with 1000 decision trees
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

rf = RandomForestRegressor(n_estimators=1000, random_state=42)

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
    # df = df.drop(['NHLid'], axis=1)
    return df


def combine_data(left, right):
    result = pd.merge(left, right, on='NHLid')
    return result


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

    previous_seasons_df = combine_data(df_2015, df_2016)

    linear_df = pd.DataFrame()
    linear_df['2017_PTS'] = df_2017['PTS']
    linear_df['NHLid'] = df_2017['NHLid']

    linear_df = previous_seasons_df.merge(linear_df, how='inner', on=['NHLid'])
    linear_df = linear_df.drop(['NHLid'], axis=1)

    return linear_df, df_2017


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


def do_forest(df):
    y = df['2017_PTS']
    X = df.drop(['2017_PTS'], axis=1)
    # X = X.drop(['G', 'A'], axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y)
    rf.fit(X_train, y_train)
    # Use the forest's predict method on the test data
    y_pred = rf.predict(X_test)     # Calculate the absolute errors
    errors = abs(y_pred - y_test)   # Print out the mean absolute error (mae)
    print('forest')
    print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')
    # Calculate mean absolute percentage error (MAPE)
    mape = 100 * (errors / y_test)  # Calculate and display accuracy
    accuracy = 100 - np.mean(mape)
    # print('Accuracy:', round(accuracy, 2), '%.')
    return X_train, X_test, y_train, y_test, y_pred


def predict_player(prediction_target):
    return lm.predict(prediction_target)
