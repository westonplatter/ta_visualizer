import datetime
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
from typing import List


matplotlib.use("agg")


def condense_assset_df(ddf, agg_interval):
    agg_col_definition = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        # "number_of_trades": "sum",
        "bid_volume": "sum",
        "ask_volume": "sum",
    }
    return ddf.resample(agg_interval).agg(agg_col_definition)


def prepare_asset_data(ddf, agg_interval):
    return condense_assset_df(ddf, agg_interval)


# def prepare_filled_orders_data(ddf):
#     cols = ["order_type", "trade_price", "quantity", "date_time"]
#     return ddf[cols].copy()


def get_opening_range(ddf):
    opening_range = ddf.between_time("07:30:00", "07:30:30")
    high, low = opening_range.close.max(), opening_range.close.min()
    return (high, low)


def get_opening_range_last_ts(ddf):
    return ddf.between_time("07:30:00", "07:30:30").index.values[-1]


def only_rth_data(ddf):
    return ddf.between_time("06:30:00", "15:00:00")


def dot_annotation_for_order(order_row):
    if order_row.quantity > 0:
        # return "go"
        return "bo"
    if order_row.quantity < 0:
        return "ro"


def plot_filled_orders(
    date, ddf, additional_columns: List[str], additional_or_relative_levels: List[float]
):
    # plt.figure(figsize=(15, 8))
    # plt.grid(True)
    fig = plt.figure(figsize=(20, 15))
    # gs = gridspec.GridSpec(2, 1, height_ratios=[5, 2])
    gs = gridspec.GridSpec(1, 1, height_ratios=[1])
    ax1 = plt.subplot(gs[0])
    # ax2 = plt.subplot(gs[1]) # TODO add MACD(26, 12, 9) on 30 second data

    ax1.grid(True)
    # ax2.grid(True)

    title = f"date = {date}"
    plt.title(title)

    ax1.plot(only_rth_data(ddf).close)
    for ac in additional_columns:
        ax1.plot(only_rth_data(ddf)[ac])

    # OR high, low, & middle lines
    or_high, or_low = get_opening_range(ddf)
    ax1.axhline(y=or_high, color="r", lw=0.8)
    ax1.axhline(y=or_low, color="r", lw=0.8)
    ax1.axhline(y=((or_high + or_low)) / 2, color="b", lw=0.4)
    ax1.axvline(x=get_opening_range_last_ts(ddf), color="r", lw=0.6)

    for level in additional_or_relative_levels:
        if level > 0:
            y = or_high + level
            ax1.axhline(y=y, color="r", lw=0.6)
        if level < 0:
            y = or_low + level
            ax1.axhline(y=y, color="r", lw=0.6)

    plt.savefig(f"chart_{date}.png")


def generate_plot(
    date: datetime.date,
    raw_asset_price_by_date: pd.DataFrame,
    additional_columns: List[str] = [],
    additional_or_relative_levels: List[float] = [],
):
    asset_prices = raw_asset_price_by_date
    plot_filled_orders(
        date, asset_prices, additional_columns, additional_or_relative_levels
    )
