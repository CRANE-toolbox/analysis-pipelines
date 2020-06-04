# Utility functions that may be used by several scripts

import pandas as pd
from datetime import datetime

def transformDateFormat(df):
    """Add the date of the "timestamp" column of a DataFrame to a "day" column.

    :param DataFrame df: A DataFrame with a "timestamp" column containing pandas datetime objects.
    :return: df with a new column "day" that corresponds to the date version of the "timestamp" column.
    :rtype: DataFrame

    """

    timestamps = df["timestamp"].to_list()
    days = [datetime.date(t) for t in timestamps]
    df["day"] = days
    return df
