import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

NA_VALUES = ["#DIV/0!"]

lm = LinearRegression()
models = dict(
    {
        "PTS": LinearRegression(),
        "+/-": LinearRegression(),
        "A": LinearRegression(),
        "G": LinearRegression(),
        "TOI": LinearRegression(),
    }
)

COLUMNS_TO_INCLUDE = [
    "NHLid",
    "Position",
    "GP",
    "G",
    "A",
    "PTS",
    "+/-",
    "TOI",
    "IPP%",
    "Shots",
    "Shots_missed",
    "Shots_cbar",
    "Shots_post",
    "Team",
]

COLUMNS_TO_INCLUDE_2017 = [
    "NHLid",
    "Position",
    "Team",
    "GP",
    "G",
    "A",
    "PTS",
    "+/-",
    "TOI",
    "IPP%",
    "CBar ",  # Notice the whitespace
    "Post",
    "S.Bkhd",
    "S.Dflct",
    "Over",
    "S.Slap",
    "S.Snap",
    "S.Tip",
    "S.Wrap",
    "S.Wrst",
    "Wide",
]

COLUMNS_TO_INCLUDE_2016 = [
    "NHLid",
    "Last Name",
    "First Name",
    "Position",
    "Team",
    "GP",
    "G",
    "A",
    "PTS",
    "+/-",
    "TOI",
    "IPP%",
    "CBar ",  # Notice the whitespace
    "Post",
    "Over",
    "S.Bkhd",
    "S.Dflct",
    "S.Slap",
    "S.Snap",
    "S.Tip",
    "S.Wrap",
    "S.Wrst",
    "Wide",
]

COLUMNS_TO_INCLUDE_2015 = [
    "First Name",
    "Last Name",
    "End Team",
    "Pos",
    "GP",
    "G",
    "A",
    "PTS",
    "+/-",
    "TOI",
    "IPP",
    "Crossbar",  # CBar
    "Post",
    "Backhand",  # S.Bkhd
    "Deflected",  # S.Dflct
    "OverNet",  # S.Over
    "Slap",  # S.Slap
    "Snap",  # S.Snap
    "Tipped",  # S.Tip
    "WideOfNet",  # S.Wide
    "Wraparound",  # S.Wrap
    "Wrist",  # S.Wrist
]


def parse_position(position, keep_first=False):
    # "NHL source listed first, followed by those listed by any other source."
    return position.split("/")[0 if keep_first else -1]


def parse_ipp(ipp):
    return float(ipp.strip("%"))


def parse_team(team, rename_team=False, keep_first=False, delimiter=","):
    team_name = team.split(delimiter)[0 if keep_first else -1]
    if rename_team:
        if team_name == "L.A":
            team_name = "LAK"
        elif team_name == "N.J":
            team_name = "NJD"
        elif team_name == "S.J":
            team_name = "SJS"
        elif team_name == "T.B":
            team_name = "TBL"

    return team_name


def fill_id(first_name, last_name, df_next_year):
    # NOTE: The function could find id data from all the following seasons
    players_df = df_next_year.loc[
        lambda x: (x["First Name"] == first_name) & (x["Last Name"] == last_name)
    ]
    found_players = len(players_df.index)

    if found_players == 0:
        player_id = float("nan")
    elif found_players == 1:
        player_id = players_df["NHLid"].iloc[0]
    else:
        # TODO: Do something for the duplicates if necessary
        pass

    return player_id


def sum_columns(df, shots_columns):
    return df[shots_columns].sum(axis=1)


def format_columns_2017(df):
    df["Shots"] = sum_columns(
        df, ["S.Bkhd", "S.Dflct", "S.Slap", "S.Snap", "S.Tip", "S.Wrap", "S.Wrst"]
    )
    df["Shots_missed"] = sum_columns(df, ["Over", "Wide"])
    df = df.rename(
        columns={"CBar ": "Shots_cbar", "Post": "Shots_post"}
    )  # Notice the whitespace
    return df


def format_columns_2016(df):
    df["Shots"] = sum_columns(
        df, ["S.Bkhd", "S.Dflct", "S.Slap", "S.Snap", "S.Tip", "S.Wrap", "S.Wrst"]
    )
    df["Shots_missed"] = sum_columns(df, ["Over", "Wide"])
    df = df.rename(
        columns={"CBar ": "Shots_cbar", "Post": "Shots_post"}
    )  # Notice the whitespace
    return df


def format_columns_2015(df, df_2016):
    df["Shots"] = sum_columns(
        df, ["Backhand", "Deflected", "Slap", "Snap", "Tipped", "Wraparound", "Wrist"]
    )
    df["Shots_missed"] = sum_columns(df, ["OverNet", "WideOfNet"])

    df = df.rename(
        columns={
            "Pos": "Position",
            "IPP": "IPP%",
            "Crossbar": "Shots_cbar",
            "Post": "Shots_post",
            "End Team": "Team",
        }
    )

    df["NHLid"] = df.apply(
        lambda x: fill_id(x["First Name"], x["Last Name"], df_2016), axis=1
    )

    return df


def pre_process_2017():
    path = "../data/nhl_2017-2018.csv"

    df = pd.read_csv(
        path,
        header=2,
        usecols=COLUMNS_TO_INCLUDE_2017,
        converters={"Position": parse_position, "IPP%": parse_ipp, "Team": parse_team},
    )

    df = format_columns_2017(df)

    return df


def pre_process_2016():
    path = "../data/NHL_2016-17.csv"

    df = pd.read_csv(
        path,
        header=2,
        usecols=COLUMNS_TO_INCLUDE_2016,
        na_values=NA_VALUES,
        converters={
            "Position": lambda x: parse_position(x, True),
            "IPP%": parse_ipp,
            "Team": lambda x: parse_team(
                x, keep_first=True, rename_team=True, delimiter="/"
            ),
        },
        # Run na_values first, then converters
        # https://github.com/pandas-dev/pandas/issues/13302
        engine="python",
    )

    df = format_columns_2016(df)

    return df


def pre_process_2015(df_2016):
    path = "../data/NHL 2015-16.csv"

    df = pd.read_csv(
        path,
        usecols=COLUMNS_TO_INCLUDE_2015,
        na_values=NA_VALUES,
        converters={"Pos": lambda x: parse_position(x, True), "IPP": parse_ipp},
        # Run na_values first, then converters
        # https://github.com/pandas-dev/pandas/issues/13302
        engine="python",
    )

    df = format_columns_2015(df, df_2016)

    return df


def impute_columns(df):
    avg_ipp = df["IPP%"].mean()
    df["IPP%"] = df["IPP%"].infer_objects(copy=False).fillna(avg_ipp)
    return df


def remove_missing(df):
    return df.dropna(subset=["NHLid"])


def transform_categorical(df_2017, df_2016, df_2015):
    df_2017["Season"] = 2017
    df_2016["Season"] = 2016
    df_2015["Season"] = 2015

    df = pd.concat([df_2017, df_2016, df_2015])

    df["Position"] = df["Position"].astype("category").cat.codes
    df["Team"] = df["Team"].astype("category").cat.codes

    df_2017_categorized = df.loc[df["Season"] == 2017].drop(["Season"], axis=1)
    df_2016_categorized = df.loc[df["Season"] == 2016].drop(["Season"], axis=1)
    df_2015_categorized = df.loc[df["Season"] == 2015].drop(["Season"], axis=1)

    return df_2017_categorized, df_2016_categorized, df_2015_categorized


def filter_columns(df):
    df = df.filter(items=COLUMNS_TO_INCLUDE)
    return df


def combine_data(left, right, latest):
    combined_df = pd.merge(
        left["df"],
        right["df"],
        on="NHLid",
        how="inner",
        suffixes=(left["suffix"], right["suffix"]),
    )

    df = pd.DataFrame()
    df["NHLid"] = latest["NHLid"]

    for category in models.keys():
        df["latest_" + category] = latest[category]

    df = combined_df.merge(df, how="inner", on=["NHLid"])

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

    df_2017, df_2016, df_2015 = transform_categorical(df_2017, df_2016, df_2015)

    fill = pd.DataFrame()
    fill["NHLid"] = df_2016["NHLid"]
    training_df = combine_data(
        {"df": df_2015, "suffix": "_previous"},
        {"df": df_2016, "suffix": "_next"},
        df_2017,
    )

    # Finally drop NHLid
    training_df = training_df.drop(["NHLid"], axis=1)

    forecast_df = combine_data(
        {"df": df_2016, "suffix": "_previous"},
        {"df": df_2017, "suffix": "_next"},
        df_2017,
    )

    return training_df, forecast_df, df_2017


def evaluate_model(lm, category, X, y_test, y_pred):
    slope_df = pd.DataFrame(
        {
            "column": X.columns,
            "slope": lm.coef_,
        }
    )

    slope = slope_df.loc[slope_df["column"] == category + "_next", "slope"].iloc[0]

    errors = abs(y_pred - y_test)

    print("Category:", category)
    print("Intercept:", lm.intercept_)
    print("Slope:", slope)
    print("Mean Absolute Error:", round(np.mean(errors), 2), "degrees.")
    print("")
    print(slope_df)
    print("")


def train_models(df):
    X = df
    test_data = pd.DataFrame()
    regression_stats = dict()

    for category in models.keys():  # delete test result cols
        test_data["latest_" + category] = X["latest_" + category]
        X = X.drop(["latest_" + category], axis=1)

    for category, lm in models.items():
        y = df["latest_" + category]
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=100)
        lm.fit(X_train, y_train)
        y_pred = lm.predict(X_test)
        # evaluation on model
        evaluate_model(lm, category, X, y_test, y_pred)
        regression_stats[category] = dict({"y_test": y_test, "y_pred": y_pred})

    return regression_stats


def forecast(df):
    predict_df = df.drop(["NHLid"], axis=1)
    for category in models.keys():  # delete test result cols
        predict_df = predict_df.drop(["latest_" + category], axis=1)
    for category in models.keys():
        result_on_category = models[category].predict(predict_df)
        df["forecast_" + category] = result_on_category

    return df


def get_forecast_visual_data(df_full, forecast_df):
    cap_hit_df = pd.DataFrame()
    cap_hit_df["Cap Hit"] = df_full["Cap Hit"]
    cap_hit_df["H-Ref Name"] = df_full["H-Ref Name"]
    cap_hit_df["NHLid"] = df_full["NHLid"]
    cap_hit_df["Position"] = df_full["Position"]

    forecast_results = forecast(forecast_df)
    forecast_results = forecast_results.merge(
        cap_hit_df, left_on="NHLid", right_on="NHLid", how="inner"
    )
    return forecast_results
