from dotenv import load_dotenv
from binance.client import Client
import os
import pandas as pd
import matplotlib.pyplot as plt
import ta

load_dotenv()

client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

def get_historical_data(symbol, interval, start_date, end_date=None):
    klines=client.get_historical_klines(symbol, interval, start_date, end_date)
    data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    data = data[['timestamp', 'close', 'close_time', 'volume']]

    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data['close_time'] = pd.to_datetime(data['close_time'], unit='ms')

    data.set_index('timestamp', inplace=True)
    for col in ['close', 'volume']:
        data[col] = data[col].astype(float)
    
    return data

if __name__=="__main__":
    try:
        account_info = client.get_account()
        symbol = 'SOLUSDT'
        interval = Client.KLINE_INTERVAL_1HOUR
        start_date = "1 Jul, 2024"

        historical_data = get_historical_data(symbol, interval, start_date)
        print(historical_data.iloc[1])
        historical_data.to_csv('trading bot/SOLUSD2024H.csv')
        print(historical_data)
        # Plot 1: Price vs Date
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Plot price on primary axis
        color = 'tab:blue'
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price', color=color)
        ax1.plot(historical_data.index, historical_data['close'], color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        # Create secondary axis for volume
        ax2 = ax1.twinx()
        color = 'tab:green'
        ax2.set_ylabel('RSI', color=color)
        ax2.plot(historical_data.index, historical_data['volume'], color=color, alpha=0.3)
        ax2.tick_params(axis='y', labelcolor=color)

        # Set title and format x-axis
        plt.title(f'{symbol} Price and Volume History')
        fig.autofmt_xdate()  # Rotation and alignment of tick labels

        # Add grid
        ax1.grid(True, linestyle='--', alpha=0.7)

        # Adjust layout and show plot
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Connection error: {e}")