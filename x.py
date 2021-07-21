import pandas as pd
from typing import List
from decimal import Decimal


filename = "data/CL-202109-NYMEX-lsc-exp-cl-002.txt"
df = pd.read_csv(filename, delimiter=",")

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


df.columns = normalize_columns(df.columns)

buy_signals = df.query("buy_entry != 0.0")
sell_signals = df.query("sell_entry != 0.0")


for index, row in buy_signals.iterrows():
    price = Decimal(str(row.buy_entry))
    # slipage = Decimal("0.02") # for the /MCL contract
    # price_adjusted_commission = Decimal("0.74")/Decimal("100.0") # the /MCL contract
    # execution_price = price + slipage + price_adjusted_commission

    diffs: List[Decimal] = []
    for xindex in range(0, 21):
        row = df.iloc[index + xindex]
        diff = price - Decimal(str(row[LAST]))
        diffs.append(diff)

    import pdb

    pdb.set_trace()
