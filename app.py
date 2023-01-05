# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 17:33:14 2020

@author: Elvis
"""

import pandas as pd
import numpy as np


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State

import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re


# import data

df = pd.read_excel(
    "./data/Superstore.xls",
    sheet_name="Orders",
    parse_dates=["Order Date", "Ship Date"],
    dtype={"Row ID": "object", "Postal Code": "object"},
)

# compute shipping days
df["Ship Days"] = df["Ship Date"] - df["Order Date"]

# compute minimum date
min_date = df["Order Date"].min()
max_date = df["Order Date"].max()


# create app
app = dash.Dash(__name__, title="SuperStore Dashboard")


# app layout - header
header = html.Div(
    className="header",
    children=[
        html.Div(className="header__title", children=[html.H1("SuperStore Dashboard")]),
        html.Div(
            className="header__logo",
            children=[html.Img(src="assets/logo.svg", id="header__logo__img")],
        ),
    ],
)

# app layout - filter
filters = html.Div(
    className="filter",
    children=[
        html.Div(
            className="filter__daterange",
            children=[
                html.Div(
                    className="filter__daterange__start",
                    children=[
                        html.P("Start Date"),
                        dcc.DatePickerSingle(
                            id="filter__daterange_Dstart_id",
                            className="filter__daterange__Dstart",
                            min_date_allowed=min_date,
                            max_date_allowed=datetime.today(),
                            date=datetime.strptime("2017/07/01", "%Y/%m/%d"),
                        ),
                    ],
                ),
                html.Div(
                    className="filter__daterange__end",
                    children=[
                        html.P("End Date"),
                        dcc.DatePickerSingle(
                            id="filter__daterange_Dend_id",
                            className="filter__daterange__Dend",
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            date=max_date,
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="filter__compare",
            children=[
                html.P("Compare to"),
                dcc.Dropdown(
                    id="filter__compare__to_id",
                    className="filter__compare__to",
                    options=[
                        {"label": "Prior Year", "value": "prioryear"},
                        {"label": "Prior Period", "value": "priorperiod"},
                    ],
                    value="prioryear",
                    searchable=False,
                    clearable=False,
                    style={"height": "48px"},
                ),
            ],
        ),
        html.Div(
            className="filter__submit",
            children=[
                html.P("Submit", className="filter__submit__label"),
                html.Button(
                    "Submit",
                    id="filter__submit__id",
                    className="filter__submit__button",
                    n_clicks=0,
                ),
            ],
        ),
    ],
)

# app label - bans
label_bans = html.Div(className="label__1", children=[html.P("KPIs")])


# app layout - Bans
bans = html.Div(
    className="bans",
    children=[
        html.Div(
            className="bans__sales",
            children=[
                html.H2(
                    id="bans__sales__amount_id",
                    className="bans__sales__amount",
                    children=["$235.3b"],
                ),
                html.H3(
                    className="bans__sales__indicator",
                    children=[
                        html.Span(id="bans__sales__indicator_id"),
                        html.Span(
                            id="bans__sales__change_id",
                            className="bans__sales__change",
                            children=["2%"],
                        ),
                    ],
                ),
                html.P(className="bans__sales_label", children=["sales"]),
                # the config variable disables plotly's toolbar display in rendered plot
                dcc.Graph(id="bans__sales__trend_id", config={"displayModeBar": False}),
            ],
        ),
        html.Div(
            className="bans__profit",
            children=[
                html.H2(
                    id="bans__profit__amount_id",
                    className="bans__profit__amount",
                    children=["$101b"],
                ),
                html.H3(
                    className="bans__profit__indicator",
                    children=[
                        html.Span(id="bans__profit__indicator_id"),
                        html.Span(
                            id="bans__profit__change_id",
                            className="bans__profit__change",
                            children=[str("12%")],
                        ),
                    ],
                ),
                html.P(className="bans__profit_label", children=["profit"]),
                dcc.Graph(
                    id="bans__profit__trend_id", config={"displayModeBar": False}
                ),
            ],
        ),
        html.Div(
            className="bans__shipping",
            children=[
                html.H2(
                    id="bans__shipping__amount_id",
                    className="bans__shipping__amount",
                    children=["3.5 days"],
                ),
                html.H3(
                    className="bans__shipping__indicator",
                    children=[
                        html.Span(id="bans__shipping__indicator_id"),
                        html.Span(
                            id="bans__shipping__change_id",
                            className="bans__shipping__change",
                            children=["15%"],
                        ),
                    ],
                ),
                html.P(
                    className="bans__shipping__label", children=["avg. shipping days"]
                ),
                dcc.Graph(
                    id="bans__shipping__trend_id", config={"displayModeBar": False}
                ),
            ],
        ),
    ],
)


# app label - content
label_content = html.Div(className="label__2", children=[html.P("Sales Trend")])

# app content
content = html.Div(
    className="content",
    id="content_id",
    children=[dcc.Graph(id="content__shipping__trend_id")],
)

# app footer
footer = html.Div(
    className="footer",
    children=[
        html.P(["Author: Elvis Agbeshi (@graphshade)"], style={"textAlign": "left"})
    ],
)

# app layout
app.layout = html.Div(
    className="container",
    children=[header, filters, label_bans, bans, label_content, content, footer],
)

# call back to update the metric bans for a user selected filter
@app.callback(
    [
        Output("bans__sales__amount_id", "children"),
        Output("bans__profit__amount_id", "children"),
        Output("bans__shipping__amount_id", "children"),
        Output("bans__sales__indicator_id", "children"),
        Output("bans__profit__indicator_id", "children"),
        Output("bans__shipping__indicator_id", "children"),
        Output("bans__sales__change_id", "children"),
        Output("bans__profit__change_id", "children"),
        Output("bans__shipping__change_id", "children"),
    ],
    [Input("filter__submit__id", "n_clicks")],
    [
        State("filter__daterange_Dstart_id", "date"),
        State("filter__daterange_Dend_id", "date"),
        State("filter__compare__to_id", "value"),
    ],
)
def update_metrics(n_clicks, start_date, end_date, comparison):
    # collect filter parameters
    s_date = datetime.strptime(re.split("T| ", start_date)[0], "%Y-%m-%d")
    e_date = datetime.strptime(re.split("T| ", end_date)[0], "%Y-%m-%d")
    comparison = comparison

    # filter dataframe for selected period
    df_cc = df[(df["Order Date"] >= s_date) & (df["Order Date"] <= e_date)]

    # compute a conditional date range(end_date minus start_date)
    # the date range is used to filter the data to select the base period for period-on-period comparison
    # if the type of comparison is prior year, then the date range is 365 days before and up to the start date
    # if the type of comparison is  prior period, then date range is (end_date - start_date) + 1 days before the start date
    # + 1 is added to always include the start_date when you do (end_date - start_date)
    if comparison == "prioryear":
        daterange = pd.Timedelta(365, unit="days")
    elif comparison == "priorperiod":
        daterange = (e_date - s_date) + pd.Timedelta(1, "days")

    # filter the dataframe for the prior period data. i.e the base YoY comparison
    # When the start date of the prior period computed (start_date - daterange) is
    # less than the minimum date in the data, then the prior period data is out of range
    if (s_date - daterange) >= df["Order Date"].min():
        df_pp = df[
            (df["Order Date"] >= (s_date - daterange))
            & (df["Order Date"] <= (e_date - daterange))
        ]
    else:
        df_pp = None  # return No dataframe because the prior period is out of range

    # selected period metrics
    sales_cc = df_cc["Sales"].sum()
    profit_cc = df_cc["Profit"].sum()
    shipping_cc = df_cc["Ship Days"].dt.days.mean()

    # prior period metrics
    # this function takes the prior period data & attribute and returns the aggregate of the metric
    def get_metric_pp_amt(df, metric):
        if isinstance(df, pd.DataFrame):
            metric_pp = df[metric].sum()
        else:
            metric_pp = None
        return metric_pp

    def get_metric_pp_day(df, metric):
        if isinstance(df, pd.DataFrame):
            metric_pp = df[metric].dt.days.mean()
        else:
            metric_pp = None
        return metric_pp

    sales_pp = get_metric_pp_amt(df_pp, "Sales")
    profit_pp = get_metric_pp_amt(df_pp, "Profit")
    shipping_pp = get_metric_pp_day(df_pp, "Ship Days")

    # format metrics function
    # these functions format the metrics for screen rendering
    def format_metrics_amt(metric):
        if metric >= 100000:
            return str("${:,.2f}m".format(metric / 1000000))
        else:
            return str("${:,.2f}k".format(metric / 1000))

    def format_metrics_time(metric):
        return str("{:.2f}".format(metric))

    def format_metric_pct(metric):
        return str("{:.2f}%".format(metric))

    # format period-on-period indicator label
    def format_indicator_label(metric_pct):
        if metric_pct > 0:
            return str("▲")
        elif metric_pct < 0:
            return str("▼")

    # formated selected period metrics
    sales_cc_f = format_metrics_amt(sales_cc)
    profit_cc_f = format_metrics_amt(profit_cc)
    shipping_cc_f = format_metrics_time(shipping_cc)

    # period-on-period comparison (percent change)
    try:
        sales_pct = ((sales_cc / sales_pp) - 1) * 100
    except TypeError:
        sales_pct = 0

    try:
        profit_pct = ((profit_cc / profit_pp) - 1) * 100
    except TypeError:
        profit_pct = 0

    try:
        shipping_pct = ((shipping_cc / shipping_pp) - 1) * 100
    except TypeError:
        shipping_pct = 0

    # formated period-on-period changes
    sales_pct_f = format_metric_pct(sales_pct)
    profit_pct_f = format_metric_pct(profit_pct)
    shipping_pct_f = format_metric_pct(shipping_pct)

    # period-on-period indicator labels
    sales_pct_label = format_indicator_label(sales_pct)
    profit_pct_label = format_indicator_label(profit_pct)
    shipping_pct_label = format_indicator_label(shipping_pct)

    return (
        sales_cc_f,
        profit_cc_f,
        shipping_cc_f,
        sales_pct_label,
        profit_pct_label,
        shipping_pct_label,
        sales_pct_f,
        profit_pct_f,
        shipping_pct_f,
    )


# callback function to render the last n-days(10days) trend in a selected metric (sales, profit,shiping)
@app.callback(
    [
        Output("bans__sales__trend_id", "figure"),
        Output("bans__profit__trend_id", "figure"),
        Output("bans__shipping__trend_id", "figure"),
    ],
    [Input("filter__submit__id", "n_clicks")],
    [State("filter__daterange_Dend_id", "date")],
)
def update_sparkline(n_clicks, e_date):
    e_date = datetime.strptime(re.split("T| ", e_date)[0], "%Y-%m-%d")

    # reset dataframe index to pd.DateTime index to enable easy t-series manipulation
    dfs = df.set_index("Order Date")

    # return the integer days for the 'Ship Days' attribute for the y_axis plot
    dfs["Ship Days"] = dfs["Ship Days"].dt.days

    # the function takes the dataframe, the attribute, the last n-days, and the end date to plot
    # and returns a plotly express figure (sparkline)
    def sparkline(df, metric, period, e_date):
        dfs = df.resample("D").sum().sort_index(ascending=True)
        s_date = e_date - pd.Timedelta(period, "days")
        dfs = dfs[(dfs.index >= s_date) & (dfs.index <= e_date)]
        fig = px.line(dfs, x=dfs.index, y=metric, height=30, width=30)

        return (
            fig.update_xaxes(visible=False, fixedrange=True)
            .update_yaxes(visible=False, fixedrange=True)
            .update_layout(
                hovermode=False,
                annotations=[],
                overwrite=True,
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=2, t=2, b=2, r=2),
            )
        )

    # generate figure plots for the metrics use the sparkline function
    sales_fig = sparkline(dfs, "Sales", 10, e_date)
    profit_fig = sparkline(dfs, "Profit", 10, e_date)
    shipping_fig = sparkline(dfs, "Ship Days", 10, e_date)

    return sales_fig, profit_fig, shipping_fig


# callback function to render the trends for(sales, profit,shiping)
@app.callback(
    Output("content__shipping__trend_id", "figure"),
    Input("filter__submit__id", "n_clicks"),
    [
        State("filter__daterange_Dstart_id", "date"),
        State("filter__daterange_Dend_id", "date"),
    ],
)
def update_detail_trend(n_clicks, s_date, e_date):
    # collect filter parameters
    s_date = datetime.strptime(re.split("T| ", s_date)[0], "%Y-%m-%d")
    e_date = datetime.strptime(re.split("T| ", e_date)[0], "%Y-%m-%d")

    # filter dataframe for selected period
    dfs = df[(df["Order Date"] >= s_date) & (df["Order Date"] <= e_date)]
    dfs.set_index("Order Date", inplace=True)
    dfs = dfs[["Sales", "Profit"]].resample("D").sum().sort_index(ascending=True)

    # reset dataframe index to pd.DateTime index to enable easy t-series manipulation

    fig = px.line(dfs, x=dfs.index, y="Sales")

    return fig


# run app when app.py is runned
if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_hot_reload=True)
