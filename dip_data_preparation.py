#features:
#growth since last bottom
#days since last bottom
#1 week growth
#days since last top
#growth volue past month
#growth since last top(meh 7%)

import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd
from aws_keys_retrieval import load_secrets
from data_preparation import get_historical_data
from binance.client import Client
import os
from datetime import datetime, timedelta

if __name__=="__main__":
    asset_name = "SOL-USD"
    #all_data = yf.download(asset_name)
    #short_data = yf.download(asset_name, start='2022-01-01', end='2022-07-01')

    no_light_data = pd.read_csv('trading bot/SOLUSD2024H.csv')
    print(no_light_data)
    no_light_data['date'] = no_light_data['timestamp'].astype('datetime64[s]')
    load_secrets()

    client = Client(os.environ.get("DATA_BINANCE_API_KEY"), os.environ.get("DATA_BINANCE_API_SECRET"))
    account_info = client.get_account()
    symbol = 'SOLUSDT'
    interval = Client.KLINE_INTERVAL_15MINUTE
    start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') 

    data = get_historical_data(client, symbol, interval, start_date)
    print(data)
    asset_df = data

    asset_df_reset = asset_df.reset_index()
    derivatives = np.gradient(asset_df['close'], asset_df_reset.index.values)
    second_order_derivatives = np.gradient(derivatives, asset_df_reset.index.values)
    asset_df['derivatives'], asset_df['second_order_derivatives'] = derivatives, second_order_derivatives
    asset_df['abs derivatives'] = abs(asset_df['derivatives'])

    zero_derivatives_mask = np.isclose(derivatives, 0, atol = 0.25)
    asset_df['close'][zero_derivatives_mask]
    #def growth_since_last_bottom(data):
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot the stock price on the first y-axis
    ax1.plot(asset_df.index, asset_df['close'], color='blue', label='Stock Price')
    ax1.set_xlabel('date')
    ax1.set_ylabel('price')
    ax1.legend(loc='upper left')

    # Create a second y-axis for the derivative
    ax2 = ax1.twinx()

    # Plot the derivative on the second y-axis
    ax2.plot(asset_df.index, derivatives, color='green', label='derivative')
    ax2.plot(asset_df.index, second_order_derivatives, color='purple', label='Second order derivative')
    ax2.set_ylabel('derivative')
    ax2.legend(loc='upper right')

    # Plot vertical lines where the derivative is close to 0
    for idx in asset_df.index[zero_derivatives_mask]:
        ax1.axvline(x=idx, color='red', linestyle='--', linewidth=1)
    print(asset_df.describe())
    print(asset_df.sort_values(['abs derivatives']))

    plt.title(f'{asset_name} Price Derivative')
    plt.legend()
    plt.grid(True)

    plt.show()

