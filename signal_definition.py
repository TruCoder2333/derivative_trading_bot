import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from aws_keys_retrieval import load_secrets
from binance.client import Client
import os
from data_preparation import get_historical_data
from datetime import timedelta, datetime

def transform_signals(df):
    # Create a boolean mask for non-zero values
    mask = df['signal'] != 0
    
    # Forward fill the non-zero values
    df['transformed_signal'] = df['signal'].where(mask).ffill()
    
    # Fill any remaining NaNs at the beginning with 0
    df['transformed_signal'] = df['transformed_signal'].fillna(0)
    
    return df

def sign_change(data):
    # Create a Series of zeros with the same index as data
    result = pd.Series(0, index=data.index)
    
    # Positive to negative change
    result[(data.shift(1) > 0) & (data < 0)] = -1
    
    # Negative to positive change
    result[(data.shift(1) < 0) & (data > 0)] = 1
    
    return result

def derivative_signal(data):
    derivatives = np.gradient(data['close'], data.reset_index().index.values)
    second_order_derivatives = np.gradient(derivatives, data.reset_index().index.values)
    data['derivatives'], data['second_order_derivatives'] = derivatives, second_order_derivatives
    data['abs derivatives'] = abs(data['derivatives'])
    data = data.dropna()
    data['fod_zero'] = np.isclose(data['derivatives'], 0, atol=0.15)
    data['sod_zero'] = np.isclose(data['second_order_derivatives'], 0, atol=0.13)
    data['fod_change'] = sign_change(data['derivatives'])
    data['sod_change'] = sign_change(data['second_order_derivatives'])
    
    # Rule 1: sod changes from negative to positive and fod > 0
    condition1 = (data['sod_change'] == 1) & (data['derivatives'] > 0)
    
    # Rule 2: sod changes from positive to negative and fod <= 0
    condition2 = (data['second_order_derivatives'] < 0) & ((data['fod_change'] != 0) | data['fod_zero'])
    # Rule 3: sod > 0 and fod close to 0
    condition3 = (data['second_order_derivatives'] > 0) & ((data['fod_change'] != 0) | data['fod_zero'])
    data['signal'] = np.where(condition1 | condition3, 1,
                            np.where(condition2, -1, 0))
    return data

def plot_signals(data):
    plt.figure(figsize=(12,6))
    plt.plot(data.index, data['close'], label='Close Price')
    
    # Plot buy signals
    plt.scatter(data.index[data['signal'] == 1], 
                data['close'][data['signal'] == 1],
                marker='^', color='g', s=100, label='Buy Signal')
    
    # Plot sell signals (assuming -1 for sell, adjust if different)
    plt.scatter(data.index[data['signal'] == -1], 
                data['close'][data['signal'] == -1],
                marker='v', color='r', s=100, label='Sell Signal')

    plt.title('Price with Buy/Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

if __name__=="__main__":
    load_secrets()

    client = Client(os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_API_SECRET"))
    account_info = client.get_account()
    symbol = 'SOLUSDT'
    interval = Client.KLINE_INTERVAL_1HOUR
    start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d') 

    data = get_historical_data(symbol, interval, start_date)
    print(data)
    #no_light_data = pd.read_csv('trading bot/SOLUSD2024H.csv')
    #no_light_data['date'] = no_light_data['timestamp'].astype('datetime64[s]')
    #data = no_light_data.set_index('date')
    #data = data[data.index < '2024-01-17']
    data = data['2024-07-21' < data.index]
    results = derivative_signal(data)


    print(results)


    # Assuming 'result' is your dataframe from the previous code
    plot_signals(results)