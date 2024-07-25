import schedule
import time
from binance.client import Client
import pandas as pd
from datetime import datetime, timedelta, timezone
from aws_keys_retrieval import load_secrets
import os
from signal_definition import *
from data_preparation import get_historical_data
from connection import buy_sol_with_all_usdt, sell_all_sol

current_date = datetime.now()
load_secrets
# Calculate date from a week ago
week_ago = current_date - timedelta(days=7)

# Format the date as a string (optional)
week_ago_formatted = week_ago.strftime('%Y-%m-%d')
print("Hello! Bot initialized!")
client = Client(os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_API_SECRET"))

if client:
    print("Successfully connected to binance\nWaiting for the releveant timestamps")

def analyze_market():
    print("Fetching relevant data")
    df = get_historical_data(client, 'SOLUSDT', Client.KLINE_INTERVAL_1HOUR, week_ago_formatted)
    df = derivative_signal(df)
    df = transform_signals(df)

    print("Data fetched and analyzed!")
    last_close = df['close'].iloc[-1]
    last_signal = df['signal'].iloc[-1]
    last_derivative = df['derivatives'].iloc[-1]
    last_sod = df['second_order_derivatives'].iloc[-1]
    print(df[['close', 'derivatives', 'second_order_derivatives', 'fod_change', 'sod_change']].tail(3))
    print(f"Last price {last_close}\n"
          f"Last signal {last_signal}\n",
          f"Last derivative {last_derivative}\n"
          f"Last second order derivative {last_sod}")
    if last_signal == 1:
        print(f"Buy signal generated at {datetime.now()}")
        transaction = buy_sol_with_all_usdt()
        print(transaction)
    elif last_signal == -1:
        print(f"Sell signal generated at {datetime.now()}")
        transaction = sell_all_sol()
        print(transaction)
    else:
        print(f"No signal generated at {datetime.now()}")

    


symbol = 'SOLUSDT'
interval = Client.KLINE_INTERVAL_15MINUTE

minutes_to_run = ["14", "29", "44", "59"]

for minute in minutes_to_run:
    schedule.every().hour.at(f":{minute}").do(analyze_market)

while True:
    schedule.run_pending()
    time.sleep(1)