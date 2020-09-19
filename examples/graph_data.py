import datetime
from loguru import logger
import sys
import pandas as pd

from ta_scanner.data.data import db_data_fetch_between, aggregate_bars
from ta_scanner.models import gen_engine
from ta_visualizer import graph_results


symbol = "/MES"
symbol_technical = "MES"
sd = datetime.date(2020, 9, 18)
ed = sd

engine = gen_engine()
groupby_minutes = 1


def query_data(engine, symbol, sd, ed, groupby_minutes):
    df = db_data_fetch_between(engine, symbol, sd, ed)
    df.set_index("ts", inplace=True)
    df = aggregate_bars(df, groupby_minutes=groupby_minutes)
    df["ts"] = df.index
    df.sort_index(ascending=True, inplace=True)
    return df


df = query_data(engine, symbol, sd, ed, groupby_minutes)


def prepare_trade_df(ddf) -> pd.DataFrame:
    # TODO(weston) move data layer mapping back to lsc repo
    rename_columns = {
        "symbol": "symbol",
        "accountId": "account_id",
        "underlyingSymbol": "underlying_symbol",
        "tradeDate": "trade_date",
        "tradePrice": "trade_price",
        "dateTime": "date_time",
        "tradeMoney": "trade_money",
        "orderType": "order_type",
    }
    ddf = ddf.rename(columns=rename_columns)
    ddf.trade_date = pd.to_datetime(ddf.trade_date)
    ddf.date_time = pd.to_datetime(ddf.date_time)
    ddf.set_index("date_time", drop=False, inplace=True)
    ddf = ddf.tz_localize('US/Eastern')
    ddf = ddf.tz_convert("UTC")
    ddf = ddf.sort_index()
    return ddf


def trade_df_only_date(ddf, date) -> pd.DataFrame:
    return ddf.query("trade_date == @date").copy()


def trade_df_only_underlying_symbol(ddf, symbol):
    return ddf.query("underlying_symbol == @symbol").copy()


trades_df = pd.read_csv("trades.csv")
trades_df = prepare_trade_df(trades_df)
trades_df = trade_df_only_underlying_symbol(trades_df, symbol_technical)
trades_df = trade_df_only_date(trades_df, sd)

graph_results.generate_plot(sd, df, trades_df)
