import schedule
import time
from binance.client import Client
import pandas as pd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from signal_definition import *
from data_preparation import get_historical_data
from connection import buy_sol_with_all_usdt, sell_all_sol

current_date = datetime.now()

# Calculate date from a week ago
week_ago = current_date - timedelta(days=7)

# Format the date as a string (optional)
week_ago_formatted = week_ago.strftime('%Y-%m-%d')
client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

def analyze_market():
    df = get_historical_data('SOLUSDT', Client.KLINE_INTERVAL_1HOUR, week_ago_formatted)
    df = derivative_signal(df)
    df = transform_signals(df)
    print(df)
    last_signal = df['signal'].iloc[-1]

    print(last_signal)
    if last_signal == 1:
        print(f"Buy signal generated at {datetime.now()} ({datetime.fromtimestamp(datetime.now, tz=timezone.utc)} UTC)")
        transaction = buy_sol_with_all_usdt()
        print(transaction)
    elif last_signal == -1:
        print(f"Sell signal generated at {datetime.now()}")
        transaction = sell_all_sol()
        print(transaction)
    else:
        print(f"No signal generated at {datetime.now()}")

    


symbol = 'SOLUSDT'
interval = Client.KLINE_INTERVAL_1HOUR

minutes_to_run = ["00", "30"]

for minute in minutes_to_run:
    schedule.every().hour.at(f":{minute}").do(analyze_market)

while True:
    schedule.run_pending()
    time.sleep(1)