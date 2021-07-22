import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
from dash.dependencies import Output, Input, State

from ta_scanner.data.data import aggregate_bars
from ta_scanner.data.csv_file_fetcher import CsvFileFetcher
from ta_scanner.indicators import IndicatorSmaCrossover, IndicatorParams


# load data here so it's loaded once (and not on each callback execution)
data = CsvFileFetcher("../../example.csv")
original_df = data.request_instrument()
dates = []
dates_dfs = {}
for k, v in original_df.groupby(original_df.index.date):
    dates.append(k)
    dates_dfs[k] = v


def gen_df(date: datetime.date):
    return dates_dfs[date]


def first_between_time(df, t1, t2):
    x = df.between_time(t1, t2)
    if len(x.index) > 0:
        values = x.index.to_pydatetime()
        return values[0]


def first_and_close_between_time(df, t1, t2):
    x = df.between_time(t1, t2)
    if len(x.index) > 0:
        values = x.index.to_pydatetime()
        closes = x.close.values
        return (values[0], closes[0])


def us_open(df):
    return first_and_close_between_time(df, "07:30", "07:31")


def us_close(df):
    return first_and_close_between_time(df, "13:59", "14:00")


def european_close(df):
    return first_and_close_between_time(df, "9:30", "9:31")


def add_line(fig, x, ymin: float, ymax: float):
    fig.add_shape(
        dict(
            type="line", x0=x, y0=ymin, x1=x, y1=ymax, line=dict(color="black", width=1)
        )
    )


def gen_or_df(df, number_bars):
    dfs = []

    def gen_copy_df(df):
        return df.between_time("07:30", "2:00").copy()

    rows = df[df.time == " 07:30:00.0"]

    if len(rows.index) == 0:
        return []

    index_value = rows.index[0]
    index_i = df.index.get_loc(index_value)
    rows = df.iloc[index_i : index_i + number_bars]

    high = gen_copy_df(df)
    high["value"] = rows.close.max()
    dfs.append(["OR High", high])

    low = gen_copy_df(df)
    low["value"] = rows.close.min()
    dfs.append(["OR Low", low])

    return dfs


def gen_figure(df, number_bars, fast_ma, mid_ma, slow_ma):
    # fig = go.Figure()
    fig = make_subplots(rows=2, cols=1, row_heights=[0.5, 0.5], vertical_spacing=0)
    fig.add_trace(
        go.Scatter(x=df.index.to_pydatetime(), y=df.close, mode="lines", name="price"),
        row=1,
        col=1,
    )

    or_df = gen_or_df(df, number_bars)
    for name, xddf in or_df:
        fig.add_trace(
            go.Scatter(
                x=xddf.index.to_pydatetime(), y=xddf.value, mode="lines", name=name
            ),
            row=1,
            col=1,
        )

    for f in [us_open, european_close, us_close]:
        x, y = f(df)
        if x:
            diff = 10
            ymin, ymax = y - diff, y + diff
            add_line(fig, x, ymin, ymax)

    windows = [fast_ma, mid_ma, slow_ma]
    window_colors = ["red", "orange", "green"]
    for i, w in enumerate(windows):
        fig.add_trace(
            go.Scatter(
                x=df.index.to_pydatetime(),
                y=df.close.rolling(window=w).mean(),
                mode="lines",
                name=f"{w} SMA",
                line=dict(color=window_colors[i], width=1),
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        {"legend_orientation": "h"},
        legend=dict(y=1, x=0),
        font=dict(color="black"),
        dragmode="pan",
        hovermode="y",
        margin=dict(b=0, t=0, l=40, r=40),
    )

    fig.update_yaxes(
        showgrid=True,
        zeroline=True,
        showticklabels=True,
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        showline=False,
        spikedash="solid",
        spikecolor="grey",
        spikethickness=1,
    )

    fig.update_xaxes(
        showgrid=True,
        zeroline=False,
        rangeslider_visible=False,
        showticklabels=True,
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        showline=True,
        spikedash="solid",
        spikecolor="grey",
        spikethickness=1,
    )

    fig.update_layout(hoverdistance=0)

    fig.update_traces(xaxis="x", hoverinfo="none")

    return fig


inits = dict(date=datetime.date(2020, 9, 10), or_interval=2, smas=[10, 20, 60])
states = dict(date=inits["date"], or_interval=inits["or_interval"], smas=inits["smas"])
df = gen_df(states["date"])
fig = gen_figure(
    df, states["or_interval"], states["smas"][0], states["smas"][1], states["smas"][2]
)

app = dash.Dash(__name__)


app.layout = html.Div(
    [
        html.Div(
            [html.H1("Moving Average Crossover Strategy")],
            style={"textAlign": "center"},
        ),
        # inputs
        html.Div(
            [
                html.Div(
                    ["Fast MA: ", dcc.Input(id="fast-ma", value="10", type="number")]
                ),
                html.Br(),
                html.Div(
                    ["Mid MA: ", dcc.Input(id="mid-ma", value="20", type="number")]
                ),
                html.Br(),
                html.Div(
                    ["Slow MA: ", dcc.Input(id="slow-ma", value="60", type="number")]
                ),
                html.Br(),
                html.Div(
                    [
                        "Establish OR after x 30 second bars: ",
                        dcc.Input(
                            id="or-interval", value=states["or_interval"], type="number"
                        ),
                    ]
                ),
                html.Br(),
                html.Div(
                    [
                        html.Button(" << ", id="increment-down"),
                        dcc.DatePickerSingle(
                            id="date-picker-single",
                            min_date_allowed=dates[0],
                            max_date_allowed=dates[-1],
                            initial_visible_month=dates[-2],
                            date=dates[-2],
                        ),
                        html.Button(" >> ", id="increment-up"),
                    ]
                ),
                html.Br(),
                html.Div(id="params-output"),
            ],
            className="row",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="graph-asset", figure=fig)],
                            className="row",
                            style={"margin": "auto"},
                        ),
                    ],
                    className="six columns",
                    style={"margin-right": 0, "padding": 0},
                )
            ],
            className="row",
        ),
    ],
    className="container",
    id="container",
)


@app.callback(
    Output(component_id="date-picker-single", component_property="date"),
    [
        Input(component_id="increment-down", component_property="n_clicks"),
        Input(component_id="increment-up", component_property="n_clicks"),
    ],
)
def callback_incrementers(increment_up, increment_down):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]

    def adjust_date(adjustment: int):
        date_index = dates.index(states["date"])
        new_date = dates[date_index + adjustment]
        states["date"] = new_date
        return new_date

    if changed_id in ["increment-down.n_clicks", "increment-up.n_clicks"]:

        if changed_id == "increment-down.n_clicks":
            return adjust_date(-1)

        if changed_id == "increment-up.n_clicks":
            return adjust_date(+1)


@app.callback(
    [
        Output(component_id="params-output", component_property="children"),
        Output(component_id="graph-asset", component_property="figure"),
    ],
    [
        Input(component_id="fast-ma", component_property="value"),
        Input(component_id="mid-ma", component_property="value"),
        Input(component_id="slow-ma", component_property="value"),
        Input(component_id="or-interval", component_property="value"),
        Input(component_id="date-picker-single", component_property="date"),
    ],
)
def update_output_div(
    fast_ma, mid_ma, slow_ma, or_interval, date_str,
):
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    df = gen_df(date)
    updated_fig = gen_figure(df, or_interval, int(fast_ma), int(mid_ma), int(slow_ma))
    df_date = date
    week_day_name = df.ts.dt.day_name()[0]

    params_output = f"Date = {df_date} / {week_day_name}"

    return (params_output, updated_fig)


if __name__ == "__main__":
    app.run_server(debug=True)
