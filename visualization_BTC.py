import os
import numpy as np
import pandas as pd
import pickle
import quandl
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
quandl.ApiConfig.api_key = "JmoMXXYhf2-GW78XYnMh" # API key for Quandl datasets


def get_quandl_data(quandl_id):

    """A helper function is a function that performs part of the computation of another function.
Helper functions are used to make your programs easier to read by giving descriptive names to computations.
 They also let you reuse computations, just as with functions in general.
 """
    cache_path = '{}.pkl'.format(quandl_id).replace('/','-')
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df

# Pull Kraken BTC price exchange data
btc_usd_price_kraken = get_quandl_data('BCHARTS/KRAKENUSD')

# Chart the BTC pricing data
btc_trace = go.Scattergl(x=btc_usd_price_kraken.index, y=btc_usd_price_kraken['Weighted Price'])
#py.plot([btc_trace])

# Pull pricing data for 3 more BTC exchanges
exchanges = ['COINBASE','HITBTC','BITFINEX']

exchange_data = {}

exchange_data['KRAKEN'] = btc_usd_price_kraken

for exchange in exchanges:
    exchange_code = 'BCHARTS/{}USD'.format(exchange) # All Bitcoin codes follow the same format: "/BCHARTS/BITSTAMPUSD"

    btc_exchange_df = get_quandl_data(exchange_code)
    exchange_data[exchange] = btc_exchange_df


def merge_dfs_on_column(dataframes, labels, col):
    '''Merge a single column of each dataframe into a new combined dataframe'''
    series_dict = {}
    for index in range(len(dataframes)):
        series_dict[labels[index]] = dataframes[index][col]

    return pd.DataFrame(series_dict)
btc_usd_datasets = merge_dfs_on_column(list(exchange_data.values()), list(exchange_data.keys()), 'Weighted Price')
print (btc_usd_datasets.tail())


def df_scatter(df, title, seperate_y_axis=False, y_axis_label='', scale='linear', initial_hide=False):
    '''Generate a scatter plot of the entire dataframe'''
    label_arr = list(df)
    series_arr = list(map(lambda col: df[col], label_arr))

    layout = go.Layout(
        title=title,
        legend=dict(orientation="h"),
        xaxis=dict(type='date'),
        yaxis=dict(
            title=y_axis_label,
            showticklabels=not seperate_y_axis,
            type=scale
        )
    )

    y_axis_config = dict(
        overlaying='y',
        showticklabels=False,
        type=scale)

    visibility = 'visible'
    if initial_hide:
        visibility = 'legendonly'

    # Form Trace For Each Series
    trace_arr = []
    for index, series in enumerate(series_arr):
        trace = go.Scatter(
            x=series.index,
            y=series,
            name=label_arr[index],
            visible='legendonly'
        )

        # Add seperate axis for the series
        if seperate_y_axis:
            trace['yaxis'] = 'y{}'.format(index + 1)
            layout['yaxis{}'.format(index + 1)] = y_axis_config
        trace_arr.append(trace)

    fig = go.Figure(data=trace_arr, layout=layout)
    py.plot(fig)

df_scatter(btc_usd_datasets, 'Bitcoin Price (USD) By Exchange')
print('check')
