import datetime

from ta_scanner.data.data import aggregate_bars
from ta_scanner.data.csv_file_fetcher import CsvFileFetcher
from ta_scanner.indicators import IndicatorSmaCrossover, IndicatorParams

from ta_visualizer.graph_opening_range import generate_plot

data = CsvFileFetcher("example.csv")
df = data.request_instrument()


field_name = "moving_avg_cross"
indicator_params = {
    IndicatorParams.fast_sma: 5,
    IndicatorParams.slow_sma: 60,
}
indicator_sma_cross = IndicatorSmaCrossover(
    field_name=field_name, params=indicator_params
)
indicator_sma_cross.apply(df)


min_datetime = datetime.date(2020, 6, 20)
max_datetime = datetime.date(2020, 6, 26)
additional_columns = ["fast_sma"]



for k, v in df.groupby("date"):
    dayofweek = v.index.dayofweek.values[0]

    # Monday - Friday
    if dayofweek in [0, 1, 2, 3, 4]:

        date = v.index.date[0]

        if date > min_datetime and date < max_datetime:
            print(f"{k} = {dayofweek}")
            generate_plot(date, v, additional_columns)
