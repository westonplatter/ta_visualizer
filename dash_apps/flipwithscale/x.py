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
    result_df = pd.DataFrame(columns=["bars_after", "diff"])

    for index, row in signals.iterrows():
        price = row[col]
        # slipage = Decimal("0.02") # for the /MCL contract
        # price_adjusted_commission = Decimal("0.74")/Decimal("100.0") # the /MCL contract
        # execution_price = price + slipage + price_adjusted_commission

        for rindex in range(0, 21):
            row = df.iloc[index + rindex]
            diff = price - row[LAST]
            result_df.loc[len(result_df)] = [rindex, diff]

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
    ax.xaxis.grid(True)
    ax.set(ylabel="")
    sns.despine(trim=True, left=True)

    ax.axhline(0, ls="--")

    f.savefig(f"{name}.png")


def run():
    filename = "data/CL-202109-NYMEX-lsc-exp-cl-002.txt"
    df = pd.read_csv(filename, delimiter=",")
    df.columns = normalize_columns(df.columns)

    folder = "dashapps/flipwithscale"

    buy_signals = df.query("buy_entry != 0.0")
    results_df = gen_results(df, buy_signals, "buy_entry")
    gen_and_save_figure(results_df, f"{folder}/buy")

    # sell_signals = df.query("sell_entry != 0.0")
    # results_df = gen_results(sell_signals, "sell_entry")
    # gen_and_save_figure(results_df, "flipwithscale_sell")


if __name__ == "__main__":
    run()
