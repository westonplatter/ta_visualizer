import datetime
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec

matplotlib.use("agg")


def condense_assset_df(ddf, agg_interval):
    agg_col_definition = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
        # "number_of_trades": "sum",
        # "bid_volume": "sum",
        # "ask_volume": "sum",
    }
    return ddf.resample(agg_interval).agg(agg_col_definition)


def prepare_asset_data(ddf, agg_interval):
    return condense_assset_df(ddf, agg_interval)


def prepare_filled_orders_data(ddf):
    cols = ["order_type", "trade_price", "quantity", "date_time"]
    return ddf[cols].copy()


def get_opening_range(ddf):
    opening_range = ddf.between_time(
        "13:30:00", "13:31:00"
    )  # TODO, make this work with/without DST
    high, low = opening_range.close.max(), opening_range.close.min()
    return (high, low)


def get_opening_range_last_ts(ddf):
    return ddf.between_time("13:30:00", "13:31:00").index.values[-1]


def only_rth_data(ddf):
    return ddf  # .between_time("08:30:00", "20:00:00")


def dot_annotation_for_order(order_row):
    if order_row.quantity > 0:
        # return "go"
        return "bo"
    if order_row.quantity < 0:
        return "ro"


def plot_filled_orders(date, ddf, ddf_filled_orders, observations_ddf):
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

    or_high, or_low = get_opening_range(ddf)

    ax1.plot(only_rth_data(ddf).close)

    # OR high, low, & middle lines
    ax1.axhline(y=or_high, color="r", lw=0.8)
    ax1.axhline(y=or_low, color="r", lw=0.8)
    ax1.axhline(y=((or_high + or_low)) / 2, color="b", lw=0.4)

    ax1.axvline(x=get_opening_range_last_ts(ddf), color="r", lw=0.6)

    if ddf_filled_orders is not None:
        for i, order_row in ddf_filled_orders.iterrows():
            annotation = dot_annotation_for_order(order_row)
            ax1.plot(order_row.name, order_row.trade_price, annotation)

    if observations_ddf is not None:
        for i, observation_row in observations_ddf.iterrows():
            ax1.axvline(x=observation_row.observed_at, color="g", lw=0.6)

    plt.savefig(f"chart_{date}.png")


def generate_plot(
    date: datetime.date,
    raw_asset_price_by_date: pd.DataFrame,
    raw_filled_orders_by_date: pd.DataFrame = None,
    observations_df: pd.DataFrame = None,
):
    interval = "1min"
    asset_prices = prepare_asset_data(raw_asset_price_by_date, interval)
    filled_orders = prepare_filled_orders_data(raw_filled_orders_by_date)
    plot_filled_orders(date, asset_prices, raw_filled_orders_by_date, observations_df)
