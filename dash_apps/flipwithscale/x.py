import pandas as pd
from typing import List
from decimal import Decimal

from datetime import date

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


# constants
SPACE = " "
UNDERSCORE = "_"
LAST = "last"


def normalize_columns(cols: List[str]) -> List[str]:
    """Clean up the columns we get from Sierra Chart
    """
    result = []

    def normalize(col: str) -> str:
        if col[0] == SPACE:
            col = col[1:]
        col = col.replace(SPACE, UNDERSCORE)
        col = col.lower()
        return col

    for col in cols:
        result.append(normalize(col))

    return result


def gen_results(df: pd.DataFrame, signals: pd.DataFrame, col: str) -> pd.DataFrame:
    """[summary]

    Args:
        df (pd.DataFrame): raw data DF
        signals (pd.DataFrame): signals data DF
        col (str): col to get the price data from

    Returns:
        pd.DataFrame: [description]
    """
    # create new df to hold results
    result_df = pd.DataFrame(columns=["bars_after", "diff"])

    # index in signals is the same as index in df
    for index, row in signals.iterrows():
        price = row[col]

        # TODO(weston) calculate theoretical execution prices
        slipage_pts = 0.01  # 0.02 # for the /MCL contract
        commission_pts = 0.01 * 2 * (0.74 / 1.0)  # the /MCL contract
        execution_price = price + slipage_pts + commission_pts

        for rindex in range(0, 21):
            row = df.iloc[index + rindex]
            diff = row[LAST] - price
            result_df.loc[len(result_df)] = [rindex, diff]
            # TODO(weston) add additional columns for corrlation analysis

    return result_df


def gen_and_save_figure(results_df: pd.DataFrame, name: str) -> None:

    f, ax = plt.subplots(figsize=(7, 6))

    # Plot the orbital period with horizontal boxes
    sns.boxplot(
        x="bars_after",
        y="diff",
        data=results_df,
        whis=[0, 100],
        width=0.6,
        palette="vlag",
    )

    # Add in points to show each observation
    sns.stripplot(
        x="bars_after", y="diff", data=results_df, size=2, color=".3", linewidth=0
    )

    # Tweak the visual presentation

    # chart title
    ax.set_title(name)

    # x axis
    ax.xaxis.grid(True)
    plt.xticks(rotation=-90)
    # add zero line
    ax.axhline(0, ls="--")

    # y axis
    ax.set(ylabel="Contract Points")
    sns.despine(trim=True, left=True)

    f.savefig(f"{name}.png")


def run():
    filename = "data/CL-202109-lsc-exp-002.txt"
    df = pd.read_csv(filename, delimiter=",")
    df.columns = normalize_columns(df.columns)

    folder = "dash_apps/flipwithscale"

    buy_signals = df.query("buy_entry != 0.0")
    results_df = gen_results(df, buy_signals, "buy_entry")
    gen_and_save_figure(results_df, f"{folder}/buy")

    sell_signals = df.query("sell_entry != 0.0")
    results_df = gen_results(df, sell_signals, "sell_entry")
    gen_and_save_figure(results_df, f"{folder}/sell")


if __name__ == "__main__":
    run()
